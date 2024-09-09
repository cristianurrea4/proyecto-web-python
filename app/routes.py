import io
import base64
import matplotlib
import matplotlib.pyplot as plt
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, session, login_manager
from app.models import User, Media, MediaLike, FavoriteMedia, MediaViewed
from app.forms import LoginForm, RegistrationForm, ProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from unidecode import unidecode

matplotlib.use('Agg')  # Usar el backend 'Agg' para gráficos no interactivos


# Función para devolver la imagen codificada o None
def image_profile():
    image_profile = None

    # Si el usuario tiene una imagen de perfil, se codifica en base64.
    if current_user.profile_image:
        image_profile = base64.b64encode(current_user.profile_image).decode('utf-8')
    return image_profile


@login_manager.user_loader
def load_user(user_id):
    """Carga el usuario actual en la sesión basándose en su ID."""
    return session.query(User).get(int(user_id))


''' LOGIN / REGISTRO / LOGOUT '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para gestionar el proceso de inicio de sesión de los usuarios."""
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.is_banned:
                flash('[login]Tu cuenta está bloqueada. No puedes iniciar sesión.', 'danger')
            else:
                login_user(user)
                return redirect(url_for('index'))
        else:
            flash('[login]Correo electrónico o contraseña incorrectos.', 'danger')

    # Renderizamos la plantilla 'login.html'
    return render_template('login.html', title='Iniciar sesión', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta para gestionar el registro de nuevos usuarios."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificamos si el nombre de usuario o el correo electrónico están reservados.
        reserved_names = ['admin', 'administrator', 'superuser']
        if form.username.data.lower() in reserved_names or form.email.data.lower() in [name + "@example.com" for name in
                                                                                       reserved_names]:
            flash('[register]El nombre de usuario o correo electrónico está reservado y no puede ser usado.', 'danger')
            return redirect(url_for('register'))

        # Creamos y guardamos el nuevo usuario en la base de datos.
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        session.add(new_user)
        session.commit()
        return redirect(url_for('login'))
    else:
        # Manejo de errores comunes durante el registro.
        user = session.query(User).filter_by(username=form.username.data).first()
        if user:
            flash('[register]El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('register'))

        user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            flash('[register]El correo electrónico ya está en uso.', 'danger')
            return redirect(url_for('register'))

        if form.password.data != form.confirm_password.data:
            flash('[register]Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))

    # Renderizamos la plantilla 'register.html'
    return render_template('register.html', title='Registro', form=form)


@app.route('/logout')
@login_required
def logout():
    """Cerramos la sesión del usuario y redirige a la página de login."""
    logout_user()
    return redirect(url_for('login'))


''' INICIO '''


@app.route('/')
@login_required
def index():
    """
    Ruta para la página principal del sitio, que muestra una vista general del contenido disponible.
    Se requiere que el usuario haya iniciado sesión.
    """

    user_id = current_user.id

    # Obtener las películas y series que se han añadido recientemente a la base de datos, ordenadas por fecha más reciente.
    recent_media = session.query(Media).order_by(Media.added_date.desc()).all()

    # Obtener las películas y series más populares, ordenadas primero por el número de "me gusta" y luego por la puntuación.
    popular_media = session.query(Media).outerjoin(Media.likes).group_by(Media.id).order_by(
        func.count(MediaLike.user_id).desc(), Media.rating.desc()).all()

    # Obtener todas las películas disponibles en la base de datos.
    movies = session.query(Media).filter(Media.type == 'movie').all()

    # Obtener todas las series disponibles en la base de datos.
    series = session.query(Media).filter(Media.type == 'tv').all()

    # Obtener los IDs de los media que el usuario ha marcado como "me gusta", favoritos y vistos.
    liked_media = {like.media_id for like in session.query(MediaLike).filter_by(user_id=user_id).all()}
    favorite_media = {favorite.media_id for favorite in session.query(FavoriteMedia).filter_by(user_id=user_id).all()}
    viewed_media = {viewed.media_id for viewed in session.query(MediaViewed).filter_by(user_id=user_id).all()}

    # Obtener la lista de media que el usuario ha visto.
    media_viewed_list = session.query(Media).filter(Media.id.in_(viewed_media)).all()

    # Definir el tamaño del grid para que el carrusel aparezca.
    carousel_size = 7

    # Renderizamos la plantilla 'index.html'
    return render_template('index.html', media=[], media_likes=liked_media, favorite_media=favorite_media,
                           media_viewed=viewed_media, recent_media=recent_media, popular_media=popular_media,
                           movies=movies, series=series, media_viewed_list=media_viewed_list, section_title="Home",
                           carousel_size=carousel_size, image_profile=image_profile())


''' SERIES Y PELÍCULAS '''


@app.route('/viewed')
@login_required
def viewed():
    """
    Ruta para filtrar las películas o series marcadas como vistas
    """
    user_id = current_user.id

    # Obtener los IDs de los media que el usuario ha marcado como vistos
    viewed_media_ids = {viewed.media_id for viewed in session.query(MediaViewed).filter_by(user_id=user_id).all()}

    # Filtrar los media que han sido marcados como vistos por el usuario
    media = session.query(Media).filter(Media.id.in_(viewed_media_ids)).all()

    # Obtener los IDs de los media que el usuario ha dado like y favoritos
    liked_media = {like.media_id for like in session.query(MediaLike).filter_by(user_id=user_id).all()}
    favorite_media = {favorite.media_id for favorite in session.query(FavoriteMedia).filter_by(user_id=user_id).all()}

    return render_template('index.html', media=media, media_likes=liked_media, favorite_media=favorite_media,
                           media_viewed=viewed_media_ids, section_title="Viewed", image_profile=image_profile())


@app.route('/series')
@login_required
def series():
    """
    Ruta para filtrar las series
    """

    user_id = current_user.id

    # Obtener solo series
    media = session.query(Media).outerjoin(Media.likes).group_by(Media.id).order_by(
        func.count(MediaLike.user_id).desc(), Media.rating.desc()).filter(Media.type == 'tv').all()

    # Obtener los IDs de las series que el usuario ha dado like, favoritas y vistas
    liked_media = {like.media_id for like in session.query(MediaLike).filter_by(user_id=user_id).all()}
    favorite_media = {favorite.media_id for favorite in session.query(FavoriteMedia).filter_by(user_id=user_id).all()}
    viewed_media = {viewed.media_id for viewed in session.query(MediaViewed).filter_by(user_id=user_id).all()}

    return render_template('index.html', media=media, media_likes=liked_media, favorite_media=favorite_media,
                           media_viewed=viewed_media, section_title="Series", image_profile=image_profile())


@app.route('/movies')
@login_required
def movies():
    """
    Ruta para filtrar las películas
    """

    user_id = current_user.id

    # Obtener solo películas
    media = session.query(Media).outerjoin(Media.likes).group_by(Media.id).order_by(
        func.count(MediaLike.user_id).desc(), Media.rating.desc()).filter(Media.type == 'movie').all()

    # Obtener los IDs de las películas que el usuario ha dado like, favoritas y vistas
    liked_media = {like.media_id for like in session.query(MediaLike).filter_by(user_id=user_id).all()}
    favorite_media = {favorite.media_id for favorite in session.query(FavoriteMedia).filter_by(user_id=user_id).all()}
    viewed_media = {viewed.media_id for viewed in session.query(MediaViewed).filter_by(user_id=user_id).all()}

    return render_template('index.html', media=media, media_likes=liked_media, favorite_media=favorite_media,
                           media_viewed=viewed_media, section_title="Movies", image_profile=image_profile())


@app.route('/media/<int:media_id>')
@login_required
def media_details(media_id):
    """
    Ruta para filtrar los media para ver mas detalles
    """

    media = session.query(Media).get(media_id)
    if not media:
        return redirect(url_for('index'))

    # Función para convertir minutos a formato hh:mm
    def format_duration(minutes):
        hours = minutes // 60
        minutes = minutes % 60
        if hours > 0:
            return f"{hours}:{minutes}h"
        else:
            return f"{minutes}m"

    # Formatear la duración de la media en hh:mm
    if media.duration > 0:
        media_duration_formatted = format_duration(media.duration)
    else:
        media_duration_formatted = '-'

    # Si es una serie 'TV', también formatea la duración de los episodios
    if media.type == 'tv':
        if media.episode_duration > 0:
            episode_duration_formatted = format_duration(media.episode_duration)
        else:
            episode_duration_formatted = '-'
    else:
        episode_duration_formatted = None

    return render_template('details.html', media=media, media_duration_formatted=media_duration_formatted,
                           episode_duration_formatted=episode_duration_formatted, image_profile=image_profile())


''' ADMIN '''


# Función para verificar si la cadena es una URL
def is_url(url):
    return url and url.startswith('https:')


@app.route('/admin')
@login_required
def admin_panel():
    """
    Ruta para el panel de administrador
    """

    # Comprobamos que el usuario actual es un administrador y no otro usuario
    if not current_user.is_admin:
        return redirect(url_for('index'))

    users = session.query(User).all()
    media = session.query(Media).all()

    # Obtener datos para la gráfica de estadísticas
    user_stats = []
    for user in users:
        # Contar películas vistas
        total_movies_watched = session.query(func.count(MediaViewed.media_id)).join(Media).filter(
            MediaViewed.user_id == user.id, Media.type == 'movie'
        ).scalar() or 0

        # Contar series vistas
        total_series_watched = session.query(func.count(MediaViewed.media_id)).join(Media).filter(
            MediaViewed.user_id == user.id, Media.type == 'tv'
        ).scalar() or 0

        # Calcular tiempo total en películas
        total_movie_time = session.query(func.sum(Media.duration)).join(MediaViewed).filter(
            MediaViewed.user_id == user.id, Media.type == 'movie'
        ).scalar() or 0

        # Calcular tiempo total en series
        total_series_time = session.query(func.sum(Media.episodes * Media.episode_duration)).join(MediaViewed).filter(
            MediaViewed.user_id == user.id, Media.type == 'tv'
        ).scalar() or 0

        user_stats.append(
            (user.username, total_movies_watched, total_series_watched, total_movie_time, total_series_time))

    # Crear gráfica comparativa de número de películas/series vistas
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    usernames, movies_watched, series_watched, total_movie_time, total_series_time = zip(*user_stats)

    # Gráfico 1: Número de películas/series vistas
    ax[0].bar(usernames, movies_watched, label='Películas Vistas', color='blue')
    ax[0].bar(usernames, series_watched, bottom=movies_watched, label='Series Vistas', color='green')
    ax[0].set_xlabel('Usuarios')
    ax[0].set_ylabel('Número de películas/series vistas')
    ax[0].set_title('Comparativa de Visualización por Usuario')
    ax[0].legend()

    # Gráfico 2: Tiempo total empleado
    ax[1].bar(usernames, total_movie_time, label='Tiempo en Películas (min)', color='blue')
    ax[1].bar(usernames, total_series_time, bottom=total_movie_time, label='Tiempo en Series (min)', color='green')
    ax[1].set_xlabel('Usuarios')
    ax[1].set_ylabel('Tiempo Total (minutos)')
    ax[1].set_title('Comparativa de Tiempo Empleado por Usuario')
    ax[1].legend()

    # Rotar etiquetas de los usuarios para mejor legibilidad
    plt.setp(ax[0].xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.setp(ax[1].xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Guardar gráfica en buffer es decir en memoria temporalmente
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('admin_panel.html', title='Panel de Administrador',
                           users=users, media=media, graph=data, image_profile=image_profile())


@app.route('/admin/add_media', methods=['POST'])
@login_required
def add_media():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    # Obtener datos del formulario
    title = request.form.get('title')
    description = request.form.get('description')
    release_date = request.form.get('release_date')
    producer = request.form.get('producer')
    rating = request.form.get('rating')
    type = request.form.get('type')
    duration = request.form.get('duration')
    seasons = request.form.get('seasons')
    episodes = request.form.get('episodes')
    episode_duration = request.form.get('episode_duration')
    categories = request.form.get('categories')

    # Obtener la URL de la imagen o la imagen subida como archivo
    image_url = request.form.get('image_url')
    image_base64 = request.form.get('image_base64')

    # Comprobamos la forma en que guardaremos la imagen por url o por fichero
    if image_url and is_url(image_url):
        image_base64 = image_url
    elif image_url == '':
        image_base64 = ''
    else:
        image_base64 = 'data:image/jpeg;base64,' + image_base64.split(',')[
            1]  # Eliminar la cabecera de datos URI si está presente

    # Validar campos requeridos
    if not title:
        flash('[add_media] El título es un campo obligatorio.', 'danger')
        return redirect(url_for('admin_panel'))

    # Comprobar si el título ya existe
    existing_media = session.query(Media).filter_by(title=title).first()
    if existing_media:
        flash('[add_media] Una película/serie con este título ya existe.', 'danger')
        return redirect(url_for('admin_panel'))

    # Convertir campos vacíos en valores predeterminados o `None`
    try:
        rating = float(rating) if rating else 0.0  # Proporciona un valor por defecto si es vacío
        duration = float(duration) if duration else 0.0
        seasons = int(seasons) if seasons else 0
        episodes = int(episodes) if episodes else 0
        episode_duration = float(episode_duration) if episode_duration else 0.0
    except ValueError:
        flash('[add_media] Algunos valores numéricos no son válidos. Asegúrese de ingresar valores válidos.', 'danger')
        return redirect(url_for('admin_panel'))

    new_media = Media(
        title=title,
        image_url=image_base64,
        description=description,
        release_date=release_date,
        producer=producer,
        rating=rating,
        type=type,
        duration=duration,
        seasons=seasons,
        episodes=episodes,
        episode_duration=episode_duration,
        categories=categories
    )
    session.add(new_media)
    session.commit()
    flash('[add_media]Película/Serie añadida con éxito.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/edit_media/<int:media_id>', methods=['GET', 'POST'])
@login_required
def edit_media(media_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    media = session.query(Media).get(media_id)  # Obtener Id del media
    if not media:
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        release_date = request.form.get('release_date')
        producer = request.form.get('producer')
        rating = request.form.get('rating')
        type = request.form.get('type')
        duration = request.form.get('duration')
        seasons = request.form.get('seasons')
        episodes = request.form.get('episodes')
        episode_duration = request.form.get('episode_duration')
        categories = request.form.get('categories')

        # Obtener la URL de la imagen o la imagen subida como archivo
        image_url = request.form.get('image_url')
        image_base64 = request.form.get('image_base64')

        if image_url and is_url(image_url):
            image_base64 = image_url
        elif image_base64:
            if ',' in image_base64:
                image_base64 = 'data:image/jpeg;base64,' + image_base64.split(',')[1]
            else:
                flash('[edit_media] Formato de imagen base64 no válido.', 'danger')
                return redirect(url_for('edit_media', media_id=media_id))
        else:
            image_base64 = ''  # Si no hay imagen nueva, dejamos la existente o vacía

        # Validar campos obligatorios
        if not title or not type:
            flash('[edit_media] El título y el tipo son campos obligatorios.', 'danger')
            return redirect(url_for('edit_media', media_id=media_id))

        # Comprobar si el título ya existe (excepto el actual registro)
        existing_media = session.query(Media).filter(Media.title == title, Media.id != media_id).first()
        if existing_media:
            flash('[edit_media] Una película/serie con este título ya existe.', 'danger')
            return redirect(url_for('edit_media', media_id=media_id))

        # Convertir campos vacíos en valores predeterminados o `None`
        try:
            rating = float(rating) if rating else 0.0
            duration = float(duration) if duration else 0.0
            seasons = int(seasons) if seasons else 0
            episodes = int(episodes) if episodes else 0
            episode_duration = float(episode_duration) if episode_duration else 0.0
        except ValueError:
            flash('[edit_media] Algunos valores numéricos no son válidos. Asegúrese de ingresar valores válidos.',
                  'danger')
            return redirect(url_for('edit_media', media_id=media_id))

        # Actualizar la película/serie
        media.title = title
        media.image_url = image_base64
        media.description = description
        media.release_date = release_date
        media.producer = producer
        media.rating = rating
        media.type = type
        media.duration = duration
        media.seasons = seasons
        media.episodes = episodes
        media.episode_duration = episode_duration
        media.categories = categories

        session.commit()

        # '_anchor' lo utilizo para especificar donde quiero que la url se desplace automáticamente dentro de la misma en la que se encuentra
        return redirect(url_for('admin_panel', _anchor='manage-media'))

    return render_template('edit_media.html', media=media, image_profile=image_profile())


@app.route('/admin/media/delete/<int:media_id>')
@login_required
def delete_media(media_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    # Obtener media a eliminar
    media = session.query(Media).get(media_id)

    if media:
        # Eliminar todos los registros relacionados en la tabla MediaLike
        session.query(MediaLike).filter_by(media_id=media_id).delete()

        # Eliminar todos los registros relacionados en la tabla FavoriteMedia
        session.query(FavoriteMedia).filter_by(media_id=media_id).delete()

        # Eliminar todos los registros relacionados en la tabla MediaViewed
        session.query(MediaViewed).filter_by(media_id=media_id).delete()

        # Eliminar media
        session.delete(media)
        session.commit()

    return redirect(url_for('admin_panel', _anchor='manage-media'))


''' ADMIN GESTIÓN DE USUARIOS '''


@app.route('/admin/users/ban/<int:user_id>')
@login_required
def ban_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    user = session.query(User).get(user_id)

    # Comprobamos antes que sea un usuario
    if user:
        user.is_banned = True
        session.commit()
        flash('[admin]Usuario bloqueado con éxito.', 'success')
    return redirect(url_for('admin_panel', _anchor='manage-users'))


@app.route('/admin/users/unban/<int:user_id>')
@login_required
def unban_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    user = session.query(User).get(user_id)
    if user:
        user.is_banned = False
        session.commit()
        flash('[admin]Usuario desbloqueado con éxito.', 'success')
    return redirect(url_for('admin_panel', _anchor='manage-users'))


@app.route('/admin/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    user = session.query(User).get(user_id)
    if user:
        session.delete(user)
        session.commit()
    return redirect(url_for('admin_panel', _anchor='manage-users'))


''' FAVORITOS Y LIKES '''


@app.route('/favorites')
@login_required
def favorites():
    """
    Ruta para mostrar solo los favoritos y ver los media que se han marcado como 'favorito'
    """

    user_id = current_user.id

    # Subconsulta para contar la cantidad de likes por película
    like_counts = (
        session.query(MediaLike.media_id, func.count(MediaLike.user_id).label('like_count'))
        .group_by(MediaLike.media_id)
        .subquery()
    )

    # Obtener las películas favoritas del usuario y unir con la subconsulta para obtener la cantidad de likes
    media = (
        session.query(Media)
        .join(FavoriteMedia)
        .outerjoin(like_counts, Media.id == like_counts.c.media_id)
        .filter(FavoriteMedia.user_id == user_id)
        .group_by(Media.id)
        .order_by(
            like_counts.c.like_count.desc(),  # Ordenar por cantidad de likes
            Media.rating.desc()  # Ordenar por calificación en caso de empate
        )
        .all()
    )

    # Obtener los IDs de los media que el usuario ha dado like, favoritas y vistas
    liked_media = {like.media_id for like in session.query(MediaLike).filter_by(user_id=user_id).all()}
    favorite_media = {favorite.media_id for favorite in session.query(FavoriteMedia).filter_by(user_id=user_id).all()}
    viewed_media = {viewed.media_id for viewed in session.query(MediaViewed).filter_by(user_id=user_id).all()}

    return render_template('index.html', media=media, media_likes=liked_media, favorite_media=favorite_media,
                           media_viewed=viewed_media, section_title="Favorites", image_profile=image_profile())


@app.route('/toggle_like', methods=['POST'])
@login_required
def toggle_like():
    """
    Ruta para marca o desmarcar como 'me gusta' los media
    """

    media_id = request.form.get('media_id')
    user_id = current_user.id

    like = session.query(MediaLike).filter_by(user_id=user_id, media_id=media_id).first()

    # Comprobamos si ya está marcado con 'me gusta' en caso contrario lo desactivada es decir quitará el 'me gusta'
    if like:
        session.delete(like)
        session.commit()
    else:
        new_like = MediaLike(user_id=user_id, media_id=media_id)
        session.add(new_like)
        session.commit()

    return redirect(url_for('index'))


@app.route('/toggle_viewed', methods=['POST'])
@login_required
def toggle_viewed():
    """
    Ruta para marca o desmarcar como 'visto' los media
    """

    media_id = request.form.get('media_id')
    user_id = current_user.id

    viewed = session.query(MediaViewed).filter_by(user_id=user_id, media_id=media_id).first()

    # Comprobamos si ya está marcado como 'visto' en caso contrario lo desactivada es decir quitará el 'visto'
    if viewed:
        session.delete(viewed)
        session.commit()
    else:
        new_viewed = MediaViewed(user_id=user_id, media_id=media_id)
        session.add(new_viewed)
        session.commit()

    return redirect(url_for('index'))


@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    """
    Ruta para marca o desmarcar como 'favorito' los media
    """

    media_id = request.form.get('media_id')
    user_id = current_user.id

    favorite = session.query(FavoriteMedia).filter_by(user_id=user_id, media_id=media_id).first()

    # Comprobamos si ya está marcado como 'favorito' en caso contrario lo desactivada es decir quitará el 'favorito'
    if favorite:
        session.delete(favorite)
        session.commit()
    else:
        new_favorite = FavoriteMedia(user_id=user_id, media_id=media_id)
        session.add(new_favorite)
        session.commit()

    return redirect(url_for('index'))


''' BUSCADOR '''


@app.route('/search', methods=['GET'])
@login_required
def search():
    """
    Ruta para mostrar los resultados de la búsqueda de los media
    """

    query = request.args.get('query')
    media_type = request.args.get('type')  # Obtener el tipo (películas o series)

    if not query:
        return redirect(url_for('index'))

    # Normalizar la consulta de búsqueda para facilitar la comparación, ignorando mayúsculas y acentos.
    query_normalized = unidecode(query).lower()

    # Filtrar por tipo de media
    if media_type == 'movie':
        media_query = session.query(Media).filter(Media.type == 'movie').all()
    elif media_type == 'tv':
        media_query = session.query(Media).filter(Media.type == 'tv').all()
    else:
        media_query = session.query(Media).all()

    # Filtrar las medias
    filtered_media = []
    for media in media_query:
        title_normalized = unidecode(media.title).lower()
        categories_normalized = unidecode(media.categories).lower()
        if query_normalized in title_normalized or query_normalized in categories_normalized:
            filtered_media.append(media)

    # Obtener los IDs de las medias que el usuario ha dado like y favoritas
    liked_media = {like.media_id for like in session.query(MediaLike).filter_by(user_id=current_user.id).all()}
    favorite_media = {favorite.media_id for favorite in
                      session.query(FavoriteMedia).filter_by(user_id=current_user.id).all()}

    return render_template('index.html', media=filtered_media, media_likes=liked_media,
                           favorite_media=favorite_media, section_title="Search", image_profile=image_profile())


''' PERFIL DE USUARIO '''


# Función para verificar la extension de fichero de imagen permitida
def allowed_file(filename):
    # Verificamos si el archivo tiene una extensión permitida (jpg, jpeg, png, gif)
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    # Al devolver comprobamos si el nombre del fichero tiene un punto y lo siguiente es la extensión de modo que verificamos si es la extension permitida.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Ruta mostrar el perfil de usuario
    """
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Verificamos y actualizamos la contraseña
        if form.password.data and form.new_password.data:
            if not current_user.check_password(form.password.data):
                flash('[profile]La contraseña actual es incorrecta', 'danger')
                return redirect(url_for('profile'))

            current_user.password = generate_password_hash(form.new_password.data)
            session.commit()
            flash('[profile]Contraseña actualizada con éxito', 'success')

        # Actualizamos el nombre de usuario y el correo electrónico
        if form.username.data:
            current_user.username = form.username.data
        if form.email.data:
            current_user.email = form.email.data

        session.commit()
        flash('[profile]Perfil actualizado con éxito', 'success')
        return redirect(url_for('profile'))
    else:
        # Comprobamos si las nuevas contraseñas coinciden
        if form.new_password.data != form.confirm_new_password.data:
            flash('[profile]Las nuevas contraseñas no coinciden', 'danger')
            return redirect(url_for('profile'))

    # Obtenemos los datos para las gráficas
    total_movies_watched = session.query(func.count(MediaViewed.media_id)).join(Media).filter(
        MediaViewed.user_id == current_user.id,
        Media.type == 'movie'
    ).scalar() or 0  # Podemos 0 en caso de que no hayan resultados

    total_series_watched = session.query(func.count(MediaViewed.media_id)).join(Media).filter(
        MediaViewed.user_id == current_user.id,
        Media.type == 'tv'
    ).scalar() or 0

    total_movie_time = session.query(func.sum(Media.duration)).join(MediaViewed).filter(
        MediaViewed.user_id == current_user.id,
        Media.type == 'movie'
    ).scalar() or 0

    total_series_time = session.query(func.sum(Media.episodes * Media.episode_duration)).join(MediaViewed).filter(
        MediaViewed.user_id == current_user.id,
        Media.type == 'tv'
    ).scalar() or 0

    # Convertimos tiempo total de visualización a horas y minutos
    total_movie_time_hours = total_movie_time // 60
    total_movie_time_minutes = total_movie_time % 60

    total_series_time_hours = total_series_time // 60
    total_series_time_minutes = total_series_time % 60

    # Texto del resumen de las estadísticas
    stats_text = {
        'movies_watched': f"Has visto un total de {total_movies_watched} películas.",
        'series_watched': f"Has visto un total de {total_series_watched} series.",
        'movie_time': f"Tiempo total viendo películas: {total_movie_time_hours} horas y {total_movie_time_minutes} minutos.",
        'series_time': f"Tiempo total viendo series: {total_series_time_hours} horas y {total_series_time_minutes} minutos."
    }

    # Creamos la gráfica
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # Gráfico 1: Número de películas/series vistas
    ax[0].bar(['Películas', 'Series'], [total_movies_watched, total_series_watched], color=['blue', 'green'])
    ax[0].set_xlabel('Tipo')
    ax[0].set_ylabel('Número de películas/series vistas')
    ax[0].set_title('Estadísticas de Visualización')

    # Gráfico 2: Tiempo total empleado
    ax[1].bar(['Películas', 'Series'], [total_movie_time, total_series_time], color=['blue', 'green'])
    ax[1].set_xlabel('Tipo')
    ax[1].set_ylabel('Tiempo Total (minutos)')
    ax[1].set_title('Tiempo Total Empleado')

    # Guardamos la gráfica en buffer
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('profile.html', title='Perfil', form=form,
                           graph=data, stats_text=stats_text, image_profile=image_profile())


@app.route('/upload-profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    """
    Ruta para subir o actualizar la imagen de perfil
    """
    # Verificamos si se ha subido un archivo
    if 'profile_image' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400

    file = request.files['profile_image']

    # Verificamos si el archivo tiene un nombre válido
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Leer el archivo en formato binario
        image_data = file.read()

        # Guardamos la imagen en la base de datos
        user = session.query(User).get(current_user.id)
        user.profile_image = image_data
        session.commit()

        flash('[profile]La imagen ha sido actualizada con éxito', 'success')

        # Convertir la imagen a base64 para mostrar en la vista
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        return jsonify({'success': True, 'new_image_base64': image_base64}), 200

    return jsonify({'success': False, 'message': 'Invalid file'}), 400
