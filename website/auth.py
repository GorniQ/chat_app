from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Ban
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            user_bans = Ban.query.filter_by(user_id=user.id).all()

            if user_bans:
                flash('This account has been banned!', category='error')
            elif check_password_hash(user.password, password):
                flash('Logged in successfuly!', category='success')
                login_user_with_online_status(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email doesn\'t exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user_with_online_status(current_user)
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        isCorrect = check_data(user, email, first_name,
                               last_name, password1, password2)
        if isCorrect:
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='sha256'), is_moderator=False, last_seen=datetime.now())
            db.session.add(new_user)
            db.session.commit()
            # Update user online status
            login_user_with_online_status(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)


def check_data(user, email, first_name, last_name, password1, password2):
    specialSym = ['!', '$', '@', '#', '%']
    if user:
        flash("Email already exists.", category='error')

    if len(email) < 4:
        flash('Email must be greater than 3 characters', category='error')
    elif len(first_name) < 2:
        flash('Name must be greater than 1 character', category='error')
    elif len(last_name) < 2:
        flash('Name must be greater than 1 character', category='error')
    elif password1 != password2:
        # TODO: sprawdzenie poprawności hasła wg założeń z scenariuszy
        flash('passwords don\'t match', category='error')
    elif len(password1) < 7:
        flash('Password must be greater than 7 characters', category='error')
    elif not any(char.isdigit() for char in password1):
        flash('Password should have at least one numeral', category='error')
    elif not any(char.isupper() for char in password1):
        flash('Password should have at least one uppercase letter', category='error')
    elif not any(char.islower() for char in password1):
        flash('Password should have at least one lowercase letter', category='error')
    elif not any(char in specialSym for char in password1):
        flash('Password should have at least one of the symbols $@#', category='error')
    else:
        return True
    return False


def update_user_online_status(user, is_online):
    user.is_online = is_online
    db.session.add(user)
    db.session.commit()


def login_user_with_online_status(user, remember=False):
    login_user(user, remember=remember)
    update_user_online_status(user, True)


def logout_user_with_online_status(user):
    update_user_online_status(user, False)
    logout_user()
