from flask import Blueprint, request, jsonify
from models.user import User, db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': '缺少必需字段'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # 验证邮箱格式
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'message': '邮箱格式不正确'}), 400
        
        # 检查用户名或邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': '邮箱已被注册'}), 409
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': '用户注册成功', 'user_id': user.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '注册失败', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': '缺少用户名或密码'}), 400
        
        username = data['username']
        password = data['password']
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # 创建访问令牌
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            }), 200
        else:
            return jsonify({'message': '用户名或密码错误'}), 401
    
    except Exception as e:
        return jsonify({'message': '登录失败', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': '用户不存在或未激活'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'is_admin': user.is_admin
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': '获取用户信息失败', 'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': '用户不存在或未激活'}), 404
        
        data = request.get_json()
        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({'message': '缺少必需字段'}), 400
        
        old_password = data['old_password']
        new_password = data['new_password']
        
        if not user.check_password(old_password):
            return jsonify({'message': '原密码错误'}), 400
        
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '修改密码失败', 'error': str(e)}), 500
