from flask import Blueprint, jsonify, request
from src.models.database import Category, db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """الحصول على جميع الفئات"""
    categories = Category.query.all()
    return jsonify([{
        'category_id': category.category_id,
        'name': category.name,
        'products_count': len(category.products)
    } for category in categories])

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    """إضافة فئة جديدة"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'اسم الفئة مطلوب'}), 400
    
    # التحقق من عدم وجود فئة بنفس الاسم
    existing_category = Category.query.filter_by(name=data['name']).first()
    if existing_category:
        return jsonify({'error': 'فئة بهذا الاسم موجودة بالفعل'}), 400
    
    try:
        category = Category(name=data['name'])
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'category_id': category.category_id,
            'name': category.name,
            'products_count': 0
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """الحصول على فئة محددة"""
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'category_id': category.category_id,
        'name': category.name,
        'products_count': len(category.products),
        'products': [{
            'product_id': product.product_id,
            'name': product.name,
            'price': float(product.price),
            'quantity': product.quantity
        } for product in category.products]
    })

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """تحديث فئة"""
    category = Category.query.get_or_404(category_id)
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'اسم الفئة مطلوب'}), 400
    
    # التحقق من عدم وجود فئة أخرى بنفس الاسم
    existing_category = Category.query.filter(
        Category.name == data['name'],
        Category.category_id != category_id
    ).first()
    if existing_category:
        return jsonify({'error': 'فئة بهذا الاسم موجودة بالفعل'}), 400
    
    try:
        category.name = data['name']
        db.session.commit()
        
        return jsonify({
            'category_id': category.category_id,
            'name': category.name,
            'products_count': len(category.products)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """حذف فئة"""
    category = Category.query.get_or_404(category_id)
    
    # التحقق من عدم وجود منتجات مرتبطة بهذه الفئة
    if category.products:
        return jsonify({'error': 'لا يمكن حذف فئة تحتوي على منتجات'}), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

