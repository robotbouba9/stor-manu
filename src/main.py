import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.database import db
from src.config import get_config
from src.routes.user import user_bp
from src.routes.products import products_bp
from src.routes.categories import categories_bp
from src.routes.customers import customers_bp
from src.routes.suppliers import suppliers_bp
from src.routes.sales import sales_bp
from src.routes.settings import settings_bp

def create_app():
    """إنشاء وتكوين التطبيق"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # تحميل التكوين
    config_class = get_config()
    app.config.from_object(config_class)
    
    # إعداد CORS للسماح بالتفاعل مع الواجهة الأمامية
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # تسجيل المسارات (Blueprints)
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(categories_bp, url_prefix='/api')
    app.register_blueprint(customers_bp, url_prefix='/api')
    app.register_blueprint(suppliers_bp, url_prefix='/api')
    app.register_blueprint(sales_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # إنشاء الجداول إذا لم تكن موجودة
    with app.app_context():
        try:
            db.create_all()
            print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """خدمة الملفات الثابتة"""
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    @app.route('/health')
    def health_check():
        """فحص صحة التطبيق"""
        return {"status": "healthy", "message": "التطبيق يعمل بشكل طبيعي"}, 200
    
    return app

# إنشاء التطبيق
app = create_app()

if __name__ == '__main__':
    # للتطوير المحلي
    config_class = get_config()
    app.run(
        host=config_class.HOST,
        port=config_class.PORT,
        debug=config_class.DEBUG
    )

