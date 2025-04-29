document.addEventListener("DOMContentLoaded", () => {
    const bottomButton = document.getElementById("bottom_button");

    bottomButton.addEventListener("mouseenter", () => {
        bottomButton.classList.add("hovered");
    });

    bottomButton.addEventListener("mouseleave", () => {
        bottomButton.classList.remove("hovered");
        bottomButton.classList.remove("clicked"); // por si se queda activado
    });

    bottomButton.addEventListener("mousedown", () => {
        bottomButton.classList.add("clicked");
    });

    bottomButton.addEventListener("mouseup", () => {
        bottomButton.classList.remove("clicked");
    });
});
