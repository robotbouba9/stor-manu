from flask import Blueprint, jsonify, request
from src.models.database import Product, Category, Supplier, db

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """الحصول على جميع المنتجات"""
    products = Product.query.all()
    return jsonify([{
        'product_id': product.product_id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'quantity': product.quantity,
        'serial_number': product.serial_number,
        'brand': product.brand,
        'model': product.model,
        'category_id': product.category_id,
        'category_name': product.category.name if product.category else None,
        'supplier_id': product.supplier_id,
        'supplier_name': product.supplier.name if product.supplier else None,
        'location': product.location,
        'min_stock_level': product.min_stock_level,
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None
    } for product in products])

@products_bp.route('/products', methods=['POST'])
def create_product():
    """إضافة منتج جديد"""
    data = request.json
    
    # التحقق من البيانات المطلوبة
    if not data.get('name') or not data.get('price'):
        return jsonify({'error': 'اسم المنتج والسعر مطلوبان'}), 400
    
    try:
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            quantity=data.get('quantity', 0),
            serial_number=data.get('serial_number'),
            brand=data.get('brand'),
            model=data.get('model'),
            category_id=data.get('category_id'),
            supplier_id=data.get('supplier_id'),
            location=data.get('location'),
            min_stock_level=data.get('min_stock_level', 0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'quantity': product.quantity,
            'serial_number': product.serial_number,
            'brand': product.brand,
            'model': product.model,
            'category_id': product.category_id,
            'supplier_id': product.supplier_id,
            'location': product.location,
            'min_stock_level': product.min_stock_level,
            'created_at': product.created_at.isoformat() if product.created_at else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """الحصول على منتج محدد"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'product_id': product.product_id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'quantity': product.quantity,
        'serial_number': product.serial_number,
        'brand': product.brand,
        'model': product.model,
        'category_id': product.category_id,
        'category_name': product.category.name if product.category else None,
        'supplier_id': product.supplier_id,
        'supplier_name': product.supplier.name if product.supplier else None,
        'location': product.location,
        'min_stock_level': product.min_stock_level,
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None
    })

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """تحديث منتج"""
    product = Product.query.get_or_404(product_id)
    data = request.json
    
    try:
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.quantity = data.get('quantity', product.quantity)
        product.serial_number = data.get('serial_number', product.serial_number)
        product.brand = data.get('brand', product.brand)
        product.model = data.get('model', product.model)
        product.category_id = data.get('category_id', product.category_id)
        product.supplier_id = data.get('supplier_id', product.supplier_id)
        product.location = data.get('location', product.location)
        product.min_stock_level = data.get('min_stock_level', product.min_stock_level)
        
        db.session.commit()
        
        return jsonify({
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'quantity': product.quantity,
            'serial_number': product.serial_number,
            'brand': product.brand,
            'model': product.model,
            'category_id': product.category_id,
            'supplier_id': product.supplier_id,
            'location': product.location,
            'min_stock_level': product.min_stock_level,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """حذف منتج"""
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/low-stock', methods=['GET'])
def get_low_stock_products():
    """الحصول على المنتجات ذات المخزون المنخفض"""
    products = Product.query.filter(Product.quantity <= Product.min_stock_level).all()
    return jsonify([{
        'product_id': product.product_id,
        'name': product.name,
        'quantity': product.quantity,
        'min_stock_level': product.min_stock_level,
        'brand': product.brand,
        'model': product.model
    } for product in products])

@products_bp.route('/products/search', methods=['GET'])
def search_products():
    """البحث في المنتجات"""
    query = request.args.get('q', '')
    category_id = request.args.get('category_id')
    supplier_id = request.args.get('supplier_id')
    
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            Product.name.contains(query) | 
            Product.brand.contains(query) | 
            Product.model.contains(query)
        )
    
    if category_id:
        products_query = products_query.filter(Product.category_id == category_id)
    
    if supplier_id:
        products_query = products_query.filter(Product.supplier_id == supplier_id)
    
    products = products_query.all()
    
    return jsonify([{
        'product_id': product.product_id,
        'name': product.name,
        'price': float(product.price),
        'quantity': product.quantity,
        'brand': product.brand,
        'model': product.model,
        'category_name': product.category.name if product.category else None,
        'supplier_name': product.supplier.name if product.supplier else None
    } for product in products])

