from django.http import HttpResponse
from django.shortcuts import redirect
import os
from urllib.parse import urlencode
import hashlib
import hmac
import requests
import base64
from django.conf import settings
from .models import Shop, Rule
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .shopify_utils import create_delivery_customization, save_shipping_config, get_shipping_methods, create_payment_customization, save_payment_config, generate_id, delete_delivery_customization, delete_payment_customization, deactivate_delivery_customization, deactivate_payment_customization


#https://checkout-rules.onrender.com/shopify/install/?shop=teststoreone-3413.myshopify.com
#https://gonadial-ninfa-nonanimated.ngrok-free.dev/shopify/install/?shop=teststoreone-3413.myshopify.com
#http://127.0.0.1:8000/shopify/install/?shop=smart-shipping-test-2.myshopify.com
#http://127.0.0.1:8000/shopify/install/?shop=test-store-292292.myshopify.com

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")

def install(request):
    shop = request.GET.get("shop")

    if not shop:
        return HttpResponse("Missing shop parameter", status=400)

    params = {
        "client_id": SHOPIFY_API_KEY,
        "scope": "write_delivery_customizations,write_payment_customizations,read_checkouts,write_checkouts",
        "redirect_uri": "https://checkout-rules.onrender.com/shopify/callback/",
    }

    auth_url = f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"
    return redirect(auth_url)


def callback(request):
    params = request.GET.dict()
    hmac_received = params.pop("hmac", None)
    shop = params.get("shop")
    store_name = shop.replace(".myshopify.com", "")

    # 1. Verify HMAC
    message = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(digest, hmac_received):
        return HttpResponse("HMAC validation failed", status=400)

    shop = params.get("shop")
    code = params.get("code")

    # 2. Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": os.getenv("SHOPIFY_API_KEY"),
        "client_secret": SHOPIFY_API_SECRET,
        "code": code,
    }

    resp = requests.post(token_url, json=payload)
    data = resp.json()
    access_token = data.get("access_token")

    # 3. Save shop
    Shop.objects.update_or_create(
        shop_domain=shop,
        defaults={"access_token": access_token, "is_active": True},
    )

    # 🔥 4. REGISTER WEBHOOK HERE
    webhook_url = "https://checkout-rules.onrender.com/shopify/webhooks/app-uninstalled/"

    webhook_data = {
        "webhook": {
            "topic": "app/uninstalled",
            "address": webhook_url,
            "format": "json"
        }
    }

    webhook_response = requests.post(
        f"https://{shop}/admin/api/2024-01/webhooks.json",
        json=webhook_data,
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }
    )

    print("WEBHOOK RESPONSE:", webhook_response.json())

    host = request.GET.get("host")

    return redirect(f"https://admin.shopify.com/store/{store_name}/apps/oeme-checkout-rules")


def app_home(request):
    shop_domain = request.GET.get("shop")
    host = request.GET.get("host")

    shop = Shop.objects.filter(shop_domain=shop_domain).first()
    
    if not shop or shop.is_active == False:
        return redirect(f"/shopify/install/?shop={shop_domain}")
    
    rules = Rule.objects.filter(shop=shop) if shop else []

    upgrade = False
    rule_count = rules.count()

    if shop.plan == "Free" and rules.count() >= 1:
        upgrade = True

    response = render(request, "app_home.html", {
        "shop": shop,
        "rules": rules,
        "host": host,
        "upgrade":upgrade,
        "rule_count":rule_count,
    })

    response["Content-Security-Policy"] = "frame-ancestors https://admin.shopify.com https://*.myshopify.com;"

    return response


def create_rule(request):
    shop_domain = request.GET.get("shop")
    shop = Shop.objects.filter(shop_domain=shop_domain).first()
    random_id = generate_id()

    # 🚨 LIMIT LOGIC
    if shop.plan == "free" and shop.rules.count() >= 1:
        return HttpResponse(f"""
            <h2>Free plan limit reached</h2>
            <p>You can only create 1 rule on Free plan.</p>

            <a href="/shopify/upgrade/?shop={shop.shop_domain}">
                <button>Upgrade to Pro ($12/month)</button>
            </a>
        """)
    
    

    if request.method == "POST":
        Rule.objects.create(
            shop=shop,
            name=request.POST.get("name"),
            rule_type=request.POST.get("rule_type"),
            summary=request.POST.get("summary"), 
            min_cart_value=request.POST.get("min_cart_value") or None,
            shipping_method_name=request.POST.get("shipping_method") or None,
            payment_method_name=request.POST.get("payment_method") or None,
            region=request.POST.get("region"),
            condition_type=request.POST.get("condition_type") or "and",
            rule_id=random_id,
            is_active = False,
        )

        return redirect(f"/shopify/app/?shop={shop.shop_domain}")
    
    
    methods = get_shipping_methods(
        shop.shop_domain,
        shop.access_token
    )

    return render(request, "create_rule.html", {
        "methods": methods,
    })


def upgrade(request):
    shop_domain = request.GET.get("shop")
    shop = Shop.objects.get(shop_domain=shop_domain)

    url = f"https://{shop_domain}/admin/api/2024-01/recurring_application_charges.json"

    headers = {
        "X-Shopify-Access-Token": shop.access_token,
        "Content-Type": "application/json",
    }

    return_url = f"https://checkout-rules.onrender.com/shopify/billing/callback/?shop={shop_domain}"

    data = {
        "recurring_application_charge": {
            "name": "Smart Shipping Pro",
            "price": 12.0,
            "return_url": return_url,
            "trial_days": 0,
            "test": True
        }
    }

    r = requests.post(url, json=data, headers=headers)
    data = r.json()
    print(data)

    charge = data.get("recurring_application_charge")

    if not charge:
        return HttpResponse(f"Billing error: {data}")

    # ✅ ADD THIS LINE
    confirmation_url = charge.get("confirmation_url")

    return redirect(confirmation_url)


def billing_callback(request):
    shop_domain = request.GET.get("shop")
    charge_id = request.GET.get("charge_id")
    store_name = shop_domain.replace(".myshopify.com", "")

    shop = Shop.objects.get(shop_domain=shop_domain)

    url = f"https://{shop_domain}/admin/api/2024-01/recurring_application_charges/{charge_id}.json"

    headers = {
        "X-Shopify-Access-Token": shop.access_token,
    }

    r = requests.get(url, headers=headers)
    data = r.json()

    print("BILLING CHECK:", data)

    charge = data["recurring_application_charge"]

    if charge and charge["status"] == "active":
        shop.plan = "Pro"
        shop.save()   
        print("PLAN ACTIVATED & SAVED")

    return redirect(f"https://admin.shopify.com/store/{store_name}/apps/oeme-checkout-rules")


def activate_rule(request):

    rule_id = request.POST.get("rule_id")
    rule = Rule.objects.get(id=rule_id)
    shop = rule.shop

    if rule.rule_type == "hide_payment":

        payment_id = create_payment_customization(
            shop.shop_domain,
            shop.access_token,
            rule.name
        )

        save_payment_config(
            shop.shop_domain,
            shop.access_token,
            payment_id,
            rule.payment_method_name,
            rule.min_cart_value,
            rule.region,
            rule.condition_type
        )

        rule.shopify_payment_id = payment_id
        rule.is_active = True
        rule.save()


    elif rule.rule_type == "hide_shipping":

        delivery_id = create_delivery_customization(
            shop.shop_domain,
            shop.access_token
        )

        save_shipping_config(
            shop.shop_domain,
            shop.access_token,
            delivery_id,
            rule.shipping_method_name,
            rule.min_cart_value,
            rule.region,
            rule.condition_type
        )

        rule.shopify_delivery_id = delivery_id
        rule.is_active = True
        rule.save()

    return redirect(f"/shopify/app/?shop={shop.shop_domain}")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def data_deletion_policy(request):
    return render(request, "data_deletion_policy.html")


def delete_rule(request):

    rule_id = request.POST.get("rule_id")
    rule = Rule.objects.get(id=rule_id)
    shop = rule.shop

    if rule.rule_type == "hide_payment" and rule.shopify_payment_id:

        delete_payment_customization(
            shop.shop_domain,
            shop.access_token,
            rule.shopify_payment_id
        )

    if rule.rule_type == "hide_shipping" and rule.shopify_delivery_id:

        delete_delivery_customization(
            shop.shop_domain,
            shop.access_token,
            rule.shopify_delivery_id
        )

    rule.delete()

    return redirect(f"/shopify/app/?shop={shop.shop_domain}")


def deactivate_rule(request):

    rule_id = request.POST.get("rule_id")

    rule = Rule.objects.get(id=rule_id)
    shop = rule.shop

    # deactivate payment rule
    if rule.rule_type == "hide_payment" and rule.shopify_payment_id:

        deactivate_payment_customization(
            shop.shop_domain,
            shop.access_token,
            rule.shopify_payment_id
        )

    # deactivate shipping rule
    elif rule.rule_type == "hide_shipping" and rule.shopify_delivery_id:

        deactivate_delivery_customization(
            shop.shop_domain,
            shop.access_token,
            rule.shopify_delivery_id
        )

    rule.is_active = False
    rule.save()

    return redirect(f"/shopify/app/?shop={shop.shop_domain}")


def verify_webhook(request):
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        request.body,
        hashlib.sha256
    ).digest()

    computed_hmac = base64.b64encode(digest).decode()

    return hmac.compare_digest(computed_hmac, hmac_header)


@csrf_exempt
def app_uninstalled(request):
    if request.method == "POST":

        # 🔐 VERIFY FIRST
        if not verify_webhook(request):
            return HttpResponse("Invalid webhook", status=401)

        import json
        data = json.loads(request.body)

        shop_domain = data.get("domain")

        try:
            shop = Shop.objects.get(shop_domain=shop_domain)
            shop.is_active = False
            shop.access_token = ""  # 🔥 important
            shop.save()

            print(f"{shop_domain} marked as inactive")

        except Shop.DoesNotExist:
            pass

        return HttpResponse(status=200)

    return HttpResponse(status=405)