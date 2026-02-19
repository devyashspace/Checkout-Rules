from django.http import HttpResponse
from django.shortcuts import redirect
import os
from urllib.parse import urlencode
import hashlib
import hmac
import requests
from django.conf import settings
from .models import Shop, Rule
from django.shortcuts import render
from .shopify_utils import create_delivery_customization, save_shipping_config, get_shipping_methods


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
        "redirect_uri": "https://gonadial-ninfa-nonanimated.ngrok-free.dev/shopify/callback/",
    }

    auth_url = f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"
    return redirect(auth_url)


def callback(request):
    params = request.GET.dict()
    hmac_received = params.pop("hmac", None)

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

    

    

    

    host = request.GET.get("host")

    return redirect(f"/shopify/app/?shop={shop}&host={host}")


def app_home(request):
    shop_domain = request.GET.get("shop")
    host = request.GET.get("host")

    shop = Shop.objects.filter(shop_domain=shop_domain).first()
    rules = Rule.objects.filter(shop=shop) if shop else []

    response = render(request, "app_home.html", {
        "shop": shop,
        "rules": rules,
        "host": host,
    })

    response["Content-Security-Policy"] = "frame-ancestors https://admin.shopify.com https://*.myshopify.com;"

    return response


def create_rule(request):
    shop_domain = request.GET.get("shop")
    shop = Shop.objects.filter(shop_domain=shop_domain).first()

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
            min_cart_value=request.POST.get("min_cart_value") or None,
            shipping_method_name=request.POST.get("shipping_method") or None,
        )

        return redirect(f"/shopify/app/?shop={shop.shop_domain}")
    
    
    methods = get_shipping_methods(
        shop.shop_domain,
        shop.access_token
    )

    return render(request, "create_rule.html", {
        "methods": methods
    })


def upgrade(request):
    shop_domain = request.GET.get("shop")
    shop = Shop.objects.get(shop_domain=shop_domain)

    url = f"https://{shop_domain}/admin/api/2024-01/recurring_application_charges.json"

    headers = {
        "X-Shopify-Access-Token": shop.access_token,
        "Content-Type": "application/json",
    }

    return_url = f"https://gonadial-ninfa-nonanimated.ngrok-free.dev/shopify/billing/callback/?shop={shop_domain}"

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

    return render(request, "billing_redirect.html", {
        "confirmation_url": confirmation_url,
        "shop": shop_domain
    })


def billing_callback(request):
    shop_domain = request.GET.get("shop")
    charge_id = request.GET.get("charge_id")

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
        shop.plan = "pro"
        shop.save()   
        print("PLAN ACTIVATED & SAVED")

    return redirect(f"/shopify/app/?shop={shop_domain}")


def activate_rule(request):
    shop_domain = request.POST.get("shop_domain")
    shop = Shop.objects.filter(shop_domain=shop_domain).first()

    keyword = request.POST.get("shipping_method")
    rule_type = request.POST.get("rule_type")

    # create once
    
    delivery_id = create_delivery_customization(
        shop.shop_domain,
        shop.access_token
    )
    
    save_shipping_config(
        shop.shop_domain,
        shop.access_token,
        delivery_id,
        keyword
    )


    print("Activated, Shipping Method:", keyword)

    return redirect(f"/shopify/app/?shop={shop.shop_domain}")


