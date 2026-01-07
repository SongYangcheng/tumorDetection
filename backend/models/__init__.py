from flask_sqlalchemy import SQLAlchemy

# 创建一个db实例，供整个应用使用
db = SQLAlchemy()

from .user import User
from .medical_image import MedicalImage, Dataset

__all__ = ['db', 'User', 'MedicalImage', 'Dataset']