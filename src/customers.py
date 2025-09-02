from flask import Blueprint, jsonify, request
from src.models.database import Customer, db

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    """الحصول على جميع العملاء"""
    customers = Customer.query.all()
    return jsonify([{
        'customer_id': customer.customer_id,
        'name': customer.name,
        'address': customer.address,
        'phone_number': customer.phone_number,
        'email': customer.email,
        'sales_count': len(customer.sales),
        'created_at': customer.created_at.isoformat() if customer.created_at else None,
        'updated_at': customer.updated_at.isoformat() if customer.updated_at else None
    } for customer in customers])

@customers_bp.route('/customers', methods=['POST'])
def create_customer():
    """إضافة عميل جديد"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'اسم العميل مطلوب'}), 400
    
    # التحقق من عدم وجود عميل بنفس البريد الإلكتروني
    if data.get('email'):
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'عميل بهذا البريد الإلكتروني موجود بالفعل'}), 400
    
    try:
        customer = Customer(
            name=data['name'],
            address=data.get('address'),
            phone_number=data.get('phone_number'),
            email=data.get('email')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'customer_id': customer.customer_id,
            'name': customer.name,
            'address': customer.address,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'sales_count': 0,
            'created_at': customer.created_at.isoformat() if customer.created_at else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """الحصول على عميل محدد"""
    customer = Customer.query.get_or_404(customer_id)
    
    # حساب إجمالي المشتريات
    total_purchases = sum(sale.total_amount for sale in customer.sales)
    
    return jsonify({
        'customer_id': customer.customer_id,
        'name': customer.name,
        'address': customer.address,
        'phone_number': customer.phone_number,
        'email': customer.email,
        'sales_count': len(customer.sales),
        'total_purchases': float(total_purchases),
        'created_at': customer.created_at.isoformat() if customer.created_at else None,
        'updated_at': customer.updated_at.isoformat() if customer.updated_at else None,
        'recent_sales': [{
            'sale_id': sale.sale_id,
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
            'total_amount': float(sale.total_amount),
            'status': sale.status
        } for sale in customer.sales[-5:]]  # آخر 5 مبيعات
    })

@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """تحديث عميل"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'اسم العميل مطلوب'}), 400
    
    # التحقق من عدم وجود عميل آخر بنفس البريد الإلكتروني
    if data.get('email'):
        existing_customer = Customer.query.filter(
            Customer.email == data['email'],
            Customer.customer_id != customer_id
        ).first()
        if existing_customer:
            return jsonify({'error': 'عميل بهذا البريد الإلكتروني موجود بالفعل'}), 400
    
    try:
        customer.name = data.get('name', customer.name)
        customer.address = data.get('address', customer.address)
        customer.phone_number = data.get('phone_number', customer.phone_number)
        customer.email = data.get('email', customer.email)
        
        db.session.commit()
        
        return jsonify({
            'customer_id': customer.customer_id,
            'name': customer.name,
            'address': customer.address,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'sales_count': len(customer.sales),
            'updated_at': customer.updated_at.isoformat() if customer.updated_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """حذف عميل"""
    customer = Customer.query.get_or_404(customer_id)
    
    # التحقق من عدم وجود مبيعات مرتبطة بهذا العميل
    if customer.sales:
        return jsonify({'error': 'لا يمكن حذف عميل له مبيعات مسجلة'}), 400
    
    try:
        db.session.delete(customer)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/search', methods=['GET'])
def search_customers():
    """البحث في العملاء"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    customers = Customer.query.filter(
        Customer.name.contains(query) | 
        Customer.phone_number.contains(query) | 
        Customer.email.contains(query)
    ).all()
    
    return jsonify([{
        'customer_id': customer.customer_id,
        'name': customer.name,
        'phone_number': customer.phone_number,
        'email': customer.email,
        'sales_count': len(customer.sales)
    } for customer in customers])

