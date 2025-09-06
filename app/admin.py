# File ini telah disempurnakan dengan logika untuk highlight, status kedaluwarsa, dan edit durasi.

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from firebase_admin import auth as firebase_auth, firestore
from datetime import datetime, timezone

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Akses ditolak. Silakan login sebagai admin.', 'error')
            return redirect(url_for('auth.login_page'))
        try:
            db = firestore.client()
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists and user_doc.to_dict().get('role') == 'admin':
                return f(*args, **kwargs)
            else:
                flash('Anda tidak memiliki hak akses untuk halaman ini.', 'error')
                return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Terjadi kesalahan saat verifikasi admin: {e}', 'error')
            return redirect(url_for('main.index'))
    return decorated_function

@admin.route('/dashboard')
@admin_required
def dashboard():
    db = firestore.client()
    users_list = []
    try:
        for user in firebase_auth.list_users().iterate_all():
            user_data = {'uid': user.uid, 'email': user.email, 'disabled': user.disabled, 'is_expired': False}
            user_doc = db.collection('users').document(user.uid).get()
            if user_doc.exists:
                firestore_data = user_doc.to_dict()
                user_data['role'] = firestore_data.get('role', 'user')
                expiration = firestore_data.get('expirationTimestamp')
                if expiration:
                    user_data['expiration_str'] = expiration.strftime('%d %B %Y')
                    # --- LOGIKA BARU UNTUK HIGHLIGHT ---
                    if datetime.now(timezone.utc) > expiration:
                        user_data['is_expired'] = True
                else:
                    user_data['expiration_str'] = 'Selamanya'
            else:
                user_data['role'], user_data['expiration_str'] = 'N/A', 'N/A'
            users_list.append(user_data)
    except Exception as e:
        flash(f'Gagal memuat daftar pengguna: {e}', 'error')
    return render_template('admin/dashboard.html', users=users_list)

@admin.route('/create-user', methods=['POST'])
@admin_required
def create_user():
    # ... (Fungsi ini tidak berubah, jadi saya persingkat)
    email = request.form.get('email')
    password = request.form.get('password')
    duration = request.form.get('duration')
    
    if not email or not password or not duration:
        flash('Semua kolom harus diisi.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        new_user = firebase_auth.create_user(email=email, password=password)
        db = firestore.client()
        user_data = {'role': 'user'}
        if duration == 'manual':
            date_str = request.form.get('expiration_date')
            if date_str:
                user_data['expirationTimestamp'] = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        elif duration != 'forever':
            days = int(duration.replace('d', ''))
            user_data['expirationTimestamp'] = datetime.now(timezone.utc) + timedelta(days=days)
        db.collection('users').document(new_user.uid).set(user_data)
        flash(f'Pengguna {email} berhasil dibuat!', 'success')
    except Exception as e:
        flash(f'Gagal membuat pengguna: {e}', 'error')
    return redirect(url_for('admin.dashboard'))

# --- FUNGSI BARU UNTUK EDIT DURASI ---
@admin.route('/edit-user-expiration/<uid>', methods=['POST'])
@admin_required
def edit_user_expiration(uid):
    """Memperbarui tanggal kedaluwarsa seorang pengguna di Firestore."""
    new_date_str = request.form.get('new_expiration_date')
    if not new_date_str:
        flash('Tanggal baru harus diisi.', 'error')
        return redirect(url_for('admin.dashboard'))
    try:
        db = firestore.client()
        user_ref = db.collection('users').document(uid)
        new_expiration_date = datetime.strptime(new_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        user_ref.update({'expirationTimestamp': new_expiration_date})
        flash('Durasi akses pengguna berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Gagal memperbarui durasi: {e}', 'error')
    return redirect(url_for('admin.dashboard'))

@admin.route('/toggle-user-status/<uid>', methods=['POST'])
@admin_required
def toggle_user_status(uid):
    """Mengaktifkan atau menonaktifkan akun pengguna di Firebase Authentication."""
    try:
        user = firebase_auth.get_user(uid)
        new_status = not user.disabled
        firebase_auth.update_user(uid, disabled=new_status)
        status_text = "dinonaktifkan" if new_status else "diaktifkan"
        flash(f'Pengguna {user.email} berhasil {status_text}.', 'success')
    except Exception as e:
        flash(f'Gagal mengubah status pengguna: {e}', 'error')
    return redirect(url_for('admin.dashboard'))

@admin.route('/delete-user/<uid>', methods=['POST'])
@admin_required
def delete_user(uid):
    try:
        firebase_auth.delete_user(uid)
        db = firestore.client()
        db.collection('users').document(uid).delete()
        flash('Pengguna berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Gagal menghapus pengguna: {e}', 'error')
    return redirect(url_for('admin.dashboard'))

