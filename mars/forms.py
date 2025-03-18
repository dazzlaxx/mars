from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ApplicationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    nationality = StringField('Национальность', validators=[DataRequired()])
    university = StringField('Университет', validators=[DataRequired()])
    education = StringField('Образование', validators=[DataRequired()])
    experience = StringField('Опыт работы', validators=[DataRequired()])
    skills = StringField('Навыки', validators=[DataRequired()])
    certifications = StringField('Сертификаты')
    motivation = TextAreaField('Мотивация', validators=[DataRequired()])
    submit = SubmitField('Отправить заявку')

