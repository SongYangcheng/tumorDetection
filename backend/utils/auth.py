from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User

def admin_required(f):
    """
    管理员权限装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        current_user = User.query.get(current_user_id)
        
        if not current_user or not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return jsonify({'message': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """
    登录验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_active:
            return jsonify({'message': '用户未激活或不存在'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
