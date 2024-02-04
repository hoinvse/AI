# Import các thư viện và module cần thiết
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
from flask_babel import format_currency 

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tai_chinh.db'
app.config['SECRET_KEY'] = 'your-secret-key'

# Kết nối đến cơ sở dữ liệu
db = SQLAlchemy(app)

# Model cho giao dịch
class GiaoDich(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mo_ta = db.Column(db.String(100))
    so_tien = db.Column(db.Float)
    loai = db.Column(db.String(10))
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)

# Route chính
@app.route('/')
def index():
    thang_hien_tai = int(request.args.get('thang', datetime.now().month))
    giao_dich = GiaoDich.query.filter(db.func.extract('month', GiaoDich.ngay_tao) == thang_hien_tai).all()

    tong_thu_nhap = sum(gd.so_tien for gd in giao_dich if gd.loai == 'thu_nhap')
    tong_chi_phi = sum(gd.so_tien for gd in giao_dich if gd.loai == 'chi_phi')

    # Chuyển múi giờ thành Hồ Chí Minh (GMT+7)
    vn_tz = timezone('Asia/Ho_Chi_Minh')
    for gd in giao_dich:
        gd.ngay_tao = gd.ngay_tao.replace(tzinfo=timezone('UTC')).astimezone(vn_tz).strftime("%d/%m/%Y %H:%M:%S")
    
    return render_template('index.html', giao_dich=giao_dich, tong_thu_nhap=tong_thu_nhap, tong_chi_phi=tong_chi_phi, thang_hien_tai=thang_hien_tai)


# Route thêm giao dịch
@app.route('/them', methods=['GET', 'POST'])
def them_giao_dich():
    if request.method == 'POST':
        mo_ta = request.form['mo_ta']
        so_tien = float(request.form['so_tien'])
        loai = request.form['loai']
        ngay_tao = datetime.utcnow()
        gd = GiaoDich(mo_ta=mo_ta, so_tien=so_tien, loai=loai, ngay_tao=ngay_tao)
        db.session.add(gd)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('themgiaodich.html')

# Route xóa giao dịch
@app.route('/xoa/<int:id>')
def xoa_giao_dich(id):
    gd = GiaoDich.query.get_or_404(id)
    db.session.delete(gd)
    db.session.commit()
    return redirect(url_for('index'))

# Route cập nhật giao dịch
@app.route('/cap_nhat/<int:id>', methods=['GET', 'POST'])
def cap_nhat_giao_dich(id):
    gd = GiaoDich.query.get_or_404(id)
    if request.method == 'POST':
        gd.mo_ta = request.form['mo_ta']
        gd.so_tien = float(request.form['so_tien'])
        gd.loai = request.form['loai']
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('cap_nhat.html', gd=gd)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
