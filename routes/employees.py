from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Employee, User
from datetime import datetime
import random
import string

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@employees_bp.route('/')
@login_required
def list_employees():
    employees = Employee.query.all()
    return render_template('employees/list.html', employees=employees)

@employees_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        ism = request.form.get('ism')
        lavozim = request.form.get('lavozim')
        telefon = request.form.get('telefon')
        oylik = request.form.get('oylik', 0)
        ish_haqqi_stavka = request.form.get('ish_haqqi_stavka', 0)
        
        new_emp = Employee(
            ism=ism,
            lavozim=lavozim,
            telefon=telefon,
            oylik=oylik,
            ish_haqqi_stavka=ish_haqqi_stavka,
            ish_boshlanish=datetime.now().date()
        )
        db.session.add(new_emp)
        db.session.flush() # Get ID before commit
        
        # Create user account for employee
        login_id = f"emp{new_emp.id}"
        password = generate_password()
        
        new_user = User(
            login=login_id,
            parol=password,
            rol='operator',
            ism=ism,
            employee_id=new_emp.id
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Xodim muvaffaqiyatli qo\'shildi! LOGIN: {login_id}, PAROL: {password}', 'success')
        return redirect(url_for('employees.list_employees'))
    
    return render_template('employees/add.html')

@employees_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    if request.method == 'POST':
        emp.ism = request.form.get('ism')
        emp.lavozim = request.form.get('lavozim')
        emp.telefon = request.form.get('telefon')
        emp.oylik = request.form.get('oylik', 0)
        emp.ish_haqqi_stavka = request.form.get('ish_haqqi_stavka', 0)
        emp.status = request.form.get('status', 'faol')
        
        db.session.commit()
        flash('Xodim ma\'lumotlari yangilandi', 'success')
        return redirect(url_for('employees.list_employees'))
    
    return render_template('employees/edit.html', employee=emp)

@employees_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    
    # Xodimga bog'liq user ni o'chirish
    user = User.query.filter_by(employee_id=emp.id).first()
    if user:
        db.session.delete(user)
    
    db.session.delete(emp)
    db.session.commit()
    flash(f'{emp.ism} o\'chirildi', 'success')
    return redirect(url_for('employees.list_employees'))
