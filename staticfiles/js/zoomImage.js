const container = document.getElementById("zoom-container");
const image = container.querySelector("img");

container.addEventListener("mousemove", function(e) {
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Cambia el punto de origen del zoom a donde está el ratón
    image.style.transformOrigin = `${x}px ${y}px`;
});

container.addEventListener("mouseleave", function() {
    // Resetea el punto de origen del zoom cuando el ratón sale
    image.style.transformOrigin = "center center";
});
