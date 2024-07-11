from flask import Blueprint, render_template,request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from website import db
from website.models import User
from werkzeug.security import generate_password_hash, check_password_hash  #11

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  #both
        email = request.form.get('email')  #both
        password = request.form.get('password')  #both
        #user = User.find_by_email(email)
        user = User.query.filter_by(email=email).first()  #11
        if user:  #11
            if check_password_hash(user.password, password): #11
                login_user(user)
                flash('Logged in successfully!', 'success')  #11
                return redirect(url_for('views.home'))
            else:  #11
                flash("Wrong password!", "error")  #11
        else:  #11
            flash('email does not exist!', 'error')  #11

        # if user and user.check_password(password):
        #     login_user(user)
        #     return redirect(url_for('views.home'))
        # else:
        #     flash('Login failed. Check your email and/or password', 'error')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #user = User.find_by_email(email)
        user = User.query.filter_by(email=email).first() #11

        if user:
            flash('Email address already exists', 'error')
        elif password1 != password2:
            flash('Passwords do not match', 'error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256')) #מהתיקונים

            # new_user = User(email = email, first_name = first_name, password = generate_password_hash(password1, method='sha256')) #11
            db.session.add(new_user) #11
            db.session.commit()   #11
            #new_user = User.create(email, first_name, password1)
            #login_user(new_user)
            return redirect(url_for('views.home')) #both

    return render_template('sign_up.html')
