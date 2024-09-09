document.addEventListener('DOMContentLoaded', function() {
    let globalIndex = 1; // Variable para mantener el índice global

    function updateCarouselControls() {
        document.querySelectorAll('.carousel').forEach(function(carousel) {
            const prevButton = carousel.querySelector('.carousel-control-prev');
            const nextButton = carousel.querySelector('.carousel-control-next');
            const carouselInner = carousel.querySelector('.carousel-inner');

            if (!prevButton || !nextButton || !carouselInner) {
                return; // Si alguno de los elementos no se encuentra, no hacer nada
            }

            const items = carouselInner.querySelectorAll('.carousel-item');
            if (items.length === 0) {
                return; // Si no hay elementos en el carrusel, no hacer nada
            }

            const firstItem = items[0];
            const lastItem = items[items.length - 1];

            if (!firstItem || !lastItem) {
                return; // Si no se encuentran el primer o último ítem, no hacer nada
            }

            const isFirstItemActive = firstItem.classList.contains('active');
            const isLastItemActive = lastItem.classList.contains('active');

            prevButton.style.display = isFirstItemActive ? 'none' : 'block';
            nextButton.style.display = isLastItemActive ? 'none' : 'block';
        });
    }

    function updateCardNumbers() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const rankElement = card.querySelector('.card-rank');
            if (rankElement) {
                // Asignar el número solo si está dentro del rango permitido
                if (globalIndex <= 10) {
                    rankElement.textContent = globalIndex;
                } else {
                    rankElement.textContent = ''; // Limpiar el contenido si supera el rango
                }
                globalIndex++;
            }
        });
    }

    function resetGlobalIndex() {
        globalIndex = 1; // Resetear el índice global al principio de cada diapositiva
    }

    // Actualizar controles del carrusel y números de las tarjetas inicialmente
    updateCarouselControls();
    updateCardNumbers();

    // Actualizar los controles del carrusel y números de las tarjetas al cambiar de diapositiva
    document.querySelectorAll('.carousel').forEach(function(carousel) {
        carousel.addEventListener('slid.bs.carousel', function() {
            updateCarouselControls();
            resetGlobalIndex(); // Resetear el índice global cuando se cambia de diapositiva
            updateCardNumbers(); // Recalcular los números después de cambiar de diapositiva
        });
    });
});