document.addEventListener("DOMContentLoaded", function () {
    const mainContent = document.querySelector(".main-content");
    const loader = document.querySelector(".mid-loader-container");

    function showLoader() {
        mainContent.style.display = "none";
        loader.style.display = "flex"; // or block based on your CSS
    }

    // Handle all buttons
    document.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", function () {
            showLoader();
        });
    });

    // Handle all links
    document.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", function (e) {
            const href = link.getAttribute("href");

            // Skip empty or anchor links
            if (!href || href.startsWith("#")) return;

            showLoader();
        });
    });
});


