from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

app.app_context().push()

# Create Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable = False)
	email = db.Column(db.String(200), nullable= False, unique = True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Name %r>' % self.name


# Create a Form Class
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	submit = SubmitField('Submit')


# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's your name", validators=[DataRequired()])
	submit = SubmitField('Submit')


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			user = Users(name = form.name.data, email = form.email.data)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data=''
		form.email.data=''
		flash("User added Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form=form, name=name, our_users = our_users)





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

# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
	return render_template("user.html", user_name = name)


# Create Custom Error Page

#Invalid Error
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

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

