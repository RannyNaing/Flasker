from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from models import db, Users
from webforms import LoginForm, UserForm
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app 

auth = Blueprint('auth', __name__)

# Add user registration, login, and logout views here
# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(auth)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))


# Update Database Record of the User
@auth.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		# name_to_update.favorite_color = request.form['favorite_color']
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
				saver.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name))
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

# ------------------------------------------------------------------------------------------

# Add User
@auth.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			#Hash password
			hashed_pw = generate_password_hash(form.password_hash.data)
			user = Users(name = form.name.data, username= form.username.data, 
							email = form.email.data, #_color= form.favorite_color.data, 
							password_hash = hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data=''
		form.username.data=''
		form.email.data=''
		# form.favorite_color.data=''
		form.password_hash.data = ''
		flash("User added Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form=form, name=name, our_users = our_users)

# Delete Users
@auth.route('/delete/<int:id>')
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
		return redirect(url_for('auth.dashboard'))

# --------------------------------------------------------------------------------------------


# Create a Login Page
@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Successfully")
				return redirect(url_for('auth.dashboard'))
			else:
				flash("Wrong Password - Try Again!")
		else:
			flash("That User Does not Exist!!! Please Try Again.")
	return render_template('login.html', form=form)


# Create Dashboard Page
@auth.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		# name_to_update.favorite_color = request.form['favorite_color']
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
				saver.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic_name))
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

# Create Logout
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You have been Logged Out! Thanks for stopping by")
	return redirect(url_for('auth.login'))




# Create Admin Dummy Page

# Create a route decorator
@auth.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 1:
		return render_template("admin.html")
	else:
		flash("Sorry must be admin to access the Admin page")
		return redirect(url_for('auth.dashboard'))