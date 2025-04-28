# app/routes/blog.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response, session
from app import db
from app.forms import PostForm
from app.models import Post, User, Favorite
from app.routes.auth import login_required
from werkzeug.utils import secure_filename
import uuid
import mimetypes
import logging

logging.basicConfig(level=logging.DEBUG)

blog_bp = Blueprint('blog', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@blog_bp.route('/')
def index():
    search = request.args.get('search')
    if search:
        posts = Post.query.join(User).filter(
            (Post.title.contains(search)) | (Post.content.contains(search)) | (User.username.contains(search))
        ).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()

    # Get favorited post IDs for the current user (if logged in)
    favorited_posts = set()
    if session.get('user_id'):
        user_favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
        favorited_posts = {fav.post_id for fav in user_favorites}

    return render_template('index.html', posts=posts, favorited_posts=favorited_posts)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_filename = None
        image_data = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            image_filename = f"{uuid.uuid4().hex}_{filename}"
            image_data = form.image.data.read()
            logging.debug(f"Image uploaded: filename={image_filename}, size={len(image_data)} bytes")
        else:
            logging.debug("No image uploaded or invalid file type")

        post = Post(
            title=form.title.data,
            content=form.content.data,
            image=image_filename,
            image_data=image_data,
            user_id=session['user_id']
        )<
        db.session.add(post)
        db.session.commit()
        logging.debug(f"Post created: id={post.id}, image_filename={post.image}")
        flash('Post created successfully!', 'success')
        return redirect(url_for('blog.index'))
    return render_template('create_post.html', form=form)


@blog_bp.route('/post/<int:id>')
def view_post(id):
    post = Post.query.get_or_404(id)
    # Check if the post is favorited by the current user
    is_favorited = False
    if session.get('user_id'):
        favorite = Favorite.query.filter_by(user_id=session['user_id'], post_id=post.id).first()
        is_favorited = bool(favorite)
    return render_template('post.html', post=post, is_favorited=is_favorited)


@blog_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != session['user_id']:
        flash('You can only edit your own posts.', 'danger')
        return redirect(url_for('blog.index'))

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            image_filename = f"{uuid.uuid4().hex}_{filename}"
            image_data = form.image.data.read()
            post.image = image_filename
            post.image_data = image_data
            logging.debug(f"Image updated for post {post.id}: filename={image_filename}, size={len(image_data)} bytes")
        else:
            logging.debug(f"No new image uploaded for post {post.id}")
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.view_post', id=post.id))

    form.title.data = post.title
    form.content.data = post.content
    return render_template('edit_post.html', form=form, post=post)


@blog_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != session['user_id']:
        flash('You can only delete your own posts.', 'danger')
        return redirect(url_for('blog.index'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('blog.index'))


@blog_bp.route('/image/<int:post_id>')
def serve_image(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.image_data:
        logging.debug(f"No image data found for post {post_id}")
        return Response(status=404)

    mime_type, _ = mimetypes.guess_type(post.image)
    if not mime_type:
        extension = post.image.rsplit('.', 1)[1].lower() if '.' in post.image else ''
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif'
        }
        mime_type = mime_types.get(extension, 'application/octet-stream')

    logging.debug(f"Serving image for post {post_id}: filename={post.image}, mime_type={mime_type}")
    return Response(post.image_data, mimetype=mime_type)


@blog_bp.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(session['user_id'])
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    favorite_posts = Post.query.join(Favorite).filter(Favorite.user_id == user.id).order_by(
        Favorite.created_at.desc()).all()
    return render_template('profile.html', user=user, user_posts=user_posts, favorite_posts=favorite_posts)


@blog_bp.route('/favorite/<int:post_id>', methods=['POST'])
@login_required
def toggle_favorite(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session['user_id']
    favorite = Favorite.query.filter_by(user_id=user_id, post_id=post_id).first()

    if favorite:
        # Remove from favorites
        db.session.delete(favorite)
        flash('Post removed from favorites.', 'info')
    else:
        # Add to favorites
        favorite = Favorite(user_id=user_id, post_id=post_id)
        db.session.add(favorite)
        flash('Post added to favorites!', 'success')

    db.session.commit()

    # Redirect back to the previous page
    next_page = request.referrer or url_for('blog.index')
    return redirect(next_page)