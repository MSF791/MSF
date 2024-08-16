document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('toggleButton').addEventListener('click', function() {
        var productList = document.getElementById('productList');
        productList.classList.toggle('show');
    });

    document.getElementById('close').addEventListener('click', function() {
        var productList = document.getElementById('productList');
        productList.classList.remove('show');
    });
});
