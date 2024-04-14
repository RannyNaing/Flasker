from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from webforms import SearchForm
from flask_ckeditor import CKEditor
import uuid as uuid
from flask_cors import CORS, cross_origin

from models import db, Posts, Users


from blog_posts import blog_posts


from auth import auth
#Create an instance of Flask
app = Flask(__name__)
# CK Editor
ckeditor = CKEditor(app)
# Add database

# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

# MYSQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@localhost/db_name"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost/our_users"

# Heroku Postgressql
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://aawjdadalyqjgc:9e836cdfa869390d8b0e69e26c21c173900610e2a5a73e784d4d00a82af3d896@ec2-44-221-2-86.compute-1.amazonaws.com:5432/d1nrkgdpk8mmnf"
# Secret Key!!
app.config['SECRET_KEY'] = "super_secret_key"

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
app.app_context().push()

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))


app.register_blueprint(blog_posts)
app.register_blueprint(auth)

CORS(app)

# ----------------------------------------------------------------------------------------

# Home Page
# Create a route decorator
@app.route('/')
def index():
	return render_template("index.html")

# -----------------------------------------------------------------------------------------

# Simple API to get posts and add a new post
@app.route('/api/posts', methods=['GET', 'POST'])
@cross_origin(origin='example.com')
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

# --------------------------------------------------------------
# NavBar and Search Function

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
    

# Create Custom Error Page

#Invalid Error
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
	return render_template("500.html"), 500