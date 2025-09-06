import os
import json
from flask import Flask, session, redirect, url_for, flash
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'c8a2b7e1f4d9a3b6c8f2e7d1a4b9c8d3'

    # --- KONFIGURASI SESI ---
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_IDLE_TIMEOUT_MINUTES'] = 15

    # --- INISIALISASI FIREBASE (Logika Baru untuk Render & Lokal) ---
    if not firebase_admin._apps:
        try:
            # Coba dapatkan kredensial dari Environment Variable (untuk Render)
            creds_json_str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

            if creds_json_str:
                # Jika berjalan di Render, muat kredensial dari string JSON
                creds_dict = json.loads(creds_json_str)
                cred = credentials.Certificate(creds_dict)
                print(">>> Inisialisasi Firebase dari Environment Variable (Render)...")
            else:
                # Jika berjalan di lokal, muat kredensial dari file
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                service_account_path = os.path.join(project_root, 'serviceAccountKey.json')
                cred = credentials.Certificate(service_account_path)
                print(">>> Inisialisasi Firebase dari file lokal...")
            
            firebase_admin.initialize_app(cred)
            print(">>> Firebase Admin SDK berhasil diinisialisasi.")

        except Exception as e:
            print(f">>> ERROR: Gagal menginisialisasi Firebase Admin SDK: {e}")

    # --- "PEMERIKSA GLOBAL" UNTUK SESI ---
    @app.before_request
    def before_request_check():
        session.permanent = True
        
        if 'user_id' in session:
            if 'last_activity' in session:
                last_activity = datetime.fromisoformat(session['last_activity'])
                timeout_minutes = app.config.get('SESSION_IDLE_TIMEOUT_MINUTES', 15)
                
                if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
                    session.clear()
                    flash('Sesi Anda telah berakhir karena tidak aktif. Silakan login kembali.', 'info')
                    return redirect(url_for('auth.login_page'))
            
            session['last_activity'] = datetime.now().isoformat()

    # --- Mendaftarkan Blueprints ---
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
