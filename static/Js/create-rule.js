let index = 0;
const slides = document.getElementById("slides");
const totalSlides = 4;

const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

const shippingField = document.getElementById("shippingField");
const paymentField = document.getElementById("paymentField");


// SLIDE CONTROL
function updateSlide() {

    slides.style.transform = "translateX(" + (-index * 100) + "%)";

    // Hide previous on first slide
    if (index === 0) {
        prevBtn.style.display = "none";
    } else {
        prevBtn.style.display = "inline-block";
    }

    // Change Next → Save on last slide
    if (index === totalSlides - 1) {
        nextBtn.textContent = "Save";
        nextBtn.classList.add("save-btn");
    } else {
        nextBtn.textContent = "Next";
        nextBtn.classList.remove("save-btn");
    }

    // Update rule fields when entering conditions slide
    if (index === 2) {
        updateRuleFields();
    }

    // Update summary when entering final slide
    if (index === 3) {
        updateSummary();
    }
}


// NEXT BUTTON
function nextSlide() {

    // SLIDE 1 VALIDATION
    if (index === 0) {
        const selected = document.querySelector('input[name="rule_type"]:checked');

        if (!selected) {
            alert("Please select what you want to hide.");
            return;
        }
    }


    // SLIDE 2 VALIDATION
    if (index === 1) {
        const ruleName = document.getElementById("ruleInput").value.trim();

        if (!ruleName) {
            alert("Please enter a rule name.");
            return;
        }
    }


    // SLIDE 3 VALIDATION
    if (index === 2) {

        const selectedRule = document.querySelector('input[name="rule_type"]:checked');

        const shippingMethod = shippingField.value;
        const paymentMethod = paymentField.value.trim();

        const cartValue = document.querySelector('input[name="min_cart_value"]').value;
        const region = document.querySelector('select[name="region"]').value;

        // shipping / payment validation
        if (selectedRule.value === "hide_shipping" && !shippingMethod) {
            alert("Please select a shipping method.");
            return;
        }

        if (selectedRule.value === "hide_payment" && !paymentMethod) {
            alert("Please enter a payment method.");
            return;
        }

        // condition validation (at least one required)
        if (!cartValue && !region) {
            alert("Please enter at least one condition (cart value or region).");
            return;
        }
    }


    // MOVE SLIDE
    if (index < totalSlides - 1) {
        index++;
        updateSlide();
    } else {
        document.querySelector("form").submit();
    }
}


// PREVIOUS BUTTON
function prevSlide() {

    if (index > 0) {
        index--;
        updateSlide();
    }

}


// RULE FIELD SWITCHING
function updateRuleFields() {

    const selected = document.querySelector('input[name="rule_type"]:checked');

    if (!selected) return;

    if (selected.value === "hide_shipping") {
        shippingField.style.display = "block";
        paymentField.style.display = "none";
    }

    if (selected.value === "hide_payment") {
        shippingField.style.display = "none";
        paymentField.style.display = "block";
    }
}


// SUMMARY GENERATOR
function updateSummary(){

    const ruleName = document.getElementById("ruleInput").value || "rule-name";

    const selectedRule = document.querySelector('input[name="rule_type"]:checked');
    const ruleType = selectedRule ? selectedRule.value : "";

    const shippingMethod = shippingField.value;
    const paymentMethod = paymentField.value;

    const cartValue = document.querySelector('input[name="min_cart_value"]').value;
    const region = document.querySelector('select[name="region"]').value;

    const conditionType = document.querySelector('select[name="condition_type"]').value;

    document.getElementById("summaryName").textContent = ruleName;

    if(ruleType === "hide_shipping"){
        document.getElementById("summaryType").textContent = "shipping method";
        document.getElementById("summaryMethod").textContent = shippingMethod;
    }

    if(ruleType === "hide_payment"){
        document.getElementById("summaryType").textContent = "payment method";
        document.getElementById("summaryMethod").textContent = paymentMethod || "Payment Method";
    }

    const operator = conditionType === "IN" ? "and" : "or";

    let conditions = "";

    // BOTH conditions
    if(cartValue && region){
        conditions = `when minimum cart value is <strong>${cartValue}</strong> ${operator} region is <strong>${region}</strong>`;
    }

    // ONLY cart
    else if(cartValue){
        conditions = `when minimum cart value is <strong>${cartValue}</strong>`;
    }

    // ONLY region
    else if(region){
        conditions = `when region is <strong>${region}</strong>`;
    }

    // NO conditions
    else{
        conditions = "";
    }

    document.getElementById("summaryConditions").innerHTML = conditions;

    const fullSummary = document.querySelector(".overview-channel p").innerText;
    document.getElementById("summaryField").value = fullSummary;
}

// WAIT FOR DOM
document.addEventListener("DOMContentLoaded", function () {

    const ruleOptions = document.querySelectorAll('input[name="rule_type"]');

    ruleOptions.forEach(option => {
        option.addEventListener("change", updateRuleFields);
    });

    // Update summary when inputs change
    document.querySelectorAll("input, select").forEach(el => {
        el.addEventListener("input", updateSummary);
    });

});


// CHARACTER COUNTER
const input = document.getElementById("ruleInput");
const charCount = document.getElementById("charCount");
const maxChars = 50;

if (input) {

    input.addEventListener("input", function () {

        const remaining = maxChars - input.value.length;
        charCount.textContent = remaining;

    });

}


// Run once on load
updateSlide();