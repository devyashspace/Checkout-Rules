export function cartDeliveryOptionsTransformRun(input) {
  const config =
    input.deliveryCustomization?.metafield?.jsonValue || {};

  const keyword = (config.keyword || "")
    .trim()
    .toLowerCase();

  // DEBUG LOG
  console.error("KEYWORD:", keyword);

  const operations = [];

  if (!keyword) {
    console.error("NO KEYWORD FOUND");
    return { operations };
  }

  for (const group of input.cart.deliveryGroups) {
    for (const option of group.deliveryOptions) {

      console.error("OPTION:", option.title);

      if (
        option.title &&
        option.title.toLowerCase().includes(keyword)
      ) {
        console.error("HIDING:", option.title);

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