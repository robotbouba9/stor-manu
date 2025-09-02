from flask import Blueprint, request, jsonify
from src.models.database import db, Product, Category, Supplier
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    try:
        # البحث والتصفية
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)
        supplier_id = request.args.get('supplier_id', type=int)
        low_stock = request.args.get('low_stock', type=bool)
        
        query = Product.query
        
        if search:
            query = query.filter(or_(
                Product.name.contains(search),
                Product.brand.contains(search),
                Product.model.contains(search),
                Product.serial_number.contains(search)
            ))
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
            
        if supplier_id:
            query = query.filter(Product.supplier_id == supplier_id)
            
        if low_stock:
            query = query.filter(Product.quantity <= Product.min_stock_level)
        
        products = query.all()
        
        products_data = []
        for product in products:
            products_data.append({
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
                'is_low_stock': product.quantity <= product.min_stock_level,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None
            })
        
        return jsonify({'products': products_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('name') or not data.get('price'):
            return jsonify({'error': 'اسم المنتج والسعر مطلوبان'}), 400
        
        # التحقق من عدم تكرار الرقم التسلسلي
        if data.get('serial_number'):
            existing_product = Product.query.filter_by(serial_number=data['serial_number']).first()
            if existing_product:
                return jsonify({'error': 'الرقم التسلسلي موجود مسبقاً'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            quantity=data.get('quantity', 0),
            serial_number=data.get('serial_number'),
            brand=data.get('brand', ''),
            model=data.get('model', ''),
            category_id=data.get('category_id'),
            supplier_id=data.get('supplier_id'),
            location=data.get('location', ''),
            min_stock_level=data.get('min_stock_level', 5)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة المنتج بنجاح',
            'product_id': product.product_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        product_data = {
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
            'is_low_stock': product.quantity <= product.min_stock_level,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        }
        
        return jsonify(product_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # التحقق من عدم تكرار الرقم التسلسلي
        if data.get('serial_number') and data['serial_number'] != product.serial_number:
            existing_product = Product.query.filter_by(serial_number=data['serial_number']).first()
            if existing_product:
                return jsonify({'error': 'الرقم التسلسلي موجود مسبقاً'}), 400
        
        # تحديث البيانات
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'quantity' in data:
            product.quantity = data['quantity']
        if 'serial_number' in data:
            product.serial_number = data['serial_number']
        if 'brand' in data:
            product.brand = data['brand']
        if 'model' in data:
            product.model = data['model']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'supplier_id' in data:
            product.supplier_id = data['supplier_id']
        if 'location' in data:
            product.location = data['location']
        if 'min_stock_level' in data:
            product.min_stock_level = data['min_stock_level']
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث المنتج بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        # التحقق من عدم وجود مبيعات مرتبطة بالمنتج
        if product.sale_items:
            return jsonify({'error': 'لا يمكن حذف المنتج لوجود مبيعات مرتبطة به'}), 400
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المنتج بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/low-stock', methods=['GET'])
def get_low_stock_products():
    try:
        products = Product.query.filter(Product.quantity <= Product.min_stock_level).all()
        
        products_data = []
        for product in products:
            products_data.append({
                'product_id': product.product_id,
                'name': product.name,
                'quantity': product.quantity,
                'min_stock_level': product.min_stock_level,
                'category_name': product.category.name if product.category else None
            })
        
        return jsonify({'low_stock_products': products_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

