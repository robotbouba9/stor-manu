from flask import Blueprint, request, jsonify
from src.models.database import db, Supplier
from sqlalchemy import or_

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    try:
        search = request.args.get('search', '')
        
        query = Supplier.query
        
        if search:
            query = query.filter(or_(
                Supplier.name.contains(search),
                Supplier.phone_number.contains(search),
                Supplier.email.contains(search)
            ))
        
        suppliers = query.all()
        
        suppliers_data = []
        for supplier in suppliers:
            suppliers_data.append({
                'supplier_id': supplier.supplier_id,
                'name': supplier.name,
                'address': supplier.address,
                'phone_number': supplier.phone_number,
                'email': supplier.email,
                'products_count': len(supplier.products),
                'created_at': supplier.created_at.isoformat() if supplier.created_at else None,
                'updated_at': supplier.updated_at.isoformat() if supplier.updated_at else None
            })
        
        return jsonify({'suppliers': suppliers_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'اسم المورد مطلوب'}), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if data.get('email'):
            existing_supplier = Supplier.query.filter_by(email=data['email']).first()
            if existing_supplier:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        supplier = Supplier(
            name=data['name'],
            address=data.get('address', ''),
            phone_number=data.get('phone_number', ''),
            email=data.get('email')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة المورد بنجاح',
            'supplier_id': supplier.supplier_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        supplier_data = {
            'supplier_id': supplier.supplier_id,
            'name': supplier.name,
            'address': supplier.address,
            'phone_number': supplier.phone_number,
            'email': supplier.email,
            'products_count': len(supplier.products),
            'created_at': supplier.created_at.isoformat() if supplier.created_at else None,
            'updated_at': supplier.updated_at.isoformat() if supplier.updated_at else None
        }
        
        return jsonify(supplier_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        data = request.get_json()
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if data.get('email') and data['email'] != supplier.email:
            existing_supplier = Supplier.query.filter_by(email=data['email']).first()
            if existing_supplier:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        # تحديث البيانات
        if 'name' in data:
            supplier.name = data['name']
        if 'address' in data:
            supplier.address = data['address']
        if 'phone_number' in data:
            supplier.phone_number = data['phone_number']
        if 'email' in data:
            supplier.email = data['email']
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث المورد بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # التحقق من عدم وجود منتجات مرتبطة بالمورد
        if supplier.products:
            return jsonify({'error': 'لا يمكن حذف المورد لوجود منتجات مرتبطة به'}), 400
        
        db.session.delete(supplier)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المورد بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>/products', methods=['GET'])
def get_supplier_products(supplier_id):
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        products_data = []
        for product in supplier.products:
            products_data.append({
                'product_id': product.product_id,
                'name': product.name,
                'brand': product.brand,
                'model': product.model,
                'price': float(product.price),
                'quantity': product.quantity,
                'category_name': product.category.name if product.category else None
            })
        
        return jsonify({'products': products_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

