from flask import Flask
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User

# Creamos el servidor web.
app = Flask(__name__)

# Cargamos la configuración desde el archivo de configuración.
app.config.from_object('config.Config')

# Configuramos la base de datos
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

# Crear todas las tablas definidas en los modelos.
Base.metadata.create_all(engine)

# Crear un administrador por defecto si no existe en la base de datos.
admin = session.query(User).filter_by(username='admin').first()
if not admin:
    admin = User(username='admin', email='admin@flickflare.com', password='!adminpassword%', is_admin=True)
    session.add(admin)
    session.commit()

# Configuración del administrador.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app.models import User, Media

# Importamos las rutas de la aplicación después de la configuración inicial.
from app import routes
