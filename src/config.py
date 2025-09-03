import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class Config:
    """إعدادات التطبيق الأساسية"""
    
    # مفتاح الأمان
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # إذا كان هناك رابط قاعدة بيانات (للنشر)
        if DATABASE_URL.startswith('postgres://'):
            # تحويل postgres:// إلى postgresql:// للتوافق مع SQLAlchemy الحديث
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # للتطوير المحلي - استخدام SQLite
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "database", "app.db")}'
    
    # إعدادات SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # إعدادات CORS
    CORS_ORIGINS = ['*']  # في الإنتاج، حدد النطاقات المسموحة
    
    # إعدادات JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # ساعة واحدة
    
    # إعدادات التطبيق
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')

class DevelopmentConfig(Config):
    """إعدادات التطوير"""
    DEBUG = True

class ProductionConfig(Config):
    """إعدادات الإنتاج"""
    DEBUG = False

# اختيار التكوين حسب البيئة
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """الحصول على التكوين المناسب حسب البيئة"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

