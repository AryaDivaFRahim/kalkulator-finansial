import os
from flask import Flask, session, redirect, url_for, flash, g
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'c8a2b7e1f4d9a3b6c8f2e7d1a4b9c8d3'

    # --- KONFIGURASI BARU UNTUK SESI ---
    # Menetapkan "umur" maksimal dari session cookie.
    # Setelah waktu ini, pengguna akan otomatis logout meskipun aktif.
    # Mari kita set ke 8 jam (jam kerja standar).
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    
    # Menetapkan batas waktu tidak aktif. Ganti angka 15 sesuai keinginan Anda.
    # Untuk pengujian, Anda bisa mengaturnya ke 1 menit (timedelta(minutes=1))
    app.config['SESSION_IDLE_TIMEOUT_MINUTES'] = 15


    if not firebase_admin._apps:
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            service_account_path = os.path.join(project_root, 'serviceAccountKey.json')
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print(">>> Firebase Admin SDK berhasil diinisialisasi.")
        except Exception as e:
            print(f">>> ERROR: Gagal menginisialisasi Firebase Admin SDK: {e}")

    # --- "PEMERIKSA GLOBAL" BARU ---
    @app.before_request
    def before_request_check():
        # Membuat sesi menjadi 'permanent' agar 'PERMANENT_SESSION_LIFETIME' berlaku
        session.permanent = True
        
        # Hanya periksa jika pengguna sudah login
        if 'user_id' in session:
            # Periksa apakah sesi sudah kadaluwarsa karena tidak aktif
            if 'last_activity' in session:
                last_activity = datetime.fromisoformat(session['last_activity'])
                timeout_minutes = app.config.get('SESSION_IDLE_TIMEOUT_MINUTES', 15)
                
                if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
                    session.clear()
                    flash('Sesi Anda telah berakhir karena tidak aktif. Silakan login kembali.', 'info')
                    return redirect(url_for('auth.login_page'))
            
            # Jika sesi masih aktif, perbarui waktu aktivitas terakhir
            session['last_activity'] = datetime.now().isoformat()

    # --- Mendaftarkan Blueprints ---
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app

