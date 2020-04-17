from flask import Blueprint, render_template, request
from flaskblog.models import Post

main = Blueprint('main',__name__)

@main.route('/home')
@main.route('/')
def home():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2) 
    return render_template('index.html',posts=posts)


@main.route('/about')
def about():
    return render_template('about.html',title='About')