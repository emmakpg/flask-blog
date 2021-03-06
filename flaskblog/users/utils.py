from flask import render_template, request, url_for,flash
from flaskblog import db, bcrypt, mail
from PIL import Image
from flask_mail import Message
from flaskblog.models import User,Post
from flask import current_app
import os
import secrets


def savepicture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
    
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',recipients=[user.email])
    msg.body = f'''To reset your password use the following link:
    {url_for('users.reset_token',token=token,_external=True)}

    If you did not make this request then simply ignore this change and no changes will be made.''' 
    try:
        mail.send(msg)
    except:
        flash('Email not sent.','danger')
       