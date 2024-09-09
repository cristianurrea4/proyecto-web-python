from sqlalchemy import Column, Integer, Float, String, Text, Boolean, ForeignKey, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

Base = declarative_base()


# Modelo para Usuario
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Integer, default=False)
    is_banned = Column(Boolean, default=False)
    profile_image = Column(LargeBinary, nullable=True)  # Almacenamiento de la imagen en formato binario

    # Relación con las películas que el usuario ha dado "me gusta"
    liked_media = relationship('MediaLike', back_populates='user')
    # Relación con las películas que el usuario ha visto
    viewed_media = relationship('MediaViewed', back_populates='user')
    # Relación con las películas que el usuario ha marcado como favorito
    favorite_media = relationship('FavoriteMedia', back_populates='user')

    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)  # Genera el hash aquí
        self.is_admin = is_admin

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Modelo para Películas
class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    image_url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    release_date = Column(String, nullable=False)
    producer = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    duration = Column(Integer, nullable=True)
    seasons = Column(Integer, nullable=True)
    episodes = Column(Integer, nullable=True)
    episode_duration = Column(Integer, nullable=True)
    categories = Column(String, nullable=True)
    added_date = Column(DateTime, default=datetime.utcnow)

    # Relación con los usuarios que les han dado "me gusta"
    likes = relationship('MediaLike', back_populates='media')
    # Relación con los usuarios que han visto esta película
    viewed = relationship('MediaViewed', back_populates='media')
    # Relación con los usuarios que han marcado esta película como favorita
    favorites = relationship('FavoriteMedia', back_populates='media')


# Modelo para las películas que un usuario ha dado "me gusta"
class MediaLike(Base):
    __tablename__ = 'media_likes'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    media_id = Column(Integer, ForeignKey('media.id'), primary_key=True)

    user = relationship('User', back_populates='liked_media')
    media = relationship('Media', back_populates='likes')


# Modelo para las películas que un usuario ha visto
class MediaViewed(Base):
    __tablename__ = 'media_viewed'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    media_id = Column(Integer, ForeignKey('media.id'), primary_key=True)

    user = relationship('User', back_populates='viewed_media')
    media = relationship('Media', back_populates='viewed')


# Modelo para las películas que un usuario ha marcado como favorito
class FavoriteMedia(Base):
    __tablename__ = 'favorite_media'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    media_id = Column(Integer, ForeignKey('media.id'), primary_key=True)

    user = relationship('User', back_populates='favorite_media')
    media = relationship('Media', back_populates='favorites')
