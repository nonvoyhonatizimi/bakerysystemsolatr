from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Dough, BreadMaking, Oven, Employee
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
    if request.method == 'POST':
        xodim_id = request.form.get('xodim_id')
        un_qop = request.form.get('un_qop', 0)
        xamir_soni = request.form.get('xamir_soni', 0)
        
        new_dough = Dough(
            sana=datetime.now().date(),
            xodim_id=xodim_id,
            un_qopi=un_qop,
            xamir_soni=xamir_soni
        )
        db.session.add(new_dough)
        db.session.commit()
        flash('Xamir ma\'lumoti qo\'shildi', 'success')
        return redirect(url_for('production.list_dough'))
    
    employees = Employee.query.filter_by(lavozim='Xamirchi').all()
    return render_template('production/dough_add.html', employees=employees)

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
