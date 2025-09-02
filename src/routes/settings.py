from flask import Blueprint, request, jsonify
from src.models.database import db, Setting

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET'])
def get_settings():
    try:
        settings = Setting.query.all()
        
        settings_data = {}
        for setting in settings:
            settings_data[setting.key] = {
                'value': setting.value,
                'description': setting.description
            }
        
        return jsonify({'settings': settings_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/<string:key>', methods=['GET'])
def get_setting(key):
    try:
        setting = Setting.query.filter_by(key=key).first()
        
        if not setting:
            return jsonify({'error': 'الإعداد غير موجود'}), 404
        
        setting_data = {
            'key': setting.key,
            'value': setting.value,
            'description': setting.description
        }
        
        return jsonify(setting_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings', methods=['POST'])
def create_or_update_setting():
    try:
        data = request.get_json()
        
        if not data.get('key'):
            return jsonify({'error': 'مفتاح الإعداد مطلوب'}), 400
        
        setting = Setting.query.filter_by(key=data['key']).first()
        
        if setting:
            # تحديث الإعداد الموجود
            setting.value = data.get('value', setting.value)
            setting.description = data.get('description', setting.description)
            message = 'تم تحديث الإعداد بنجاح'
        else:
            # إنشاء إعداد جديد
            setting = Setting(
                key=data['key'],
                value=data.get('value', ''),
                description=data.get('description', '')
            )
            db.session.add(setting)
            message = 'تم إنشاء الإعداد بنجاح'
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'setting_id': setting.setting_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/<string:key>', methods=['PUT'])
def update_setting(key):
    try:
        setting = Setting.query.filter_by(key=key).first_or_404()
        data = request.get_json()
        
        if 'value' in data:
            setting.value = data['value']
        if 'description' in data:
            setting.description = data['description']
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث الإعداد بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/<string:key>', methods=['DELETE'])
def delete_setting(key):
    try:
        setting = Setting.query.filter_by(key=key).first_or_404()
        
        db.session.delete(setting)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الإعداد بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# إعدادات افتراضية
@settings_bp.route('/settings/initialize', methods=['POST'])
def initialize_default_settings():
    try:
        default_settings = [
            {
                'key': 'store_name',
                'value': 'محل الهواتف',
                'description': 'اسم المحل'
            },
            {
                'key': 'store_address',
                'value': '',
                'description': 'عنوان المحل'
            },
            {
                'key': 'store_phone',
                'value': '',
                'description': 'رقم هاتف المحل'
            },
            {
                'key': 'store_email',
                'value': '',
                'description': 'بريد المحل الإلكتروني'
            },
            {
                'key': 'tax_rate',
                'value': '0.15',
                'description': 'معدل الضريبة'
            },
            {
                'key': 'currency',
                'value': 'ريال',
                'description': 'العملة المستخدمة'
            },
            {
                'key': 'receipt_footer',
                'value': 'شكراً لزيارتكم',
                'description': 'نص أسفل الفاتورة'
            }
        ]
        
        for setting_data in default_settings:
            existing_setting = Setting.query.filter_by(key=setting_data['key']).first()
            if not existing_setting:
                setting = Setting(
                    key=setting_data['key'],
                    value=setting_data['value'],
                    description=setting_data['description']
                )
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'message': 'تم تهيئة الإعدادات الافتراضية بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

