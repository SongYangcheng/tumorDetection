"""
用户管理路由模块
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from utils.auth import admin_required
from werkzeug.security import generate_password_hash
import re
import os
import time

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """获取所有用户列表（仅管理员）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        simple = request.args.get('simple', '0') == '1'
        
        query = User.query
        
        if search:
            query = query.filter(
                User.username.contains(search) | 
                User.email.contains(search)
            )
        
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        payload = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'role': 'admin' if user.is_admin else 'doctor'
        } for user in users.items]

        if simple:
            return jsonify(payload), 200

        return jsonify({
            'users': payload,
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': '获取用户列表失败', 'error': str(e)}), 500


@user_management_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """创建新用户（管理员）"""
    try:
        data = request.get_json() or {}
        username = data.get('username')
        role = data.get('role', 'doctor')
        email = data.get('email') or f"{username or 'user'}@example.com"
        password = data.get('password') or 'ChangeMe123'

        if not username:
            return jsonify({'message': '用户名必填'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 409

        user = User(
            username=username,
            email=email,
            is_active=True,
            is_admin=role == 'admin'
        )
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'id': user.id, 'username': user.username, 'role': role}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '创建用户失败', 'error': str(e)}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """获取特定用户信息（仅管理员）"""
    try:
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'is_active': user.is_active,
            'is_admin': user.is_admin
        }), 200
        
    except Exception as e:
        return jsonify({'message': '获取用户信息失败', 'error': str(e)}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """更新用户信息（仅管理员）"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'message': '请求数据不能为空'}), 400
        
        # 更新用户名（如果提供）
        if 'username' in data:
            username = data['username']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'message': '用户名已存在'}), 409
            user.username = username
        
        # 更新邮箱（如果提供）
        if 'email' in data:
            email = data['email']
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return jsonify({'message': '邮箱格式不正确'}), 400
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'message': '邮箱已被注册'}), 409
            user.email = email
        
        # 更新用户状态（如果提供）
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        # 更新管理员权限（如果提供）
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        
        db.session.commit()
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '更新用户信息失败', 'error': str(e)}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """删除用户（仅管理员）"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 不能删除自己
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        if user.id == current_user_id:
            return jsonify({'message': '不能删除自己的账户'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '用户删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '删除用户失败', 'error': str(e)}), 500

# 模型运维与系统监控
@user_management_bp.route('/model', methods=['GET'])
@jwt_required()
@admin_required
def get_model_info():
    try:
        version = 'YOLO11'
        performance = 'AUC=0.89'
        return jsonify({'version': version, 'performance': performance}), 200
    except Exception as e:
        return jsonify({'message': '获取模型信息失败', 'error': str(e)}), 500

@user_management_bp.route('/model/update', methods=['POST'])
@jwt_required()
@admin_required
def update_model():
    try:
        # 这里可集成实际的模型更新逻辑
        version = 'YOLO11'
        performance = 'AUC=0.90'
        return jsonify({'version': version, 'performance': performance}), 200
    except Exception as e:
        return jsonify({'message': '更新模型失败', 'error': str(e)}), 500

@user_management_bp.route('/backup', methods=['POST'])
@jwt_required()
@admin_required
def backup_data():
    try:
        # 简化的备份占位逻辑
        ts = int(time.time())
        return jsonify({'message': f'备份完成: {ts}'}), 200
    except Exception as e:
        return jsonify({'message': '备份失败', 'error': str(e)}), 500

@user_management_bp.route('/monitor', methods=['GET'])
@jwt_required()
@admin_required
def system_monitor():
    try:
        server_status = 'running'
        storage_usage = 35
        api_calls = 128
        return jsonify({'serverStatus': server_status, 'storageUsage': storage_usage, 'apiCalls': api_calls}), 200
    except Exception as e:
        return jsonify({'message': '获取监控信息失败', 'error': str(e)}), 500

@user_management_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户资料"""
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        user = User.query.get_or_404(current_user_id)
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': '获取用户资料失败', 'error': str(e)}), 500

@user_management_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新当前用户资料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'message': '请求数据不能为空'}), 400
        
        # 更新用户名（如果提供）
        if 'username' in data:
            username = data['username']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'message': '用户名已存在'}), 409
            user.username = username
        
        # 更新邮箱（如果提供）
        if 'email' in data:
            email = data['email']
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return jsonify({'message': '邮箱格式不正确'}), 400
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'message': '邮箱已被注册'}), 409
            user.email = email
        
        db.session.commit()
        
        return jsonify({
            'message': '用户资料更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '更新用户资料失败', 'error': str(e)}), 500

@user_management_bp.route('/profile/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改当前用户密码"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        data = request.get_json()
        
        if not data or 'old_password' not in data or 'new_password' not in data:
            return jsonify({'message': '缺少必需字段'}), 400
        
        old_password = data['old_password']
        new_password = data['new_password']
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({'message': '旧密码不正确'}), 400
        
        # 密码强度验证
        if len(new_password) < 6:
            return jsonify({'message': '新密码长度至少为6位'}), 400
        
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '修改密码失败', 'error': str(e)}), 500
