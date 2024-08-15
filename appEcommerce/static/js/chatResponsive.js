document.addEventListener('DOMContentLoaded', function() {
    if (window.matchMedia('(max-width: 748px)').matches) {
        const chatLinks = document.querySelectorAll('.collectionChats a');
        const container = document.getElementById('prueba');

        chatLinks.forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();  // Evitar la redirección automática
                const targetChatUrl = this.getAttribute('data-chat-url');

                // Redirigir a la URL de destino
                window.location.href = targetChatUrl;
            });
        });

        // Verificar si la URL actual incluye alguna de las URLs de chat
        const currentUrl = window.location.href;
        chatLinks.forEach(function(link) {
            const targetChatUrl = link.getAttribute('data-chat-url');
            if (currentUrl.includes(targetChatUrl)) {
                container.classList.add("active");
            }
        });
    }
});


