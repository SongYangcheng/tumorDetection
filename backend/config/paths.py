# config/paths.py
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
TMP_DIR = os.path.join(DATA_DIR, 'tmp')

BRAIN_TUMOR_WEIGHT_PATH = os.path.join(
    BASE_DIR,
    'weights',
    'ResNeXt50_best.pt'
)
