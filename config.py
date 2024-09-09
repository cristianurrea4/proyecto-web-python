import os
from dotenv import load_dotenv

"""
Cargamos las variables de entorno desde el archivo .env, utilizamos este fichero para mantener información sensible
fuera del código fuente y facilitar la gestión de configuraciones en diferentes entornos (desarrollo, producción, etc.).
"""
load_dotenv()


class Config:
    """
    Clase de configuración para la aplicación.
    Esta clase establece las variables de configuración esenciales que la aplicación utilizará durante su ejecución.
    """

    # Clave secreta utilizada por Flask para asegurar sesiones y formularios, hacer estos nos aseguramos de tener protección contra CSRF(Cross-Site-Request-Forgery),
    # es cuando le permite al atacante inducir a los usuarios a realizar acciones que no pretenden realizar, por ejemplo, cambiar su dirección de correo o su contraseña.
    # Si 'SECRET_KEY' no está definida en las variables de entorno, se utiliza 'default_secret_key' como valor predeterminado.
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

    # URI de la base de datos que SQLAlchemy utilizará para establecer la conexión.
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///database/flickflare.db')

    # Clave de la API de IMDB utilizada para realizar solicitudes a los servicios de IMDB.
    IMDB_API_KEY = os.getenv('IMDB_API_KEY', 'bea4627a7e38b438340bc602bef233cb')
