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


def save_shipping_config(shop, access_token, delivery_id, keyword):
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
                "value": json.dumps({"keyword": keyword})
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
