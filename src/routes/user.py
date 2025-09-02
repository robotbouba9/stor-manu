from flask import Blueprint, request, jsonify
from src.models.database import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        
        users_data = []
        for user in users:
            users_data.append({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({'users': users_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'error': 'اسم المستخدم وكلمة المرور والبريد الإلكتروني مطلوبة'}), 400
        
        # التحقق من عدم تكرار اسم المستخدم
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'اسم المستخدم موجود مسبقاً'}), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        # تشفير كلمة المرور
        password_hash = generate_password_hash(data['password'])
        
        user = User(
            username=data['username'],
            password_hash=password_hash,
            email=data['email'],
            role=data.get('role', 'user')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء المستخدم بنجاح',
            'user_id': user.user_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
        
        # إنشاء JWT token
        token = jwt.encode({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, 'secret_key', algorithm='HS256')
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'token': token,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # التحقق من عدم تكرار اسم المستخدم
        if data.get('username') and data['username'] != user.username:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user:
                return jsonify({'error': 'اسم المستخدم موجود مسبقاً'}), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if data.get('email') and data['email'] != user.email:
            existing_email = User.query.filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        # تحديث البيانات
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث المستخدم بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المستخدم بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
