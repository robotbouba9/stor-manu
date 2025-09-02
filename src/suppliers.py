from flask import Blueprint, jsonify, request
from src.models.database import Supplier, db

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """الحصول على جميع الموردين"""
    suppliers = Supplier.query.all()
    return jsonify([{
        'supplier_id': supplier.supplier_id,
        'name': supplier.name,
        'address': supplier.address,
        'phone_number': supplier.phone_number,
        'email': supplier.email,
        'products_count': len(supplier.products),
        'created_at': supplier.created_at.isoformat() if supplier.created_at else None,
        'updated_at': supplier.updated_at.isoformat() if supplier.updated_at else None
    } for supplier in suppliers])

@suppliers_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """إضافة مورد جديد"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'اسم المورد مطلوب'}), 400
    
    # التحقق من عدم وجود مورد بنفس البريد الإلكتروني
    if data.get('email'):
        existing_supplier = Supplier.query.filter_by(email=data['email']).first()
        if existing_supplier:
            return jsonify({'error': 'مورد بهذا البريد الإلكتروني موجود بالفعل'}), 400
    
    try:
        supplier = Supplier(
            name=data['name'],
            address=data.get('address'),
            phone_number=data.get('phone_number'),
            email=data.get('email')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify({
            'supplier_id': supplier.supplier_id,
            'name': supplier.name,
            'address': supplier.address,
            'phone_number': supplier.phone_number,
            'email': supplier.email,
            'products_count': 0,
            'created_at': supplier.created_at.isoformat() if supplier.created_at else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """الحصول على مورد محدد"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    return jsonify({
        'supplier_id': supplier.supplier_id,
        'name': supplier.name,
        'address': supplier.address,
        'phone_number': supplier.phone_number,
        'email': supplier.email,
        'products_count': len(supplier.products),
        'created_at': supplier.created_at.isoformat() if supplier.created_at else None,
        'updated_at': supplier.updated_at.isoformat() if supplier.updated_at else None,
        'products': [{
            'product_id': product.product_id,
            'name': product.name,
            'brand': product.brand,
            'model': product.model,
            'quantity': product.quantity,
            'price': float(product.price)
        } for product in supplier.products]
    })

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """تحديث مورد"""
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'اسم المورد مطلوب'}), 400
    
    # التحقق من عدم وجود مورد آخر بنفس البريد الإلكتروني
    if data.get('email'):
        existing_supplier = Supplier.query.filter(
            Supplier.email == data['email'],
            Supplier.supplier_id != supplier_id
        ).first()
        if existing_supplier:
            return jsonify({'error': 'مورد بهذا البريد الإلكتروني موجود بالفعل'}), 400
    
    try:
        supplier.name = data.get('name', supplier.name)
        supplier.address = data.get('address', supplier.address)
        supplier.phone_number = data.get('phone_number', supplier.phone_number)
        supplier.email = data.get('email', supplier.email)
        
        db.session.commit()
        
        return jsonify({
            'supplier_id': supplier.supplier_id,
            'name': supplier.name,
            'address': supplier.address,
            'phone_number': supplier.phone_number,
            'email': supplier.email,
            'products_count': len(supplier.products),
            'updated_at': supplier.updated_at.isoformat() if supplier.updated_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """حذف مورد"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # التحقق من عدم وجود منتجات مرتبطة بهذا المورد
    if supplier.products:
        return jsonify({'error': 'لا يمكن حذف مورد له منتجات مسجلة'}), 400
    
    try:
        db.session.delete(supplier)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/search', methods=['GET'])
def search_suppliers():
    """البحث في الموردين"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    suppliers = Supplier.query.filter(
        Supplier.name.contains(query) | 
        Supplier.phone_number.contains(query) | 
        Supplier.email.contains(query)
    ).all()
    
    return jsonify([{
        'supplier_id': supplier.supplier_id,
        'name': supplier.name,
        'phone_number': supplier.phone_number,
        'email': supplier.email,
        'products_count': len(supplier.products)
    } for supplier in suppliers])

