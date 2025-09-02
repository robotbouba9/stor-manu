from flask import Blueprint, jsonify, request
from src.models.database import Sale, SaleItem, Product, Customer, db
from datetime import datetime

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales', methods=['GET'])
def get_sales():
    """الحصول على جميع المبيعات"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    sales = Sale.query.order_by(Sale.sale_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'sales': [{
            'sale_id': sale.sale_id,
            'customer_id': sale.customer_id,
            'customer_name': sale.customer.name if sale.customer else 'عميل غير محدد',
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
            'total_amount': float(sale.total_amount),
            'discount_amount': float(sale.discount_amount),
            'tax_amount': float(sale.tax_amount),
            'payment_method': sale.payment_method,
            'status': sale.status,
            'items_count': len(sale.sale_items)
        } for sale in sales.items],
        'pagination': {
            'page': sales.page,
            'pages': sales.pages,
            'per_page': sales.per_page,
            'total': sales.total
        }
    })

@sales_bp.route('/sales', methods=['POST'])
def create_sale():
    """إضافة مبيعة جديدة"""
    data = request.json
    
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'يجب إضافة عنصر واحد على الأقل للمبيعة'}), 400
    
    try:
        # إنشاء المبيعة
        sale = Sale(
            customer_id=data.get('customer_id'),
            total_amount=0,  # سيتم حسابه لاحقاً
            discount_amount=data.get('discount_amount', 0),
            tax_amount=data.get('tax_amount', 0),
            payment_method=data.get('payment_method', 'نقدي'),
            status=data.get('status', 'مكتملة')
        )
        
        db.session.add(sale)
        db.session.flush()  # للحصول على sale_id
        
        total_amount = 0
        
        # إضافة عناصر المبيعة
        for item_data in data['items']:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'المنتج برقم {item_data["product_id"]} غير موجود'}), 400
            
            quantity = item_data['quantity']
            if product.quantity < quantity:
                return jsonify({'error': f'المخزون غير كافي للمنتج {product.name}'}), 400
            
            unit_price = item_data.get('unit_price', product.price)
            item_total = quantity * unit_price
            
            # إنشاء عنصر المبيعة
            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total
            )
            
            db.session.add(sale_item)
            
            # تحديث المخزون
            product.quantity -= quantity
            
            total_amount += item_total
        
        # تحديث إجمالي المبيعة
        sale.total_amount = total_amount + sale.tax_amount - sale.discount_amount
        
        db.session.commit()
        
        return jsonify({
            'sale_id': sale.sale_id,
            'customer_id': sale.customer_id,
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
            'total_amount': float(sale.total_amount),
            'discount_amount': float(sale.discount_amount),
            'tax_amount': float(sale.tax_amount),
            'payment_method': sale.payment_method,
            'status': sale.status,
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            } for item in sale.sale_items]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    """الحصول على مبيعة محددة"""
    sale = Sale.query.get_or_404(sale_id)
    
    return jsonify({
        'sale_id': sale.sale_id,
        'customer_id': sale.customer_id,
        'customer_name': sale.customer.name if sale.customer else 'عميل غير محدد',
        'customer_phone': sale.customer.phone_number if sale.customer else None,
        'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
        'total_amount': float(sale.total_amount),
        'discount_amount': float(sale.discount_amount),
        'tax_amount': float(sale.tax_amount),
        'payment_method': sale.payment_method,
        'status': sale.status,
        'items': [{
            'sale_item_id': item.sale_item_id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'product_brand': item.product.brand,
            'product_model': item.product.model,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'total_price': float(item.total_price)
        } for item in sale.sale_items]
    })

@sales_bp.route('/sales/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    """تحديث مبيعة"""
    sale = Sale.query.get_or_404(sale_id)
    data = request.json
    
    try:
        sale.customer_id = data.get('customer_id', sale.customer_id)
        sale.discount_amount = data.get('discount_amount', sale.discount_amount)
        sale.tax_amount = data.get('tax_amount', sale.tax_amount)
        sale.payment_method = data.get('payment_method', sale.payment_method)
        sale.status = data.get('status', sale.status)
        
        # إعادة حساب الإجمالي
        items_total = sum(item.total_price for item in sale.sale_items)
        sale.total_amount = items_total + sale.tax_amount - sale.discount_amount
        
        db.session.commit()
        
        return jsonify({
            'sale_id': sale.sale_id,
            'customer_id': sale.customer_id,
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
            'total_amount': float(sale.total_amount),
            'discount_amount': float(sale.discount_amount),
            'tax_amount': float(sale.tax_amount),
            'payment_method': sale.payment_method,
            'status': sale.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    """حذف مبيعة (إلغاء المبيعة وإرجاع المخزون)"""
    sale = Sale.query.get_or_404(sale_id)
    
    try:
        # إرجاع المخزون
        for item in sale.sale_items:
            product = Product.query.get(item.product_id)
            if product:
                product.quantity += item.quantity
        
        db.session.delete(sale)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/today', methods=['GET'])
def get_today_sales():
    """الحصول على مبيعات اليوم"""
    today = datetime.now().date()
    sales = Sale.query.filter(Sale.sale_date >= today).all()
    
    total_amount = sum(sale.total_amount for sale in sales)
    
    return jsonify({
        'sales_count': len(sales),
        'total_amount': float(total_amount),
        'sales': [{
            'sale_id': sale.sale_id,
            'customer_name': sale.customer.name if sale.customer else 'عميل غير محدد',
            'total_amount': float(sale.total_amount),
            'payment_method': sale.payment_method,
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None
        } for sale in sales]
    })

@sales_bp.route('/sales/stats', methods=['GET'])
def get_sales_stats():
    """الحصول على إحصائيات المبيعات"""
    from sqlalchemy import func
    
    # إحصائيات عامة
    total_sales = Sale.query.count()
    total_revenue = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
    
    # مبيعات اليوم
    today = datetime.now().date()
    today_sales = Sale.query.filter(Sale.sale_date >= today).count()
    today_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= today
    ).scalar() or 0
    
    return jsonify({
        'total_sales': total_sales,
        'total_revenue': float(total_revenue),
        'today_sales': today_sales,
        'today_revenue': float(today_revenue)
    })

