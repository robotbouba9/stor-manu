from flask import Blueprint, request, jsonify
from src.models.database import db, Customer, Sale
from sqlalchemy import or_

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    try:
        search = request.args.get('search', '')
        
        query = Customer.query
        
        if search:
            query = query.filter(or_(
                Customer.name.contains(search),
                Customer.phone_number.contains(search),
                Customer.email.contains(search)
            ))
        
        customers = query.all()
        
        customers_data = []
        for customer in customers:
            # حساب إجمالي المشتريات
            total_purchases = sum(sale.total_amount for sale in customer.sales)
            
            customers_data.append({
                'customer_id': customer.customer_id,
                'name': customer.name,
                'address': customer.address,
                'phone_number': customer.phone_number,
                'email': customer.email,
                'total_purchases': float(total_purchases),
                'purchases_count': len(customer.sales),
                'created_at': customer.created_at.isoformat() if customer.created_at else None,
                'updated_at': customer.updated_at.isoformat() if customer.updated_at else None
            })
        
        return jsonify({'customers': customers_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'اسم العميل مطلوب'}), 400
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if data.get('email'):
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        customer = Customer(
            name=data['name'],
            address=data.get('address', ''),
            phone_number=data.get('phone_number', ''),
            email=data.get('email')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إضافة العميل بنجاح',
            'customer_id': customer.customer_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # حساب إجمالي المشتريات
        total_purchases = sum(sale.total_amount for sale in customer.sales)
        
        customer_data = {
            'customer_id': customer.customer_id,
            'name': customer.name,
            'address': customer.address,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'total_purchases': float(total_purchases),
            'purchases_count': len(customer.sales),
            'created_at': customer.created_at.isoformat() if customer.created_at else None,
            'updated_at': customer.updated_at.isoformat() if customer.updated_at else None
        }
        
        return jsonify(customer_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        # التحقق من عدم تكرار البريد الإلكتروني
        if data.get('email') and data['email'] != customer.email:
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer:
                return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        # تحديث البيانات
        if 'name' in data:
            customer.name = data['name']
        if 'address' in data:
            customer.address = data['address']
        if 'phone_number' in data:
            customer.phone_number = data['phone_number']
        if 'email' in data:
            customer.email = data['email']
        
        db.session.commit()
        
        return jsonify({'message': 'تم تحديث العميل بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # التحقق من عدم وجود مبيعات مرتبطة بالعميل
        if customer.sales:
            return jsonify({'error': 'لا يمكن حذف العميل لوجود مبيعات مرتبطة به'}), 400
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف العميل بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>/purchases', methods=['GET'])
def get_customer_purchases(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        purchases_data = []
        for sale in customer.sales:
            purchases_data.append({
                'sale_id': sale.sale_id,
                'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
                'total_amount': float(sale.total_amount),
                'discount_amount': float(sale.discount_amount),
                'tax_amount': float(sale.tax_amount),
                'payment_method': sale.payment_method,
                'status': sale.status
            })
        
        return jsonify({'purchases': purchases_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

