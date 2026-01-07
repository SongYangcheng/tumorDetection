"""中间件文件来处理认证相关的逻辑"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User, db

def get_current_user():
    """获取当前认证用户"""
    current_user_id = get_jwt_identity()
    if current_user_id:
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        return User.query.get(current_user_id)
    return None

def require_auth(f):
    """
    需要认证的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            if not current_user or not current_user.is_active:
                return jsonify({'message': '用户未激活或不存在'}), 403
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': '认证失败', 'error': str(e)}), 401
    return decorated_function

def require_admin(f):
    """
    需要管理员权限的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_current_user()
            if not current_user or not current_user.is_active or not current_user.is_admin:
                return jsonify({'message': '需要管理员权限'}), 403
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': '认证失败', 'error': str(e)}), 401
    return decorated_function
