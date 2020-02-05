from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Email, Length, EqualTo
import psycopg2
from wtforms import StringField, PasswordField, BooleanField, validators, TextAreaField, SelectField



class LoginForm(FlaskForm):
    username = StringField('nazwa użytkownika', validators = [InputRequired(message = "Wprowadź nazwę użytkoanika"), Length(min = 5, max = 15)])
    password = PasswordField('hasło', validators = [InputRequired(), Length(min = 5, max = 30)])
    remember = BooleanField('zapamiętaj mnie')

        


class RegisterForm(FlaskForm):
    email = StringField('adres e-mail', validators = [InputRequired(message = 'Wpisz nazwę użytkownika'), Email(message = 'Nieprawidłowy adres e-mail'), Length(max = 50)])
    username = StringField('nazwa użytkownika', validators = [InputRequired(), Length(min = 5, max = 15, message = 'Nazwa użytkownika musi zawierać od 5 do 15 znaków')])
    password = PasswordField('hasło', validators = [InputRequired(message="Wpisz hasło"), EqualTo('confirm', message='Hasła nie są takie same!  '), Length(min = 5, max = 30, message= 'Hasło powinno zawierać od 5 do 30 znaków')])
    confirm = PasswordField('Potwierdż hasło')


class WyborKolejki(FlaskForm):
    kolejka = SelectField('Wybierz kolejkę', choices=[('1', 'kolejka 1'), ('2', 'kolejka 2'), ('3', 'kolejka 3'), ('4', 'kolejka 4'), ('5', 'kolejka 5')])