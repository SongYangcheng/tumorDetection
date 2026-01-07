from .auth import auth_bp
from .medical_images import medical_images_bp
from .user_management import user_management_bp

__all__ = ['auth_bp', 'medical_images_bp', 'user_management_bp']