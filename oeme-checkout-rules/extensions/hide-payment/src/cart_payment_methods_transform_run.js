export function cartPaymentMethodsTransformRun(input) {
  const config =
    input.paymentCustomization?.metafield?.jsonValue || {};

  const keyword = (config.keyword || "").trim().toLowerCase();
  const minCartValue = parseFloat(config.min_cart_value || 0);
  const region = (config.region || "").trim().toLowerCase();
  const conditionType = (config.condition_type || "and").toLowerCase();

  const operations = [];

  if (!keyword) {
    return { operations };
  }

  // ----------------------------
  // SAFE DATA EXTRACTION
  // ----------------------------

  const cartTotal = parseFloat(
    input.cart?.cost?.subtotalAmount?.amount || 0
  );

  const shippingCountry =
    input.cart?.deliveryGroups?.[0]?.deliveryAddress?.countryCode?.toLowerCase() || "";

  // ----------------------------
  // CONDITION FLAGS
  // ----------------------------

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
  // CONDITION LOGIC
  // ----------------------------

  if (conditionType === "and") {
    shouldApply =
      (hasCartCondition ? cartCondition : true) &&
      (hasRegionCondition ? regionCondition : true);

  } else if (conditionType === "or") {
    shouldApply =
      (hasCartCondition && cartCondition) ||
      (hasRegionCondition && regionCondition);
  }

  if (!shouldApply) {
    return { operations };
  }

  // ----------------------------
  // HIDE PAYMENT METHODS
  // ----------------------------

  for (const method of input.paymentMethods || []) {
    if (
      method.name &&
      method.name.toLowerCase().includes(keyword)
    ) {
      operations.push({
        paymentMethodHide: {
          paymentMethodId: method.id
        }
      });
    }
  }

  return { operations };
}