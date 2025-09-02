from flask import Blueprint, request, jsonify
from src.models.database import db, Sale, SaleItem, Product, Customer, Return
from datetime import datetime, timedelta
from sqlalchemy import func, and_

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales', methods=['GET'])
def get_sales():
    try:
        # فلترة حسب التاريخ
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        
        query = Sale.query
        
        if start_date:
            query = query.filter(Sale.sale_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Sale.sale_date <= datetime.fromisoformat(end_date))
        if customer_id:
            query = query.filter(Sale.customer_id == customer_id)
        if status:
            query = query.filter(Sale.status == status)
        
        sales = query.order_by(Sale.sale_date.desc()).all()
        
        sales_data = []
        for sale in sales:
            sales_data.append({
                'sale_id': sale.sale_id,
                'customer_id': sale.customer_id,
                'customer_name': sale.customer.name if sale.customer else 'عميل نقدي',
                'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
                'total_amount': float(sale.total_amount),
                'discount_amount': float(sale.discount_amount),
                'tax_amount': float(sale.tax_amount),
                'payment_method': sale.payment_method,
                'status': sale.status,
                'items_count': len(sale.sale_items)
            })
        
        return jsonify({'sales': sales_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales', methods=['POST'])
def create_sale():
    try:
        data = request.get_json()
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'يجب إضافة منتجات للفاتورة'}), 400
        
        # إنشاء الفاتورة
        sale = Sale(
            customer_id=data.get('customer_id'),
            total_amount=0,  # سيتم حسابه لاحقاً
            discount_amount=data.get('discount_amount', 0),
            tax_amount=data.get('tax_amount', 0),
            payment_method=data.get('payment_method', 'نقدي'),
            status=data.get('status', 'completed')
        )
        
        db.session.add(sale)
        db.session.flush()  # للحصول على sale_id
        
        total_amount = 0
        
        # إضافة عناصر الفاتورة
        for item_data in data['items']:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'المنتج غير موجود: {item_data["product_id"]}'}), 400
            
            quantity = item_data['quantity']
            if product.quantity < quantity:
                return jsonify({'error': f'الكمية المطلوبة غير متوفرة للمنتج: {product.name}'}), 400
            
            unit_price = item_data.get('unit_price', product.price)
            total_price = quantity * unit_price
            
            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            
            db.session.add(sale_item)
            
            # تحديث كمية المنتج
            product.quantity -= quantity
            
            total_amount += total_price
        
        # تحديث إجمالي الفاتورة
        sale.total_amount = total_amount + sale.tax_amount - sale.discount_amount
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء الفاتورة بنجاح',
            'sale_id': sale.sale_id,
            'total_amount': float(sale.total_amount)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    try:
        sale = Sale.query.get_or_404(sale_id)
        
        items_data = []
        for item in sale.sale_items:
            items_data.append({
                'sale_item_id': item.sale_item_id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            })
        
        sale_data = {
            'sale_id': sale.sale_id,
            'customer_id': sale.customer_id,
            'customer_name': sale.customer.name if sale.customer else 'عميل نقدي',
            'customer_phone': sale.customer.phone_number if sale.customer else None,
            'sale_date': sale.sale_date.isoformat() if sale.sale_date else None,
            'total_amount': float(sale.total_amount),
            'discount_amount': float(sale.discount_amount),
            'tax_amount': float(sale.tax_amount),
            'payment_method': sale.payment_method,
            'status': sale.status,
            'items': items_data
        }
        
        return jsonify(sale_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/<int:sale_id>/return', methods=['POST'])
def return_item():
    try:
        data = request.get_json()
        sale_item_id = data.get('sale_item_id')
        quantity = data.get('quantity')
        reason = data.get('reason', '')
        
        if not sale_item_id or not quantity:
            return jsonify({'error': 'معرف العنصر والكمية مطلوبان'}), 400
        
        sale_item = SaleItem.query.get_or_404(sale_item_id)
        
        # التحقق من الكمية
        returned_quantity = sum(ret.quantity for ret in sale_item.returns)
        if returned_quantity + quantity > sale_item.quantity:
            return jsonify({'error': 'الكمية المرجعة تتجاوز الكمية المباعة'}), 400
        
        # إنشاء المرتجع
        return_item = Return(
            sale_item_id=sale_item_id,
            quantity=quantity,
            reason=reason
        )
        
        db.session.add(return_item)
        
        # إعادة الكمية للمخزون
        product = sale_item.product
        product.quantity += quantity
        
        db.session.commit()
        
        return jsonify({'message': 'تم إرجاع المنتج بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/reports/daily', methods=['GET'])
def daily_sales_report():
    try:
        date = request.args.get('date', datetime.now().date().isoformat())
        target_date = datetime.fromisoformat(date).date()
        
        # مبيعات اليوم
        sales = Sale.query.filter(
            func.date(Sale.sale_date) == target_date
        ).all()
        
        total_sales = sum(sale.total_amount for sale in sales)
        total_transactions = len(sales)
        
        # أكثر المنتجات مبيعاً
        top_products = db.session.query(
            Product.name,
            func.sum(SaleItem.quantity).label('total_quantity')
        ).join(SaleItem).join(Sale).filter(
            func.date(Sale.sale_date) == target_date
        ).group_by(Product.product_id).order_by(
            func.sum(SaleItem.quantity).desc()
        ).limit(5).all()
        
        report_data = {
            'date': date,
            'total_sales': float(total_sales),
            'total_transactions': total_transactions,
            'top_products': [
                {'name': product.name, 'quantity': int(quantity)}
                for product, quantity in top_products
            ]
        }
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/sales/reports/monthly', methods=['GET'])
def monthly_sales_report():
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # بداية ونهاية الشهر
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # مبيعات الشهر
        sales = Sale.query.filter(
            and_(Sale.sale_date >= start_date, Sale.sale_date < end_date)
        ).all()
        
        total_sales = sum(sale.total_amount for sale in sales)
        total_transactions = len(sales)
        
        # مبيعات يومية
        daily_sales = db.session.query(
            func.date(Sale.sale_date).label('date'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            and_(Sale.sale_date >= start_date, Sale.sale_date < end_date)
        ).group_by(func.date(Sale.sale_date)).all()
        
        report_data = {
            'year': year,
            'month': month,
            'total_sales': float(total_sales),
            'total_transactions': total_transactions,
            'daily_sales': [
                {'date': day.date.isoformat(), 'total': float(day.total)}
                for day in daily_sales
            ]
        }
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

