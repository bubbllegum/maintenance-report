from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3, qrcode, os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# === Flask-Login Setup ===
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Checklist Alat Medis").sheet1

# === Daftar Alat ===
daftar_alat = [
    {'id': 'ECG', 'nama': 'Elektrokardiograf'},
    {'id': 'USG', 'nama': 'Ultrasonografi'},
    {'id': 'IVP', 'nama': 'Infusion Pump'},
    {'id': 'DEF', 'nama': 'Defibrillator'},
    {'id': 'SPO2', 'nama': 'Pulse Oximeter'},
]

# === Routes ===

@app.route('/')
@login_required
def index():
    return render_template('index.html', daftar_alat=daftar_alat)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username sudah digunakan. Kembali dan coba lagi."
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            login_user(User(user[0], user[1]))
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/form/alat/<alat_id>')
@login_required
def form_alat(alat_id):
    # Cari data alat dari daftar
    alat = next((item for item in daftar_alat if item['id'] == alat_id), None)
    if alat is None:
        return "Alat tidak ditemukan", 404
    return render_template('form_alat.html', alat=alat)

@app.route('/submit_checklist', methods=['POST'])
@login_required
def submit_checklist():
    tanggal = request.form['tanggal']
    nama_alat = request.form['nama_alat']
    kondisi = request.form['kondisi']
    keterangan = request.form['keterangan']
    sheet.append_row([tanggal, nama_alat, kondisi, keterangan, current_user.username])
    return render_template('success.html')


@app.route('/qr/<alat_id>')
@login_required
def qr_code(alat_id):
    qr_url = url_for('form_alat', alat_id=alat_id, _external=True)
    img = qrcode.make(qr_url)
    qr_folder = 'static/qrcodes'
    os.makedirs(qr_folder, exist_ok=True)
    qr_path = os.path.join(qr_folder, f"{alat_id}.png")
    img.save(qr_path)
    return render_template('qr_display.html', alat_id=alat_id, qr_path=qr_path)

@app.route('/laporan')
@login_required
def laporan():
    data = sheet.get_all_records()
    return render_template('laporan.html', data=data)
if __name__ == '__main__':
    app.run(debug=True)
