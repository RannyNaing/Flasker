from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, UserForm, PostForm, NamerForm, PasswordForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os



#Create an instance of Flask
app = Flask(__name__)
# CK Editor
ckeditor = CKEditor(app)
# Add database

# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

# MYSQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@localhost/db_name"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost/our_users"

# Heroku Postgressql
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://exxzdfhdskiddh:f75c935919f02f071192e38961ecd83368ec508a8533cd214ee37bd3680c50a1@ec2-44-220-7-157.compute-1.amazonaws.com:5432/d261tl97dqem1o"

# Secret Key!!
app.config['SECRET_KEY'] = "super_secret_key"

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()


# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))



# ----------------------------------------------------------------------------------------
# Home Page
# Create a route decorator
@app.route('/')
def index():
	return render_template("index.html")

#################################


# ---------------------------------------------------------

# Simple API to get posts and add a new post
@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        # Assume JSON data contains 'title' and 'content'
        data = request.json
        new_post = Posts(title=data['title'], content=data['content'], poster_id=current_user.id)  # Simplified example
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'message': 'Post created', 'post': {'title': data['title'], 'content': data['content']}}), 201

    posts = Posts.query.all()
    posts_data = [{'title': post.title, 'content': post.content} for post in posts]
    return jsonify(posts_data)

# ------------------------------------------------------------
# Posts

#Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
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
		# form.author.data = ''
		form.slug.data = ''

		# Add data to database

		db.session.add(post)
		db.session.commit()

		#Return a Message
		flash("Blog Post Submitted Successfully")

	# Redirect to the webpae
	return render_template("add_post.html", form = form)

# Blog Posts Pge
@app.route('/posts')
def posts():
	# Grab all the posts from database
	posts = Posts.query.order_by(Posts.date_posted)

	return render_template("posts.html", posts = posts)

# Individual Blog Post
@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post = post)

# Editting Post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
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
		return redirect(url_for('post', id = post.id))
	if current_user.id == post.poster_id or id == 1:
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
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if id == post_to_delete.poster.id or id == 1:
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

# ------------------------------------------------------------
##########################################
# -----------------------------------------------------------------------
# localhost:5000/user/
@app.route('/user/<name>')
def user(name):
	return render_template("user.html", user_name = name)
###################################
# ----------------------------------------------------------------------

# Create Custom Error Page

#Invalid Error
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
	return render_template("500.html"), 500

# ----------------------------------------------------------------------------
#########################
# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully")


	return render_template('name.html', 
		name = name, 
		form = form)
##################################
# -------------------------------------------------------------------------------------

# Update Database Record of the User
@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']
		
		# Check for profile pic
		if request.files['profile_pic']:
			name_to_update.profile_pic = request.files['profile_pic']

			# Grab Image Name
			pic_filename = secure_filename(name_to_update.profile_pic.filename)
			# Set UUID
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			# Save That Image
			saver = request.files['profile_pic']
			

			# Change it to a string to save to db
			name_to_update.profile_pic = pic_name
			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("User Updated Successfully!")
				return render_template("update.html", 
					form=form,
					name_to_update = name_to_update)
			except:
				flash("Error!  Looks like there was a problem...try again!")
				return render_template("update.html", 
					form=form,
					name_to_update = name_to_update)
		else:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("update.html", 
				form=form, 
				name_to_update = name_to_update)
	else:
		return render_template("update.html", 
				form=form,
				name_to_update = name_to_update,
				id = id)

	return render_template('update.html')


# ------------------------------------------------------------------------------------------

# Add User
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			#Hash password
			hashed_pw = generate_password_hash(form.password_hash.data)
			user = Users(name = form.name.data, username= form.username.data, email = form.email.data, favorite_color= form.favorite_color.data, password_hash = hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data=''
		form.username.data=''
		form.email.data=''
		form.favorite_color.data=''
		form.password_hash.data = ''
		flash("User added Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form=form, name=name, our_users = our_users)


# -------------------------------------------------------------------------------

# Delete Users
@app.route('/delete/<int:id>')
@login_required
def delete(id):
	if id == current_user.id:
		user_to_delete = Users.query.get_or_404(id)
		name = None
		form = UserForm()
		try:
			db.session.delete(user_to_delete)
			db.session.commit()
			flash("User Deleted Successfully")
			our_users = Users.query.order_by(Users.date_added)
			return render_template("add_user.html", form=form, name=name, our_users = our_users)
		except:
			flash("Whoops!!! There was a problem deleting the user")
			return render_template("add_user.html", form=form, name=name, our_users = our_users)
	else:
		flash("Sorry, You can't delete that user!")
		return redirect(url_for('dashboard'))

# --------------------------------------------

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear the form
		form.email.data = ''
		form.password_hash.data = ''
		# flash("Form Submitted Successfully")

		# Look up User by Email address
		pw_to_check = Users.query.filter_by(email=email).first()

		# Check hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)


	return render_template('test_pw.html', 
		email = email, 
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)



# -------------------------------------------------------------------


# Create a Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Successfully")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password - Try Again!")
		else:
			flash("That User Does not Exist!!! Please Try Again.")

	return render_template('login.html', form=form)


# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']
		
		# Check for profile pic
		if request.files['profile_pic']:
			name_to_update.profile_pic = request.files['profile_pic']

			# Grab Image Name
			pic_filename = secure_filename(name_to_update.profile_pic.filename)
			# Set UUID
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			# Save That Image
			saver = request.files['profile_pic']
			

			# Change it to a string to save to db
			name_to_update.profile_pic = pic_name
			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("User Updated Successfully!")
				return render_template("dashboard.html", 
					form=form,
					name_to_update = name_to_update)
			except:
				flash("Error!  Looks like there was a problem...try again!")
				return render_template("dashboard.html", 
					form=form,
					name_to_update = name_to_update)
		else:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("dashboard.html", 
				form=form, 
				name_to_update = name_to_update)
	else:
		return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update,
				id = id)

	return render_template('dashboard.html')

# Create Logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You have been Logged Out! Thanks for stopping by")
	return redirect(url_for('login'))


# --------------------------------------------------------------

#Pass Stuff to NavBar

@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)


#Create Search Function

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        # Using case-insensitive search across title and content fields
        posts = Posts.query.filter(db.or_(
            Posts.title.ilike(f'%{searched}%'),
            Posts.content.ilike(f'%{searched}%')
        )).order_by(Posts.date_posted.desc()).all()

        return render_template('search.html',
            form=form,
            searched=searched,
            posts=posts)


# -----------------------------------------------------

# Create Admin Page

# Create a route decorator
@app.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 1:
		return render_template("admin.html")
	else:
		flash("Sorry must be admin to access the Admin page")
		return redirect(url_for('dashboard'))

# --------------------------------------------------------------
# Models

# Create a Blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(225))
	content = db.Column(db.Text)
	# author = db.Column(db.String(55))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(55))
	# Foreign Key to Link Users (refer to primary key of the user)
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Create Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable = False)
	email = db.Column(db.String(200), nullable= False, unique = True)
	favorite_color = db.Column(db.String(120))
	about_author = db.Column(db.Text(), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(255), nullable=True)
	# Do some password stuff
	password_hash = db.Column(db.String(500))
	# User Can Have Many Posts
	posts = db.relationship('Posts', backref='poster')



	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<Name %r>' % self.name