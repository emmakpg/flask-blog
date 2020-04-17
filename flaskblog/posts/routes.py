from flask import Blueprint, render_template, request,redirect, url_for, flash, abort
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm, UpdatePostForm
from flask_login import  current_user, login_required
from flaskblog import db,mail


posts = Blueprint('posts',__name__)

@posts.route('/newpost',methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form)


@posts.route('/post-<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@posts.route('/editpost-<int:post_id>',methods=['GET','POST'])
def editpost(post_id):
    form = UpdatePostForm()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
         abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post has been updated successfully!','success')
        return redirect(url_for('posts.post',post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Update Post', post=post,form=form)

@posts.route('/delete_post-<int:post_id>')
@login_required
def deletepost(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
         abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!','success')
    return redirect(url_for('main.home'))

