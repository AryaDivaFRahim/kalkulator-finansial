from flask import Blueprint, session, redirect, url_for, render_template, flash, request, jsonify
from functools import wraps
from firebase_admin import firestore, auth as firebase_auth
from datetime import datetime, timezone

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Anda harus login untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('auth.login_page'))
        try:
            user = firebase_auth.get_user(user_id)
            if user.disabled:
                session.clear()
                flash('Akun Anda telah dinonaktifkan.', 'error')
                return redirect(url_for('auth.login_page'))
            db = firestore.client()
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                if 'expirationTimestamp' in user_data:
                    expiration = user_data.get('expirationTimestamp')
                    if expiration and datetime.now(timezone.utc) > expiration:
                        session.clear()
                        return redirect(url_for('auth.access_denied'))
            else:
                session.clear()
                flash('Data detail akun Anda tidak ditemukan.', 'error')
                return redirect(url_for('auth.login_page'))
        except Exception as e:
            session.clear()
            flash(f'Terjadi kesalahan saat verifikasi sesi: {e}', 'error')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login')
def login_page():
    return render_template('login.html')

@auth.route('/session-login', methods=['POST'])
def session_login():
    try:
        id_token = request.json['token']
        decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
        uid = decoded_token['uid']
        
        # --- LOGIKA BARU: MENYIMPAN PERAN (ROLE) PENGGUNA ---
        user_record = firebase_auth.get_user(uid)
        db = firestore.client()
        user_doc = db.collection('users').document(uid).get()

        session['user_id'] = uid
        session['user_email'] = user_record.email
        session['display_name'] = user_record.email.split('@')[0].capitalize()
        session['user_disabled'] = user_record.disabled
        
        if user_doc.exists:
            firestore_data = user_doc.to_dict()
            # Simpan peran pengguna (role) ke dalam sesi. Defaultnya adalah 'user'.
            session['user_role'] = firestore_data.get('role', 'user')
            expiration = firestore_data.get('expirationTimestamp')
            session['user_expiration'] = expiration.strftime('%d %B %Y') if expiration else 'Selamanya'
        else:
            session['user_role'] = 'user' # Jika tidak ada di Firestore, anggap user biasa
            session['user_expiration'] = 'N/A'

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Gagal memverifikasi: {e}"}), 401

@auth.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        firebase_auth.revoke_refresh_tokens(user_id)
    session.clear()
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/access-denied')
def access_denied():
    return render_template('access_denied.html')

