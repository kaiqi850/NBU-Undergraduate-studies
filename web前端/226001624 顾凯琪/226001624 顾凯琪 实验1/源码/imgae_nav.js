document.addEventListener("DOMContentLoaded", function() {
    const slides = document.querySelector(".slides");
    const prevBtn = document.querySelector(".prev-btn");
    const nextBtn = document.querySelector(".next-btn");

    let scrollAmount = 0;

    nextBtn.addEventListener("click", function() {
        scrollAmount += 300; // 调整滚动量
        slides.scrollTo({
            top: 0,
            left: scrollAmount,
            behavior: "smooth"
        });
    });

    prevBtn.addEventListener("click", function() {
        scrollAmount -= 300; // 调整滚动量
        slides.scrollTo({
            top: 0,
            left: scrollAmount,
            behavior: "smooth"
        });
    });
});
