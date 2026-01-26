"""
Authentication module for web interface
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Simple user storage (in production, use a proper database)
USERS_FILE = os.path.expanduser('~/.ssh_manager_users.json')

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
    
    @staticmethod
    def get(user_id):
        users = User.load_users()
        for uid, data in users.items():
            if uid == user_id:
                return User(uid, data['username'])
        return None
    
    @staticmethod
    def load_users():
        if not os.path.exists(USERS_FILE):
            # Create default admin user
            default_users = {
                'admin': {
                    'username': 'admin',
                    'password': generate_password_hash('admin'),
                }
            }
            with open(USERS_FILE, 'w') as f:
                json.dump(default_users, f)
            return default_users
        
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_users(users):
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
    
    @staticmethod
    def authenticate(username, password):
        users = User.load_users()
        for uid, data in users.items():
            if data['username'] == username:
                if check_password_hash(data['password'], password):
                    return User(uid, username)
        return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('connections.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        from flask_login import current_user
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        users = User.load_users()
        user_data = users.get(current_user.id)
        
        if user_data and check_password_hash(user_data['password'], current_password):
            user_data['password'] = generate_password_hash(new_password)
            users[current_user.id] = user_data
            User.save_users(users)
            flash('Password changed successfully', 'success')
            return redirect(url_for('connections.dashboard'))
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('change_password.html')
