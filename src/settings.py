from flask import Blueprint, jsonify, request
from src.models.database import Setting, db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET'])
def get_settings():
    """الحصول على جميع الإعدادات"""
    settings = Setting.query.all()
    return jsonify({
        setting.key: {
            'value': setting.value,
            'description': setting.description
        } for setting in settings
    })

@settings_bp.route('/settings/<string:key>', methods=['GET'])
def get_setting(key):
    """الحصول على إعداد محدد"""
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        return jsonify({'error': 'الإعداد غير موجود'}), 404
    
    return jsonify({
        'key': setting.key,
        'value': setting.value,
        'description': setting.description
    })

@settings_bp.route('/settings', methods=['POST'])
def create_or_update_settings():
    """إنشاء أو تحديث إعدادات متعددة"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'لا توجد بيانات للتحديث'}), 400
    
    try:
        updated_settings = []
        
        for key, value_data in data.items():
            setting = Setting.query.filter_by(key=key).first()
            
            if setting:
                # تحديث إعداد موجود
                setting.value = value_data.get('value', setting.value)
                setting.description = value_data.get('description', setting.description)
            else:
                # إنشاء إعداد جديد
                setting = Setting(
                    key=key,
                    value=value_data.get('value'),
                    description=value_data.get('description')
                )
                db.session.add(setting)
            
            updated_settings.append({
                'key': setting.key,
                'value': setting.value,
                'description': setting.description
            })
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الإعدادات بنجاح',
            'updated_settings': updated_settings
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/<string:key>', methods=['PUT'])
def update_setting(key):
    """تحديث إعداد محدد"""
    data = request.json
    
    if not data.get('value'):
        return jsonify({'error': 'قيمة الإعداد مطلوبة'}), 400
    
    try:
        setting = Setting.query.filter_by(key=key).first()
        
        if setting:
            setting.value = data['value']
            setting.description = data.get('description', setting.description)
        else:
            setting = Setting(
                key=key,
                value=data['value'],
                description=data.get('description')
            )
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'key': setting.key,
            'value': setting.value,
            'description': setting.description
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/<string:key>', methods=['DELETE'])
def delete_setting(key):
    """حذف إعداد"""
    setting = Setting.query.filter_by(key=key).first()
    
    if not setting:
        return jsonify({'error': 'الإعداد غير موجود'}), 404
    
    try:
        db.session.delete(setting)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/store-info', methods=['GET'])
def get_store_info():
    """الحصول على معلومات المحل"""
    store_settings = Setting.query.filter(
        Setting.key.in_(['store_name', 'store_address', 'store_phone', 'store_email', 'store_logo'])
    ).all()
    
    store_info = {}
    for setting in store_settings:
        store_info[setting.key] = setting.value
    
    return jsonify(store_info)

@settings_bp.route('/settings/store-info', methods=['PUT'])
def update_store_info():
    """تحديث معلومات المحل"""
    data = request.json
    
    store_keys = ['store_name', 'store_address', 'store_phone', 'store_email', 'store_logo']
    
    try:
        for key in store_keys:
            if key in data:
                setting = Setting.query.filter_by(key=key).first()
                
                if setting:
                    setting.value = data[key]
                else:
                    setting = Setting(
                        key=key,
                        value=data[key],
                        description=f'معلومات المحل - {key}'
                    )
                    db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث معلومات المحل بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/init-defaults', methods=['POST'])
def init_default_settings():
    """تهيئة الإعدادات الافتراضية"""
    default_settings = [
        {'key': 'store_name', 'value': 'محل الهواتف', 'description': 'اسم المحل'},
        {'key': 'store_address', 'value': '', 'description': 'عنوان المحل'},
        {'key': 'store_phone', 'value': '', 'description': 'رقم هاتف المحل'},
        {'key': 'store_email', 'value': '', 'description': 'بريد المحل الإلكتروني'},
        {'key': 'currency', 'value': 'ريال', 'description': 'العملة المستخدمة'},
        {'key': 'tax_rate', 'value': '15', 'description': 'معدل الضريبة (%)'},
        {'key': 'receipt_footer', 'value': 'شكراً لزيارتكم', 'description': 'نص أسفل الفاتورة'},
        {'key': 'low_stock_alert', 'value': '5', 'description': 'تنبيه المخزون المنخفض'},
    ]
    
    try:
        for setting_data in default_settings:
            existing = Setting.query.filter_by(key=setting_data['key']).first()
            if not existing:
                setting = Setting(**setting_data)
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'تم تهيئة الإعدادات الافتراضية بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

