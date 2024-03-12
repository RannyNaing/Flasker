from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

#Create an instance of Flask
app = Flask(__name__)
# Add database


# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

# MYSQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@localhost/db_name"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost/our_users"

# Secret Key!!
app.config['SECRET_KEY'] = "super_secret_key"

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()



# ---------------------------------------------------------
# Create a Blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(225))
	content = db.Column(db.Text)
	author = db.Column(db.String(55))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(55))


# Create a Post Form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = TextAreaField("Content", validators=[DataRequired()])
	author =StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField()

#Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title= form.title.data,
			content = form.content.data,
			author = form.author.data,
			slug = form.slug.data)
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
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
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated")
		return redirect(url_for('post', id = post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content
	return render_template('edit_post.html', form = form)

# Delete Post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)

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

# ------------------------------------------------------------

# JSON Thing
@app.route('/date')
def get_current_data():
	favorite_pizza = {
		"John":"Pepperoni",
		"Mary":"Cheese",
		"Tim": "Mushrooms"
	}
	return favorite_pizza
	return {"Date": date.today()}

# ---------------------------------------------------------------------------------------

# Create Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable = False)
	email = db.Column(db.String(200), nullable= False, unique = True)
	favorite_color = db.Column(db.String(120))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	# Do some password stuff
	password_hash = db.Column(db.String(500))


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


# Create a Form Class
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match')])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField('Submit')


# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's your name", validators=[DataRequired()])
	submit = SubmitField('Submit')

# Create a Passowrd Form Class
class PasswordForm(FlaskForm):
	email = StringField("What's your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's your Password", validators=[DataRequired()])
	submit = SubmitField('Submit')


# ------------------------------------------------------------------------------------------

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			#Hash password
			hashed_pw = generate_password_hash(form.password_hash.data)
			user = Users(name = form.name.data, email = form.email.data, favorite_color= form.favorite_color.data, password_hash = hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data=''
		form.email.data=''
		form.favorite_color.data=''
		form.password_hash.data = ''
		flash("User added Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form=form, name=name, our_users = our_users)



# ----------------------------------------------------------------------------------------

# Create a route decorator
@app.route('/')
# def index():
# 	return "<h1>Hello World</h1>"
# Filters
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags
def index():

	first_name = "John"
	stuff = "This is bold Text"

	favorite_pizza =["Pepperoni", "Cheese", "Mushrooms", 41]
	return render_template("index.html", first_name = first_name,
		stuff = stuff,
		favorite_pizza = favorite_pizza)
# -----------------------------------------------------------------------
# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
	return render_template("user.html", user_name = name)
# ----------------------------------------------------------------------

# Create Custom Error Page

#Invalid Error
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

# ----------------------------------------------------------------------------

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

# -------------------------------------------------------------------------------------

# Update Database Record
@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == 'POST':
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		try:
			db.session.commit()
			flash("User Updated Successfully")
			return render_template("update.html",
				form = form,
				name_to_update = name_to_update)
		except:
			flash("Error! Looks like there was an error")
			return render_template("update.html",
				form = form,
				name_to_update = name_to_update,
				id = id)
	else:
		return render_template("update.html",
				form = form,
				name_to_update = name_to_update,
				id = id)

# -------------------------------------------------------------------------------

# Delete Users
@app.route('/delete/<int:id>')
def delete(id):
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