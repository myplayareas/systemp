from msr import app
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from msr.dao import Repository, User
from msr.forms import RegisterForm, LoginForm
from msr.main import usersCollection

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('authenticate/home.html')

@app.route('/msr')
@login_required
def msr_page():
    repositories = Repository.query.filter_by(owner=current_user.get_id()).all()
    return render_template('user/msr.html', repositories=repositories)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        usersCollection.insert_user(user_to_create)
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('msr_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('authenticate/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('msr_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('authenticate/login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))