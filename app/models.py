from flask import render_template, Flask
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Email, Length
import psycopg2
from wtforms import StringField, PasswordField, BooleanField


class LoginForm(FlaskForm):
    username = StringField('nazwa użytkownika', validators = [InputRequired(), Length(min = 4, max = 15)])
    password = PasswordField('hasło', validators = [InputRequired(), Length(min = 8, max = 80)])
    remember = BooleanField('zapamiętaj mnie')


class RegisterForm(FlaskForm):
    email = StringField('adres e-mail', validators = [InputRequired(), Email(message = 'Nieprawidłowy adres e-mail'), Length(max = 50)])
    username = StringField('nazwa użytkownika', validators = [InputRequired(), Length(min = 4, max = 15)])
    password = PasswordField('hasło', validators = [InputRequired(), Length(min = 8, max = 80)])

    def add_user(self):
        con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5432")
        cur = con.cursor()
        # cur.execute("""INSERT INTO gobet.liga VALUES (%s, %s);""", 
        # (4, 'Ekstraklasa'))
        con.commit()
        cur.close()
        con.close()