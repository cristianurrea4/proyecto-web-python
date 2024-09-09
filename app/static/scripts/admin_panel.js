function urlImagePreview(url) {
    if (url) {
        document.getElementById('image_base64').value = '';
        let preview = document.getElementById('image_preview');
        preview.src = url;
        preview.style.display = 'block';
    }
}

const el = document.getElementById('search');
const el_clear = document.getElementById('clear-fields');

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el ancla de la URL (si existe)
    var hash = window.location.hash;

    // Si existe un ancla, hacer clic en la pestaña correspondiente
    if (hash) {
        var tabLink = document.querySelector('a[href="' + hash + '"]');
        if (tabLink) {
            tabLink.click();
        }
    }
});

// Manejar el botón para cargar la imagen
document.getElementById('upload_button').addEventListener('click', function() {
    let fileInput = document.getElementById('image_upload');
    fileInput.click(); // Simular clic en el campo de archivo
});

// Manejar la vista previa de la imagen desde un archivo
document.getElementById('image_upload').addEventListener('change', function(event) {
    let file = event.target.files[0];
    if (file) {
        console.log(file)
        let reader = new FileReader();
        reader.onload = function() {
            let preview = document.getElementById('image_preview');
            preview.src = reader.result;
            preview.style.display = 'block';
            document.getElementById('image_base64').value = reader.result;
            document.getElementById('image_url').value = file.name;
        };
        reader.readAsDataURL(file);
    }
});

// Manejar la vista previa de la imagen desde una URL
document.getElementById('image_url').addEventListener('input', function() {
    let url = this.value;
    urlImagePreview(url);
});

// Manejar el cambio de tipo de contenido (película/serie)
document.getElementById('type').addEventListener('change', function() {
    let tvFields = document.getElementById('tv-fields');
    if (this.value === 'tv') {
        tvFields.hidden = false;
    } else {
        tvFields.hidden = true;
    }
});

if (el) {
    el.addEventListener('input', function() {
        let query = this.value.trim(); // Eliminar espacios en blanco

        let searchResults = document.getElementById('search-results');

        // Si el campo de búsqueda está vacío, ocultar los resultados y salir de la función
        if (!query) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }

        // Si hay una búsqueda activa, mostrar el contenedor de resultados
        searchResults.style.display = 'block';

        if (query.length < 3) return; // No iniciar la búsqueda si la consulta es menor a 3 caracteres

        fetch(`https://api.themoviedb.org/3/search/multi?query=${encodeURIComponent(query)}&api_key=${IMDB_API_KEY}&language=es-ES`)
            .then(response => response.json())
            .then(data => {
                let results = data.results || [];
                searchResults.innerHTML = ''; // Limpiar resultados anteriores

                results.forEach(item => {
                    if (item.media_type === 'movie' || item.media_type === 'tv') {
                        let itemElement = document.createElement('a');
                        itemElement.className = 'list-group-item list-group-item-action';
                        itemElement.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">${item.title || item.name}</h5>
                                <img src="https://image.tmdb.org/t/p/w200${item.poster_path}" alt="${item.title || item.name}" style="width: 50px; height: 75px; object-fit: cover;">
                            </div>
                        `;
                        itemElement.addEventListener('click', function() {
                            fetch(`https://api.themoviedb.org/3/${item.media_type}/${item.id}?api_key=${IMDB_API_KEY}&language=es-ES`)
                                .then(response => response.json())
                                .then(mediaDetails => {
                                    document.getElementById('title').value = mediaDetails.title || mediaDetails.name;
                                    document.getElementById('description').value = mediaDetails.overview;
                                    document.getElementById('image_url').value = `https://image.tmdb.org/t/p/w500${mediaDetails.poster_path}`;
                                    document.getElementById('release_date').value = mediaDetails.release_date || mediaDetails.first_air_date;
                                    document.getElementById('producer').value = mediaDetails.production_companies.map(pc => pc.name).join(', ');
                                    document.getElementById('rating').value = mediaDetails.vote_average;
                                    document.getElementById('type').value = item.media_type;

                                    if (item.media_type === 'tv') {
                                        document.getElementById('duration').value = '';
                                        document.getElementById('tv-fields').hidden = false;
                                        document.getElementById('seasons').value = mediaDetails.number_of_seasons || '';
                                        document.getElementById('episodes').value = mediaDetails.number_of_episodes || '';
                                        document.getElementById('episode_duration').value = mediaDetails.episode_run_time ? mediaDetails.episode_run_time[0] : '';
                                    } else {
                                        document.getElementById('duration').value = mediaDetails.runtime || '';
                                        document.getElementById('tv-fields').hidden = true;
                                        document.getElementById('seasons').value = '';
                                        document.getElementById('episodes').value = '';
                                        document.getElementById('episode_duration').value = '';
                                    }

                                    urlImagePreview(`https://image.tmdb.org/t/p/w500${mediaDetails.poster_path}`);
                                    document.getElementById('categories').value = mediaDetails.genres.map(genre => genre.name).join(', ');
                                    searchResults.innerHTML = '';
                                    searchResults.style.display = 'none';
                                });
                        });
                        searchResults.appendChild(itemElement);
                    }
                });

                // Si no hay resultados, ocultar el contenedor
                if (results.length === 0) {
                    searchResults.style.display = 'none';
                }
            });
    });
}

// Manejar el botón de limpiar campos
if (el_clear) {
    el_clear.addEventListener('click', function() {
        document.getElementById('search').value = '';
        document.getElementById('title').value = '';
        document.getElementById('image_url').value = '';
        document.getElementById('description').value = '';
        document.getElementById('release_date').value = '';
        document.getElementById('producer').value = '';
        document.getElementById('rating').value = '';
        document.getElementById('type').value = 'movie'; // Restablecer al valor predeterminado
        document.getElementById('tv-fields').hidden = true;
        document.getElementById('seasons').value = '';
        document.getElementById('episodes').value = '';
        document.getElementById('episode_duration').value = '';
        document.getElementById('duration').value = '';
        document.getElementById('categories').value = '';
    });

}

// Para asegurarse de que los campos se muestren/oculten correctamente al cargar los datos
document.getElementById('type').dispatchEvent(new Event('change'));