# File ini sekarang menjadi titik masuk utama untuk menjalankan aplikasi Flask Anda.
# Fungsinya sederhana: mengimpor dan menjalankan 'app' yang akan kita buat di dalam folder 'app'.

from app import create_app

# Membuat instance aplikasi menggunakan fungsi factory 'create_app'
# yang akan kita definisikan di file app/__init__.py
app = create_app()

# Menjalankan server pengembangan Flask
if __name__ == '__main__':
    # debug=True memungkinkan server untuk me-restart secara otomatis saat ada perubahan kode.
    # Ini sangat berguna selama masa pengembangan.
    app.run(debug=True)
