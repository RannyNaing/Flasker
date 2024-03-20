from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import Posts
from webforms import PostForm
from models import db, Posts


blog_posts = Blueprint('blog_posts', __name__)


# Blog Posts Pge
@blog_posts.route('/posts')
def posts():
	order = request.args.get('order', 'asc')
	if order == 'desc':
		posts = Posts.query.order_by(Posts.date_posted.desc())
	else:
		posts = Posts.query.order_by(Posts.date_posted.asc())
	return render_template("posts.html", posts=posts, order=order)

# Individual Blog Post
@blog_posts.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post = post)

#Add Post Page
@blog_posts.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(title= form.title.data,
			content = form.content.data,
			poster_id = poster,
			slug = form.slug.data)
		form.title.data = ''
		form.content.data = ''
		form.slug.data = ''
		# Add data to database
		db.session.add(post)
		db.session.commit()
		#Return a Message
		flash("Blog Post Submitted Successfully")
	# Redirect to the webpae
	return render_template("add_post.html", form = form)

# Editting Post
@blog_posts.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		# post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated")
		return redirect(url_for('blog_posts.post', id = post.id))
	if current_user.id == post.poster_id or current_user.id == 1:
		form.title.data = post.title
		# form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form = form)
	else:
		flash("You Aren't Authorzed to Edit This Post")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)

# Delete Post
@blog_posts.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if post_to_delete.poster is None or id == post_to_delete.poster.id or id == 1:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()
			#Return Message
			flash("Blog Post was DELETED")
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts = posts)
		except:
			# Return Error message
			flash("There was a problem deleting post. Try again....")
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts = posts)
	else:
		flash("You are not authorized to Delete That Post. Try again....")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
