from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Dough, BreadMaking, Oven, Employee, UnQoldiq, UnTuri
from datetime import datetime

production_bp = Blueprint('production', __name__, url_prefix='/production')

@production_bp.route('/dough')
@login_required
def list_dough():
    doughs = Dough.query.order_by(Dough.sana.desc()).all()
    return render_template('production/dough_list.html', doughs=doughs)

@production_bp.route('/dough/add', methods=['GET', 'POST'])
@login_required
def add_dough():
    # Mavjud un turlarini olish
    un_turlari = UnTuri.query.all()
    
    # Tanlangan un turi bo'yicha qoldiqni hisoblash
    tanlangan_un_turi = request.form.get('un_turi') if request.method == 'POST' else (un_turlari[0].nomi if un_turlari else 'Oddiy un')
    
    # Joriy un qoldigini olish (tanlangan tur bo'yicha)
    un_qoldiq = db.session.query(db.func.sum(UnQoldiq.qop_soni)).filter_by(un_turi=tanlangan_un_turi).scalar() or 0
    ishlatilgan_un = db.session.query(db.func.sum(Dough.un_qopi)).filter_by(un_turi=tanlangan_un_turi).scalar() or 0
    mavjud_un = un_qoldiq - ishlatilgan_un
    
    if request.method == 'POST':
        xodim_id = request.form.get('xodim_id')
        un_qop = int(request.form.get('un_qop', 0))
        xamir_soni = int(request.form.get('xamir_soni', 0))
        
        # Un yetarli ekanligini tekshirish
        if un_qop > mavjud_un:
            flash(f'Xatolik: {tanlangan_un_turi} dan faqat {mavjud_un} qop mavjud! {un_qop} qop kerak.', 'error')
            employees = Employee.query.filter_by(lavozim='Xamirchi').all()
            return render_template('production/dough_add.html', employees=employees, un_turlari=un_turlari, 
                                 tanlangan_un_turi=tanlangan_un_turi, mavjud_un=mavjud_un)
        
        new_dough = Dough(
            sana=datetime.now().date(),
            xodim_id=xodim_id,
            un_turi=tanlangan_un_turi,
            un_qopi=un_qop,
            xamir_soni=xamir_soni
        )
        db.session.add(new_dough)
        db.session.commit()
        flash(f'Xamir ma\'lumoti qo\'shildi. {tanlangan_un_turi}: {un_qop} qop ishlatildi. Qoldiq: {mavjud_un - un_qop} qop', 'success')
        return redirect(url_for('production.list_dough'))
    
    employees = Employee.query.filter_by(lavozim='Xamirchi').all()
    return render_template('production/dough_add.html', employees=employees, un_turlari=un_turlari, 
                         tanlangan_un_turi=tanlangan_un_turi, mavjud_un=mavjud_un)

@production_bp.route('/bread')
@login_required
def list_bread():
    breads = BreadMaking.query.order_by(BreadMaking.sana.desc()).all()
    return render_template('production/bread_list.html', breads=breads)

@production_bp.route('/bread/add', methods=['GET', 'POST'])
@login_required
def add_bread():
    if request.method == 'POST':
        xamir_id = request.form.get('xamir_id')
        xodim_id = request.form.get('xodim_id')
        chiqqan_non = request.form.get('chiqqan_non', 0)
        brak_non = request.form.get('brak_non', 0)
        
        new_bread = BreadMaking(
            sana=datetime.now().date(),
            xamir_id=xamir_id,
            xodim_id=xodim_id,
            chiqqan_non=chiqqan_non,
            brak_non=brak_non,
            sof_non=int(chiqqan_non) - int(brak_non)
        )
        db.session.add(new_bread)
        db.session.commit()
        flash('Non yasash ma\'lumoti qo\'shildi', 'success')
        return redirect(url_for('production.list_bread'))
    
    doughs = Dough.query.filter_by(status='tayyor').all()
    employees = Employee.query.filter_by(lavozim='Non yashovchi').all()
    return render_template('production/bread_add.html', doughs=doughs, employees=employees)

@production_bp.route('/oven')
@login_required
def list_oven():
    ovens = Oven.query.order_by(Oven.sana.desc()).all()
    return render_template('production/oven_list.html', ovens=ovens)

@production_bp.route('/oven/add', methods=['GET', 'POST'])
@login_required
def add_oven():
    if request.method == 'POST':
        tandirchi_id = request.form.get('tandirchi_id')
        tandir_raqami = request.form.get('tandir_raqami')
        kirgan = request.form.get('kirgan_non', 0)
        chiqqan = request.form.get('chiqqan_non', 0)
        
        new_oven = Oven(
            sana=datetime.now().date(),
            xodim_id=tandirchi_id,
            kirdi=kirgan,
            chiqdi=chiqqan,
            brak=int(kirgan) - int(chiqqan)
        )
        db.session.add(new_oven)
        db.session.commit()
        flash('Tandir ma\'lumoti qo\'shildi', 'success')
        return redirect(url_for('production.list_oven'))
    
    employees = Employee.query.filter_by(lavozim='Tandirchi').all()
    return render_template('production/oven_add.html', employees=employees)

# Un qoldigini boshqarish
@production_bp.route('/un-qoldiq')
@login_required
def un_qoldiq_list():
    # Har bir un turi bo'yicha qoldiqni hisoblash
    un_turlari = UnTuri.query.all()
    un_statistika = []
    
    for un_turi in un_turlari:
        kelgan = db.session.query(db.func.sum(UnQoldiq.qop_soni)).filter_by(un_turi=un_turi.nomi).scalar() or 0
        ishlatilgan = db.session.query(db.func.sum(Dough.un_qopi)).filter_by(un_turi=un_turi.nomi).scalar() or 0
        mavjud = kelgan - ishlatilgan
        un_statistika.append({
            'turi': un_turi.nomi,
            'kelgan': kelgan,
            'ishlatilgan': ishlatilgan,
            'mavjud': mavjud
        })
    
    records = UnQoldiq.query.order_by(UnQoldiq.sana.desc()).all()
    return render_template('production/un_qoldiq_list.html', records=records, un_statistika=un_statistika, un_turlari=un_turlari)

@production_bp.route('/un-qoldiq/add', methods=['GET', 'POST'])
@login_required
def add_un_qoldiq():
    un_turlari = UnTuri.query.all()
    
    if request.method == 'POST':
        un_turi = request.form.get('un_turi')
        qop_soni = int(request.form.get('qop_soni', 0))
        izoh = request.form.get('izoh', '')
        
        new_un = UnQoldiq(
            un_turi=un_turi,
            qop_soni=qop_soni,
            izoh=izoh,
            xodim_id=current_user.employee_id if current_user.employee_id else 1
        )
        db.session.add(new_un)
        db.session.commit()
        flash(f'{qop_soni} qop {un_turi} qo\'shildi', 'success')
        return redirect(url_for('production.un_qoldiq_list'))
    
    return render_template('production/un_qoldiq_add.html', un_turlari=un_turlari)

# Un turlarini boshqarish
@production_bp.route('/un-turlari')
@login_required
def un_turlari_list():
    turlar = UnTuri.query.all()
    return render_template('production/un_turlari_list.html', turlar=turlar)

@production_bp.route('/un-turlari/add', methods=['GET', 'POST'])
@login_required
def add_un_turi():
    if request.method == 'POST':
        nomi = request.form.get('nomi')
        
        if UnTuri.query.filter_by(nomi=nomi).first():
            flash(f'{nomi} allaqachon mavjud', 'error')
            return redirect(url_for('production.un_turlari_list'))
        
        new_turi = UnTuri(nomi=nomi)
        db.session.add(new_turi)
        db.session.commit()
        flash(f'{nomi} qo\'shildi', 'success')
        return redirect(url_for('production.un_turlari_list'))
    
    return render_template('production/un_turi_add.html')
