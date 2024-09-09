from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import InputRequired, DataRequired, Email, Length, EqualTo, Optional
from app.models import User
from app import session


class LoginForm(FlaskForm):
    """Formulario para iniciar sesión en la aplicación."""
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')


class RegistrationForm(FlaskForm):
    """Formulario para registrar una nueva cuenta de usuario."""
    username = StringField('Nombre de Usuario', [InputRequired(), Length(min=1, max=25)])
    email = StringField('Correo Electrónico', [InputRequired(), Email()])
    password = PasswordField('Contraseña', [InputRequired(), Length(min=1, max=35)])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     [InputRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        """Validar que el nombre de usuario no esté ya en uso."""
        user = session.query(User).filter_by(username=username.data).first()
        if user:
            raise ValidationError('El nombre de usuario ya está en uso.')

    def validate_email(self, email):
        """Valida que el correo electrónico no esté ya en uso."""
        user = session.query(User).filter_by(email=email.data).first()
        if user:
            raise ValidationError('El correo electrónico ya está en uso.')


class ProfileForm(FlaskForm):
    """Formulario para actualizar el perfil de usuario."""
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña actual', validators=[Optional()])
    new_password = PasswordField('Nueva contraseña', validators=[Optional()])
    confirm_new_password = PasswordField('Confirmar nueva contraseña', validators=[
        Optional(), EqualTo('new_password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Guardar Cambios')
