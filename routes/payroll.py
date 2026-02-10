from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Employee, Dough, Oven
from datetime import datetime, date
from calendar import monthrange

payroll_bp = Blueprint('payroll', __name__, url_prefix='/payroll')

@payroll_bp.route('/')
@login_required
def index():
    # Bugungi sana
    today = date.today()
    sana = request.args.get('sana', today.strftime('%Y-%m-%d'))
    
    try:
        filter_date = datetime.strptime(sana, '%Y-%m-%d').date()
    except:
        filter_date = today
    
    # Barcha ishchilarni olish
    employees = Employee.query.filter_by(status='faol').all()
    
    # Har bir ishchi uchun hisobot
    hisobot = []
    
    for emp in employees:
        ishchi_malumot = {
            'id': emp.id,
            'ism': emp.ism,
            'lavozim': emp.lavozim,
            'stavka': float(emp.ish_haqqi_stavka) if emp.ish_haqqi_stavka else 0,
            'ish_soni': 0,
            'jami_ish_haqqi': 0
        }
        
        # Xamirchi bo'lsa - xamir qilgan qoplar soni
        if emp.lavozim == 'Xamirchi':
            xamirlar = Dough.query.filter_by(xodim_id=emp.id, sana=filter_date).all()
            jami_qop = sum([x.un_qopi for x in xamirlar])
            ishchi_malumot['ish_soni'] = jami_qop
            ishchi_malumot['jami_ish_haqqi'] = jami_qop * ishchi_malumot['stavka']
            ishchi_malumot['birlik'] = 'qop'
        
        # Tandirchi bo'lsa - tandirga kirgan non soni
        elif emp.lavozim == 'Tandirchi':
            tandirlar = Oven.query.filter_by(xodim_id=emp.id, sana=filter_date).all()
            jami_non = sum([t.kirdi for t in tandirlar])
            ishchi_malumot['ish_soni'] = jami_non
            ishchi_malumot['jami_ish_haqqi'] = jami_non * ishchi_malumot['stavka']
            ishchi_malumot['birlik'] = 'non'
        
        # Non yasovchi bo'lsa - chiqqan non soni
        elif emp.lavozim == 'Non yashovchi':
            from models import BreadMaking
            nonlar = BreadMaking.query.filter_by(xodim_id=emp.id, sana=filter_date).all()
            jami_non = sum([n.chiqqan_non for n in nonlar])
            ishchi_malumot['ish_soni'] = jami_non
            ishchi_malumot['jami_ish_haqqi'] = jami_non * ishchi_malumot['stavka']
            ishchi_malumot['birlik'] = 'non'
        
        hisobot.append(ishchi_malumot)
    
    return render_template('payroll/index.html', 
                         hisobot=hisobot, 
                         sana=filter_date.strftime('%Y-%m-%d'))

@payroll_bp.route('/detail/<int:employee_id>')
@login_required
def detail(employee_id):
    emp = Employee.query.get_or_404(employee_id)
    
    # Oy va yil
    yil = int(request.args.get('yil', date.today().year))
    oy = int(request.args.get('oy', date.today().month))
    
    # Oyning birinchi va oxirgi kuni
    _, oxirgi_kun = monthrange(yil, oy)
    boshlanish = date(yil, oy, 1)
    tugash = date(yil, oy, oxirgi_kun)
    
    # Kunlik hisobot
    kunlik_ish = []
    jami_ish_haqqi = 0
    
    for kun in range(1, oxirgi_kun + 1):
        ish_kuni = date(yil, oy, kun)
        ish_soni = 0
        
        if emp.lavozim == 'Xamirchi':
            xamirlar = Dough.query.filter_by(xodim_id=emp.id, sana=ish_kuni).all()
            ish_soni = sum([x.un_qopi for x in xamirlar])
        elif emp.lavozim == 'Tandirchi':
            tandirlar = Oven.query.filter_by(xodim_id=emp.id, sana=ish_kuni).all()
            ish_soni = sum([t.kirdi for t in tandirlar])
        elif emp.lavozim == 'Non yashovchi':
            from models import BreadMaking
            nonlar = BreadMaking.query.filter_by(xodim_id=emp.id, sana=ish_kuni).all()
            ish_soni = sum([n.chiqqan_non for n in nonlar])
        
        if ish_soni > 0:
            ish_haqqi = ish_soni * float(emp.ish_haqqi_stavka) if emp.ish_haqqi_stavka else 0
            jami_ish_haqqi += ish_haqqi
            kunlik_ish.append({
                'sana': ish_kuni.strftime('%d.%m.%Y'),
                'ish_soni': ish_soni,
                'ish_haqqi': ish_haqqi
            })
    
    return render_template('payroll/detail.html',
                         employee=emp,
                         kunlik_ish=kunlik_ish,
                         jami_ish_haqqi=jami_ish_haqqi,
                         yil=yil,
                         oy=oy)
