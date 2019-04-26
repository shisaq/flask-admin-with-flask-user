# -*- coding: utf-8 -*-

from flask import Flask, redirect, url_for, render_template, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, user_logged_in

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib import sqla
from flask_admin.contrib.fileadmin import FileAdmin

import os.path as op
path = op.join(op.dirname(__file__), 'static/files')


# Create Flask app load app.config
app = Flask(__name__)

app.config['SECRET_KEY'] = 'This is an INSECURE secret!! DO NOT use this in production!!'
# Flask-SQLAlchemy settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quickstart_app.sqlite'    # File-based SQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Avoids SQLAlchemy warning

# Flask-User settings
app.config['USER_APP_NAME'] = "文件浏览系统".decode('utf-8')     # Shown in and email templates and page footers
app.config['USER_ENABLE_EMAIL'] = False      # Disable email authentication
app.config['USER_ENABLE_USERNAME'] = True    # Enable username authentication
app.config['USER_REQUIRE_RETYPE_PASSWORD'] = True    # Simplify register form

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

# Create all database tables
db.create_all()

# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)

# 重写admin登录
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    @login_required
    def index(self):
        return super(MyAdminIndexView, self).index()


# admin columns
admin = Admin(app, name='File Research', index_view=MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(FileAdmin(path, '/static/files/', name='Media Files'))

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # String-based templates
    return render_template('index.html')

# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/members')
@login_required    # User must be authenticated
def member_page():
    # String-based templates
    return render_template_string("""
        {% extends "flask_user_layout.html" %}
        {% block content %}
            <h2>Members page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
        {% endblock %}
        """)


# Start development web server
if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)