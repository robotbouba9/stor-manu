from flask import Blueprint, request, jsonify
from src.models.database import db, Category

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'category_id': category.category_id,
                'name': category.name,
                'products_count': len(category.products)
            })
        
        return jsonify({'categories': categories_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'اسم الفئة مطلوب'}), 400
        
        # التحقق من عدم تكرار اسم الفئة
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return jsonify({'error': 'اسم الفئة موجود مسبقاً'}), 400
        
        category = Category(name=data['name'])
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة الفئة بنجاح',
            'category_id': category.category_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        category_data = {
            'category_id': category.category_id,
            'name': category.name,
            'products_count': len(category.products)
        }
        
        return jsonify(category_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'اسم الفئة مطلوب'}), 400
        
        # التحقق من عدم تكرار اسم الفئة
        if data['name'] != category.name:
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category:
                return jsonify({'error': 'اسم الفئة موجود مسبقاً'}), 400
        
        category.name = data['name']
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث الفئة بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        # التحقق من عدم وجود منتجات مرتبطة بالفئة
        if category.products:
            return jsonify({'error': 'لا يمكن حذف الفئة لوجود منتجات مرتبطة بها'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الفئة بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

