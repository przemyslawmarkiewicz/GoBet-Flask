from app import app
from flask import render_template, flash, redirect, url_for, session, logging, request
from .models import LoginForm, RegisterForm, WyborKolejki
from passlib.hash import sha256_crypt
from functools import wraps
import time  
import psycopg2


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
          
        login = form.username.data
        haslo_kandydujace = form.password.data

        con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
        cur = con.cursor()

        cur.execute("""SELECT * FROM gobet.uzytkownik WHERE login = %s;""", (login,))
        result = cur.fetchone()

        if result is None:
            flash('Nie ma takiego użytkownika!', 'danger')
            return redirect(url_for('login'))
        else:
            haslo = result[3]
            if sha256_crypt.verify(haslo_kandydujace, haslo) :
                session['logged_in'] = True
                session['username'] = login
                cur.execute("""SELECT * FROM gobet.punkty_uzytkownika(%s);""", (login,))
                res = cur.fetchone()
                punkty = float(res[0])
                session['punkty'] = punkty

                cur.execute("""SELECT * FROM gobet.stan_konta(%s);""", (login,))
                res2 = cur.fetchone()
                stan_konta = res2[0]
                session['stan_konta'] = stan_konta

                
                flash('Zalogowano', 'success')
                return redirect(url_for('terminarz'))
            else:
                flash('Niepoprawne hasło! Spróbuj jeszcze raz', 'danger')
                return redirect(url_for('login'))
    
        con.commit()
        cur.close()
        con.close()

   
    return render_template('login.html', form = form)



@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
        cur = con.cursor()
        cur.execute("SELECT login FROM gobet.uzytkownik WHERE login = %s", (username,))
        result = cur.fetchone() 
        print(result)

        if result is None:
            cur.execute("SELECT gobet.nowy_uzytkownik(%s, %s, %s);", 
            (username, email, password))
            flash('Użytkownik zajejestrowany! Teraz możesz się zalogować', 'success')
            # return redirect(url_for('login')) 
        else:
            flash('Login zajęty. Spróbuj ponownie', 'danger')

        con.commit()
        cur.close()
        con.close() 
        
    return render_template('signup.html', form = form)



#sprawdzam czy uzytkownik jest zalogowany
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            flash('Nieautoryzowany. Zaloguj się', 'danger')
            return redirect(url_for('login'))
    return wrap



#wylogowywanie
@app.route('/logout')
def logout():
    session.clear()
    flash('Wylogowano', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('terminarz.html')


@app.route('/premier_league',  methods = ['GET', 'POST'])
def pl_table():

    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT * FROM gobet.premierleague_table;""")
    teams = cur.fetchall()

    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    kolejka = res[0] - 1
    
    con.commit()
    cur.close()
    con.close()

   
    return render_template('premier_league.html', teams = teams, kolejka = kolejka)


@app.route('/serie_a',  methods = ['GET', 'POST'])
def serie_a():

    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT * FROM gobet.seriea_table;""")
    teams = cur.fetchall()
    
    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    kolejka = res[0] - 1

    con.commit()
    cur.close()
    con.close()

    

    return render_template('serie_a.html', teams = teams, kolejka = kolejka)


@app.route('/la_liga',  methods = ['GET', 'POST'])
def la_liga():

    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT * FROM gobet.laliga_table;""")
    teams = cur.fetchall()

    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    kolejka = res[0] - 1
    
    con.commit()
    cur.close()
    con.close()

    

    return render_template('la_liga.html', teams = teams, kolejka = kolejka)


@app.route('/symuluj_kolejke', methods=['GET', 'POST'])
def symuluj_kolejke():
    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT id_kupon FROM gobet.kupon ORDER BY id_kupon DESC""");
    result = cur.fetchone()
    aktualny_kupon = result[0]
    
    czy_wszedl = True

    cur.execute("""SELECT czy_zakonczony FROM gobet.kupon WHERE id_kupon = %s""", (aktualny_kupon,))
    czy_zakonczony = cur.fetchone()[0]
    
    if czy_zakonczony == False:
        cur.execute("""SELECT id_mecz, typ FROM gobet.kupon_mecz WHERE id_zaklad = %s""", (aktualny_kupon,))
        kupon = cur.fetchall()
        for i in kupon:
            cur.execute("""SELECT gobet.ktora_druzyna_wygrala(%s)""", (i[0],))
            zwyciezca = cur.fetchone()[0]
            if i[1] != zwyciezca:
                czy_wszedl = False
        
        print(czy_wszedl)
        if czy_wszedl == True:
            flash("Gratulacje, twój kupon wygrał!", 'success')
            cur.execute("""SELECT max_wygrana FROM gobet.kupon WHERE id_kupon = %s""", (aktualny_kupon,))
            wygrana = cur.fetchone()[0]
            cur.execute("""UPDATE gobet.uzytkownik SET
            liczba_punktow = liczba_punktow + %s
            WHERE login = %s""", (wygrana,session['username']))
        else:
            flash("Niestety nie udało sie wygrać, spróbuj jeszcze raz", 'warning')
        
    cur.execute("""UPDATE gobet.kupon SET czy_zakonczony = True WHERE id_kupon = %s""", (aktualny_kupon,))
    # r1 = kupon[0][0]
    # print(r1)

    # print(session['username '])


    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    nastepna_kolejka = res[0]


    if nastepna_kolejka >= 6:
        cur.execute("""select gobet.mecze_od_nowa()""")
    else:
        cur.execute("""select gobet.symuluj_kolejke();""")
        if nastepna_kolejka == 5:
            flash("""To była ostatnia kolejka w tym sezonie! Po kliknięciu 'symyluj kolejke' sezon rozpacznie się od nowa""", 'danger')

    con.commit()
    cur.close()
    con.close()

    return redirect(url_for('terminarz'))

@app.route('/terminarz', methods = ['GET', 'POST'])
def terminarz():
    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT * FROM gobet.terminarz(1);""")
    premier_league = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.terminarz(2);""")
    la_liga = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.terminarz(3);""")
    serie_a = cur.fetchall()

    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    nastepna_kolejka = res[0]

    cur.execute("""SELECT liczba_punktow FROM gobet.uzytkownik WHERE login = %s""", (session['username'],))
    liczba_pkt = cur.fetchone()[0]

    cur.execute("""SELECT * FROM gobet.ranking_uzytkownikow""")
    ranking = cur.fetchall()


    
    con.commit()
    cur.close()
    con.close()

    

    return render_template('terminarz.html', premier_league = premier_league, la_liga = la_liga, serie_a = serie_a, nastepna_kolejka = nastepna_kolejka, ranking = ranking, liczba_pkt = liczba_pkt)


@app.route('/wyniki', methods = ['GET', 'POST'])
def wyniki():

    form = WyborKolejki()

    if request.method == 'POST':

        kolejka = int(form.kolejka.data)
        con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
        cur = con.cursor()

        cur.execute("select gobet.nastepna_kolejka();")
        res = cur.fetchone()
        aktualna_kolejka = res[0] -1

        if kolejka > aktualna_kolejka:
            flash('Kolejka nie została jeszcze rozegrana!', 'danger')
        else:

            cur.execute("""SELECT * FROM gobet.pokaz_kolejke(%s, 1);""", (kolejka,))
            premier_league = cur.fetchall()

            cur.execute("""SELECT * FROM gobet.pokaz_kolejke(%s, 2);""", (kolejka,))
            la_liga = cur.fetchall()

            cur.execute("""SELECT * FROM gobet.pokaz_kolejke(%s, 3);""", (kolejka,))
            serie_a = cur.fetchall()

            return render_template('wyniki.html', form = form, premier_league = premier_league, la_liga = la_liga, serie_a = serie_a, kolejka = kolejka)
        
        con.commit()
        cur.close()
        con.close()

        

    return render_template('wyniki.html', form = form)


@app.route('/kupon',methods = ['GET', 'POST'])
def nowy_kupon():
    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(1);""")
    premier_league = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(2);""")
    la_liga = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(3);""")
    serie_a = cur.fetchall()

    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    nastepna_kolejka = res[0]

    cur.execute("""INSERT INTO gobet.kupon VALUES(DEFAULT, gobet.id_uzytkownika(%s), 0, 0, 10, false)""", (session['username'],))

    cur.execute("""SELECT id_kupon FROM gobet.kupon ORDER BY id_kupon DESC""");
    result = cur.fetchone()
    aktualny_kupon = result[0]
    print(aktualny_kupon)

    cur.execute("""SELECT liczba_punktow FROM gobet.uzytkownik WHERE login = %s""", (session['username'],))
    liczba_pkt = cur.fetchone()[0]

    con.commit()
    cur.close()
    con.close()


    return render_template('kupon.html', premier_league = premier_league, la_liga = la_liga, serie_a = serie_a, nastepna_kolejka = nastepna_kolejka, liczba_pkt = liczba_pkt)


@app.route('/dodaj_mecz', methods = ['GET', 'POST'])
def dodaj_mecz():
    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(1);""")
    premier_league = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(2);""")
    la_liga = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(3);""")
    serie_a = cur.fetchall()

    cur.execute("select gobet.nastepna_kolejka();")
    res = cur.fetchone()
    nastepna_kolejka = res[0]

    cur.execute("""SELECT id_kupon FROM gobet.kupon ORDER BY id_kupon DESC""");
    result = cur.fetchone()
    aktualny_kupon = result[0]
    print("kupon")
    print(aktualny_kupon)
    meczid = request.form['meczid']
    typ = request.form['typ']
    print("typ")
    print(typ)
    print("meczid")
    print(meczid)

    cur.execute("""SELECT liczba_punktow FROM gobet.uzytkownik WHERE login = %s""", (session['username'],))
    liczba_pkt = cur.fetchone()[0]


    cur.execute("""SELECT id_zaklad, id_mecz FROM gobet.kupon_mecz WHERE id_zaklad = %s AND id_mecz = %s""", (aktualny_kupon, meczid))
    wynik = cur.fetchone()
    print("wynik")
    print(wynik)

    if wynik is None:
        cur.execute("""INSERT INTO gobet.kupon_mecz VALUES(%s, %s, %s)""", (aktualny_kupon, meczid, typ))
        cur.execute("""SELECT * FROM gobet.pokaz_aktualny_kupon(%s)""", (aktualny_kupon,))
        kupon = cur.fetchall()

        if typ == '1':
            cur.execute("""SELECT gobet.kurs_typ1(%s)""", (meczid,))
            kurs = cur.fetchone()[0]
            cur.execute("""UPDATE  gobet.kupon  
            SET max_wygrana = max_wygrana + stawka * %s
            WHERE id_kupon = %s""", (kurs, aktualny_kupon))
            print("KUUUUURS DODAW")
            print(kurs)
        elif typ == '2':
            cur.execute("""SELECT gobet.kurs_typ2(%s)""", (meczid,))
            kurs = cur.fetchone()[0]
            cur.execute("""UPDATE  gobet.kupon  
            SET max_wygrana = max_wygrana + stawka * %s
            WHERE id_kupon = %s""", (kurs, aktualny_kupon))
        else:
            cur.execute("""SELECT gobet.kurs_typ0(%s)""", (meczid,))
            kurs = cur.fetchone()[0]
            cur.execute("""UPDATE  gobet.kupon  
            SET max_wygrana = max_wygrana + stawka * %s
            WHERE id_kupon = %s""", (kurs, aktualny_kupon))

        cur.execute("""SELECT max_wygrana from gobet.kupon WHERE id_kupon =%s """, (aktualny_kupon,))
        temp = cur.fetchone()
        max_wygrana= temp[0]
        con.commit()
        cur.close()
        con.close()
        return render_template('kupon.html', premier_league = premier_league, la_liga = la_liga, serie_a = serie_a, nastepna_kolejka = nastepna_kolejka, kupon = kupon, meczid = meczid, typ=typ, max_wygrana = max_wygrana, liczba_pkt = liczba_pkt)
    else:
        flash('Nie można dodać dwa razy tego samego meczu do kuponu!', 'danger')
        cur.execute("""SELECT * FROM gobet.pokaz_aktualny_kupon(%s)""", (aktualny_kupon,))
        kupon = cur.fetchall()
        print(kupon)
        cur.execute("""SELECT max_wygrana from gobet.kupon WHERE id_kupon =%s """, (aktualny_kupon,))
        temp = cur.fetchone()
        max_wygrana= temp[0]
        return render_template('kupon.html', premier_league = premier_league, la_liga = la_liga, serie_a = serie_a, nastepna_kolejka = nastepna_kolejka, kupon = kupon,  max_wygrana = max_wygrana, liczba_pkt = liczba_pkt)
        con.commit()
        cur.close()
        con.close()

@app.route('/usun_mecz/<int:mecz_id>', methods = ['GET', 'POST'])
def usun_mecz(mecz_id):

    con = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", password="przemek", port = "5433")
    cur = con.cursor()
    cur.execute("""SELECT id_kupon FROM gobet.kupon ORDER BY id_kupon DESC""");
    result = cur.fetchone()
    aktualny_kupon = result[0]

    cur.execute("""SELECT liczba_punktow FROM gobet.uzytkownik WHERE login = %s""", (session['username'],))
    liczba_pkt = cur.fetchone()[0]


    cur.execute("""SELECT gobet.typ(%s, %s);""", (mecz_id, aktualny_kupon))
    typ = cur.fetchone()[0]
    
    cur.execute("""DELETE FROM gobet.kupon_mecz WHERE id_mecz = %s AND id_zaklad = %s""", (mecz_id, aktualny_kupon))

    if typ == 1:
        cur.execute("""SELECT gobet.kurs_typ1(%s)""", (mecz_id,))
        kurs = cur.fetchone()[0]
        cur.execute("""UPDATE  gobet.kupon  
        SET max_wygrana = max_wygrana - stawka * %s
        WHERE id_kupon = %s""", (kurs, aktualny_kupon))
        print("KUUUUURS ODeJ")
        print(kurs)
    elif typ == 2:
        cur.execute("""SELECT gobet.kurs_typ2(%s)""", (mecz_id,))
        kurs = cur.fetchone()[0]
        cur.execute("""UPDATE  gobet.kupon  
        SET max_wygrana = max_wygrana - stawka * %s
        WHERE id_kupon = %s""", (kurs, aktualny_kupon))
    else:
        cur.execute("""SELECT gobet.kurs_typ0(%s)""", (mecz_id,))
        kurs = cur.fetchone()[0]
        cur.execute("""UPDATE  gobet.kupon  
        SET max_wygrana = max_wygrana - stawka * %s
        WHERE id_kupon = %s""", (kurs, aktualny_kupon))

    cur.execute("""SELECT max_wygrana from gobet.kupon WHERE id_kupon =%s """, (aktualny_kupon,))
    temp = cur.fetchone()
    max_wygrana= temp[0]

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(1);""")
    premier_league = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(2);""")
    la_liga = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.kursy_kolejki(3);""")
    serie_a = cur.fetchall()

    cur.execute("""SELECT * FROM gobet.pokaz_aktualny_kupon(%s)""", (aktualny_kupon,))
    kupon = cur.fetchall()

    con.commit()
    cur.close()
    con.close()

    return render_template('kupon.html', premier_league = premier_league, la_liga = la_liga, serie_a = serie_a, kupon = kupon, max_wygrana=max_wygrana, liczba_pkt = liczba_pkt)

@app.route('/pilkarze', methods = ['GET', 'POST'])
def pilkarze():
    return render_template('pilkarze.html')