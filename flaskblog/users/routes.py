from flask import Blueprint, render_template, request,redirect, url_for, flash
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, LoginForm
from flask_login import login_user, current_user,logout_user, login_required
from flaskblog import db, bcrypt,mail
from flaskblog.users.utils import savepicture,send_reset_email
from flask import current_app

users = Blueprint('users',__name__)




@users.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now login','success')
        return redirect(url_for('users.login'))
    return render_template('register.html',title='Register',form=form)

@users.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home')) 
        else:
            flash('Unsuccessful. Kindly enter correct email and password','danger')
    return render_template('login.html',title='Login',form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))

@users.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = savepicture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account has been updated','success')
        return redirect(url_for('users.account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file,form=form)

@users.route('/<string:username>')
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).\
            order_by(Post.date_posted.desc()).\
            paginate(page=page, per_page=2) 
    return render_template('user_posts.html',posts=posts, user=user)

@users.route('/password_reset',methods =['GET','POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.','info')
        return redirect(url_for('main.home'))
    return render_template('request_reset.html',title='Request Password Reset',form=form)
 
@users.route('/password_reset/<token>',methods =['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This token is invalid or expired!','warning')
        return redirect(url_for('users.request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password has been updated! You can now login','success')
        return redirect(url_for('users.users.login'))
    return render_template('password_reset.html',title='Request Password Reset',form=form) 