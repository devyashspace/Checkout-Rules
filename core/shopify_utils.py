import requests
import json

def create_delivery_customization(shop, access_token):
    url = f"https://{shop}/admin/api/2026-01/graphql.json"

    query = """
    mutation {
      deliveryCustomizationCreate(
        deliveryCustomization: {
          title: "Hide Shipping"
          enabled: true
          functionHandle: "hide-shipping"
        }
      ) {
        deliveryCustomization {
          id
        }
        userErrors {
          message
        }
      }
    }
    """

    res = requests.post(
        url,
        json={"query": query},
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        },
    )

    data = res.json()
    print(json.dumps(data, indent=2))

    return data["data"]["deliveryCustomizationCreate"]["deliveryCustomization"]["id"]


def save_shipping_config(shop, access_token, delivery_id, keyword, min_cart_value=None, region=None, condition_type="and"):
    url = f"https://{shop}/admin/api/2025-07/graphql.json"

    query = """
    mutation metafieldsSet($metafields:[MetafieldsSetInput!]!) {
      metafieldsSet(metafields:$metafields) {
        metafields { id }
        userErrors { message }
      }
    }
    """

    variables = {
        "metafields": [
            {
                "namespace": "$app:hide-shipping",
                "key": "function-configuration",
                "ownerId": delivery_id,
                "type": "json",
                "value": json.dumps({
                    "keyword": keyword,
                    "min_cart_value": min_cart_value,
                    "region": region,
                    "condition_type": condition_type
                })
            }
        ]
    }

    response = requests.post(
        url,
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        },
        json={"query": query, "variables": variables},
    )

    # DEBUG PRINT
    print("METAFIELD SAVE RESPONSE:", response.json())

    return response.json()


def get_shipping_methods(shop, access_token):
    url = f"https://{shop}/admin/api/2025-01/shipping_zones.json"

    r = requests.get(
        url,
        headers={"X-Shopify-Access-Token": access_token}
    ).json()

    methods = []

    for zone in r.get("shipping_zones", []):
        for rate in zone.get("price_based_shipping_rates", []):
            methods.append(rate["name"])

        for rate in zone.get("weight_based_shipping_rates", []):
            methods.append(rate["name"])

    return list(set(methods))


def create_payment_customization(shop, access_token, rule_name):
    url = f"https://{shop}/admin/api/2026-01/graphql.json"

    query = """
    mutation CreatePaymentCustomization($title: String!) {
      paymentCustomizationCreate(
        paymentCustomization: {
          title: $title
          enabled: true
          functionHandle: "hide-payment"
        }
      ) {
        paymentCustomization {
          id
        }
        userErrors {
          message
        }
      }
    }
    """

    variables = {
        "title": rule_name
    }

    res = requests.post(
        url,
        json={
            "query": query,
            "variables": variables
        },
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        },
    )

    data = res.json()
    print(json.dumps(data, indent=2))

    return data["data"]["paymentCustomizationCreate"]["paymentCustomization"]["id"]


def save_payment_config(shop, access_token, payment_id, keyword, min_cart_value=None, region=None, condition_type="and"):
    url = f"https://{shop}/admin/api/2025-07/graphql.json"

    query = """
    mutation metafieldsSet($metafields:[MetafieldsSetInput!]!) {
      metafieldsSet(metafields:$metafields) {
        metafields { id }
        userErrors { message }
      }
    }
    """

    variables = {
        "metafields": [
            {
                "namespace": "$app:hide-payment",
                "key": "function-configuration",
                "ownerId": payment_id,
                "type": "json",
                "value": json.dumps({
                    "keyword": keyword,
                    "min_cart_value": min_cart_value,
                    "region": region,
                    "condition_type": condition_type
                })
            }
        ]
    }

    response = requests.post(
        url,
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        },
        json={"query": query, "variables": variables},
    )

    print("PAYMENT METAFIELD SAVE:", response.json())

    return response.json()



    