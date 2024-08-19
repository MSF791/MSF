const carousel = document.querySelector('.carousel');
let currentIndex = 0;

function showNextItem() {
    const items = document.querySelectorAll('.carousel-item');
    currentIndex = (currentIndex + 1) % items.length;
    updateCarousel();
}

function showPrevItem() {
    const items = document.querySelectorAll('.carousel-item');
    currentIndex = (currentIndex - 1 + items.length) % items.length;
    updateCarousel();
}

function updateCarousel() {
    const items = document.querySelectorAll('.carousel-item');
    const offset = -currentIndex * 100;
    items.forEach(item => {
        item.style.transform = `translateX(${offset}%)`;
    });
}

setInterval(showNextItem, 6000); // Cambia el valor para ajustar la velocidad de transición en milisegundos
