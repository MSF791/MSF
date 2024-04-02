const cartBtn = document.getElementById('cart-btn');

cartBtn.addEventListener('click', () => {
  cartBtn.classList.toggle('active');
});

document.getElementById('cart-btn').addEventListener('click', function() {
    this.classList.add('btn-success'); // Agrega la clase 'btn-success' para cambiar el color del botón
    setTimeout(() => {
        window.location.href = agregarAlCarritoUrl; // Redirige al usuario después de 1 segundo
    }, 1500); // Retraso de 1 segundo (1000 milisegundos)
});


const cartBtn2 = document.getElementById('cart-btn-2');

cartBtn2.addEventListener('click', () => {
  cartBtn2.classList.toggle('active');
});
document.getElementById('cart-btn-2').addEventListener('click', function() {
  url = this.dataset.url
  console.log('hizo click en el boton')
  this.classList.add('btn-danger'); // Agrega la clase 'btn-success' para cambiar el color del botón
  setTimeout(() => {
      window.location.href = url; // Redirige al usuario después de 1 segundo
  }, 1500); // Retraso de 1 segundo (1000 milisegundos)
});
