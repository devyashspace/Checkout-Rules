export function cartDeliveryOptionsTransformRun(input) {
  const config =
    input.deliveryCustomization?.metafield?.jsonValue || {};

  const keyword = (config.keyword || "").trim().toLowerCase();
  const minCartValue = parseFloat(config.min_cart_value || 0);
  const region = (config.region || "").trim().toLowerCase();
  const conditionType = (config.condition_type || "and").toLowerCase();

  const operations = [];

  if (!keyword) {
    return { operations };
  }

  // Get cart total safely
  const cartTotal = parseFloat(
    input.cart?.cost?.subtotalAmount?.amount || 0
  );

  // Get shipping country safely
  const shippingCountry =
    input.cart?.deliveryGroups?.[0]?.deliveryAddress?.countryCode?.toLowerCase() || "";

  // Determine individual conditions
  const hasCartCondition = !!minCartValue;
  const hasRegionCondition = !!region;

  const cartCondition = hasCartCondition
    ? cartTotal >= minCartValue
    : false;

  const regionCondition = hasRegionCondition
    ? shippingCountry === region
    : false;

  let shouldApply = false;

  // ----------------------------
  // CONDITION LOGIC HANDLING
  // ----------------------------

  if (conditionType === "and") {
    // For AND:
    // If condition exists, it must pass.
    // If condition does not exist, ignore it.
    shouldApply =
      (hasCartCondition ? cartCondition : true) &&
      (hasRegionCondition ? regionCondition : true);

  } else if (conditionType === "or") {
    // For OR:
    // At least one existing condition must pass.
    shouldApply =
      (hasCartCondition && cartCondition) ||
      (hasRegionCondition && regionCondition);
  }

  if (!shouldApply) {
    return { operations };
  }

  // ----------------------------
  // HIDE SHIPPING OPTIONS
  // ----------------------------

  for (const group of input.cart.deliveryGroups) {
    for (const option of group.deliveryOptions) {
      if (
        option.title &&
        option.title.toLowerCase().includes(keyword)
      ) {
        operations.push({
          deliveryOptionHide: {
            deliveryOptionHandle: option.handle
          }
        });
      }
    }
  }

  return { operations };
}