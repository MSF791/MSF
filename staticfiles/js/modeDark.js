document.getElementById('toggle-mode').addEventListener('click', function() {
    // Alternar entre clases dark-mode y light-mode en el body
    document.body.classList.toggle('dark-mode');
    document.body.classList.toggle('light-mode');
});