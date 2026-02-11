from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Sale, Customer, Cash, BreadType
from datetime import datetime
import requests
import json

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8443497785:AAG6UAJIzZv8HCSTKHqmYUe6dYRlIxu-Yn4"

# Customer to Telegram Group mapping
CUSTOMER_GROUPS = {
    "volidam": "-5191200114",
    "doston": "-5220067597",
    "sanjar patir": "-5119590423",
    "noilaxon": "-5136672687",
    "ziyo patir": "-5285503700",
    "turonboy": "-5210259696",
    "shirin patir": "-5189698467",
    "xojamboy": "-5176607925",
    "azizbek patir": "-5189297190",
    "akmal patir": "-5237628560",
    "shukurullo patir": "-5037602691",
    "abduqahor patir": "-5032698055",
    "milyon patir": "-5137038146",
    "ramshit patir": "-5226227796",
    "xusanboy patir": "-5282042883",
    "ishonch patir": "-5223718902",
    "soxib patir": "-4634207344",
    "sardor patir": "-5045869711",
    "lazzat patir": "-5191704673",
    "paxlavon patir": "-5125695734",
    "tanxo patir": "-5198380542",
    "alisher patir": "-5128082473",
    "asil patir": "-5051316785",
    "sarvar patir": "-5179819694",
    "javohir patir": "-5256511315",
    "kozim patir": "-5213481068",
    "klara opa": "-5052219586",
    "rashid patir": "-5036846652",
    "nodir patir": "-5283359473",
    "rokiya patir": "-5247807018",
    "xayotjon": "-5164251745",
    "shaxboz patir": "-5284778568",
    "osiyo patir": "-5156743302",
    "ozbegim": "-5273159369",
    "sadiya patir": "-5130791038",
    "ifor patir": "-5158654742",
    "diyor patir": "-5174351807",
    "lazzat patir2": "-5238995053",
    "mamura qirchin": "-5109056175",
    "dilafruz qirchin": "-5022506055",
    "saroy patir": "-5168265498",
    "abbosxon qirchin": "-5216949062",
    "nasiba qirchin": "-5235937864",
    "abdulatif": "-5189577253",
    "pungan baliq": "-5290608744",
    "tomchi dangara": "-5124985853",
    "benazir": "-5087901312"
}

def send_telegram_notification(customer_name, sale_data):
    """Send sale notification to customer's Telegram group"""
    # Find matching chat ID
    chat_id = None
    customer_lower = customer_name.lower().strip()
    
    for key, value in CUSTOMER_GROUPS.items():
        if key.lower() in customer_lower or customer_lower in key.lower():
            chat_id = value
            break
    
    if not chat_id:
        print(f"Telegram group not found for: {customer_name}")
        return False
    
    # Format message
    message = f"""
🍞 YANGI SOTUV

📦 Mijoz: {sale_data['mijoz']}
📅 Sana: {sale_data['sana']} {sale_data['vaqt']}
🥖 Non turi: {sale_data['non_turi']}
📊 Miqdor: {sale_data['miqdor']} dona
💰 Narx: {sale_data['narx_dona']:,.0f} so'm
💵 Jami: {sale_data['jami_summa']:,.0f} so'm
✅ To'landi: {sale_data['tolandi']:,.0f} so'm
❗ Qarz: {sale_data['qarz']:,.0f} so'm
👤 Xodim: {sale_data['xodim']}
"""
    
    # Send to Telegram
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Telegram sent to {customer_name}: {response.status_code}")
            return True
        else:
            print(f"❌ Telegram error for {customer_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram exception: {e}")
        return False

@sales_bp.route('/')
@login_required
def list_sales():
    sales = Sale.query.order_by(Sale.sana.desc()).all()
    return render_template('sales/list.html', sales=sales)

@sales_bp.route('/pay-debt/<int:sale_id>', methods=['GET', 'POST'])
@login_required
def pay_debt(sale_id):
    from decimal import Decimal
    
    sale = Sale.query.get_or_404(sale_id)
    
    if request.method == 'POST':
        payment = Decimal(str(request.form.get('payment', 0)))
        
        if payment <= 0:
            flash('To\'lov miqdori 0 dan katta bo\'lishi kerak', 'error')
            return redirect(url_for('sales.pay_debt', sale_id=sale_id))
        
        if payment > sale.qoldiq_qarz:
            flash('To\'lov miqdori qarzdan katta bo\'lmasligi kerak', 'error')
            return redirect(url_for('sales.pay_debt', sale_id=sale_id))
        
        # Update sale
        sale.tolandi += payment
        sale.qoldiq_qarz -= payment
        
        # Update customer debt
        customer = Customer.query.get(sale.mijoz_id)
        if customer:
            customer.jami_qarz -= payment
        
        # Add to cash
        last_cash = Cash.query.order_by(Cash.id.desc()).first()
        current_balance = last_cash.balans if last_cash else Decimal('0')
        new_cash = Cash(
            sana=datetime.now().date(),
            kirim=payment,
            balans=current_balance + payment,
            izoh=f"Qarz to'lovi: {customer.nomi if customer else 'Nomalum'}"
        )
        db.session.add(new_cash)
        db.session.commit()
        
        flash(f'{float(payment):,.0f} so\'m qarz to\'landi', 'success')
        return redirect(url_for('sales.list_sales'))
    
    return render_template('sales/pay_debt.html', sale=sale)

@sales_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        from decimal import Decimal
        
        mijoz_id = request.form.get('mijoz_id')
        non_turi = request.form.get('non_turi')
        miqdor = int(request.form.get('miqdor', 0))
        narx = Decimal(str(request.form.get('narx', 0)))
        tolandi_str = request.form.get('tolandi', '0')
        tolandi = Decimal(tolandi_str) if tolandi_str and tolandi_str.strip() else Decimal('0')
        
        jami = miqdor * narx
        qarz = jami - tolandi
        
        new_sale = Sale(
            sana=datetime.now().date(),
            mijoz_id=mijoz_id,
            non_turi=non_turi,
            miqdor=miqdor,
            narx_dona=narx,
            jami_summa=jami,
            tolandi=tolandi,
            qoldiq_qarz=qarz
        )
        
        # Update customer debt
        customer = Customer.query.get(mijoz_id)
        if customer:
            customer.jami_qarz += qarz
            customer.oxirgi_sana = datetime.now().date()
        
        # Add to cash
        if tolandi > 0:
            last_cash = Cash.query.order_by(Cash.id.desc()).first()
            current_balance = last_cash.balans if last_cash else 0
            new_cash = Cash(
                sana=datetime.now().date(),
                kirim=tolandi,
                balans=current_balance + tolandi,
                izoh=f"Sotuv: {customer.nomi if customer else 'Noma`lum'}"
            )
            db.session.add(new_cash)
            
        db.session.add(new_sale)
        db.session.commit()
        
        # Send Telegram notification
        sale_info = {
            "sotuv_id": new_sale.id,
            "sana": new_sale.sana.strftime('%d.%m.%Y'),
            "vaqt": datetime.now().strftime('%H:%M:%S'),
            "mijoz": customer.nomi if customer else "Noma'lum",
            "non_turi": non_turi,
            "miqdor": miqdor,
            "narx_dona": float(narx),
            "jami_summa": float(jami),
            "tolandi": float(tolandi),
            "qarz": float(qarz),
            "xodim": current_user.ism
        }
        send_telegram_notification(customer.nomi if customer else "Noma'lum", sale_info)
        
        flash('Sotuv muvaffaqiyatli amalga oshirildi')
        return redirect(url_for('sales.list_sales'))
    
    customers = Customer.query.filter_by(status='faol').all()
    bread_types = BreadType.query.order_by(BreadType.nomi).all()
    return render_template('sales/add.html', customers=customers, bread_types=bread_types)
