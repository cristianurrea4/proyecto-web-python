function showFlashMessage(message, category) {

    // Función para crear y mostrar el mensaje de flash
    const alertContainer = document.querySelector('.alert-container');
    const alertMessage = document.createElement('div');
    alertMessage.classList.add('alert', `alert-${category}`);
    alertMessage.textContent = message.replace('[profile]', '');
    alertContainer.appendChild(alertMessage);
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profile-form');
    const saveChangesBtn = document.getElementById('save-changes-btn');
    const inputs = form.querySelectorAll('input, textarea');

    // Image de perfil
    document.getElementById('profile_image').addEventListener('change', function() {
        var form = document.getElementById('image-upload-form');
        var formData = new FormData(form);

        fetch(uploadProfileImageUrl, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Crear o actualizar la imagen de perfil
                    let img = document.querySelector('.profile-image');

                    if (!img) {
                        // Si la imagen no existe, crear una nueva
                        img = document.createElement('img');
                        img.classList.add('img-fluid', 'rounded-circle', 'profile-image');
                        const container = document.querySelector('.profile-image-container');
                        container.innerHTML = ''; // Limpiar el contenido actual
                        container.appendChild(img);
                    }

                    img.src = 'data:image/jpeg;base64,' + data.new_image_base64;

                    // Actualizar la vista previa de la imagen de perfil en la navegación
                    let preview = document.getElementById('profile-image-nav');
                    if (preview) {
                        preview.src = 'data:image/jpeg;base64,' + data.new_image_base64;
                    }

                    // Mostrar el mensaje flash de éxito
                    showFlashMessage('[profile]La imagen ha sido actualizada con éxito', 'success');

                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    });
});