from .auth import login_required
# Impor library Flask yang dibutuhkan
from flask import Blueprint,Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime, timedelta

# Inisialisasi aplikasi Flask
main = Blueprint('main', __name__)

# --- Fungsi Bantuan (opsional, tapi bagus untuk kerapian) ---
def format_rupiah(value):
    """Fungsi untuk memformat angka menjadi format mata uang Rupiah."""
    return f"Rp {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calculate_monthly_payment(principal, annual_rate, years):
    """Fungsi bantuan untuk menghitung cicilan bulanan."""
    if years <= 0 or principal < 0:
        return 0
    
    # Jika tidak ada pinjaman, tidak ada cicilan
    if principal == 0:
        return 0
        
    monthly_rate = (annual_rate / 100) / 12
    total_payments = years * 12

    if total_payments == 0:
        return principal

    if monthly_rate == 0:
        return principal / total_payments
    else:
        try:
            numerator = monthly_rate * ((1 + monthly_rate) ** total_payments)
            denominator = ((1 + monthly_rate) ** total_payments) - 1
            if denominator == 0:
                return float('inf')
            return principal * (numerator / denominator)
        except OverflowError:
            return float('inf')



# --- Rute Utama (Homepage) ---
@main.route('/')
def index():
    categories = {
        "Finance & Investment Calculators": [
            {"name": "Kalkulator Pertumbuhan Investasi", "url": "/investment-growth", "icon": "fa-chart-line", "endpoint": "investment_growth_calculator"},
            {"name": "Kalkulator Return on Investment (ROI)", "url": "/roi", "icon": "fa-sack-dollar", "endpoint": "roi_calculator"},
            {"name": "Kalkulator Anuitas", "url": "/annuity", "icon": "fa-calendar-alt", "endpoint": "annuity_calculator"},
            {"name": "Kalkulator Portofolio Investasi", "url": "/portfolio", "icon": "fa-briefcase", "endpoint": "portfolio_calculator"},
            {"name": "Kalkulator Profil Risiko", "url": "/risk-profile", "icon": "fa-user-shield", "endpoint": "risk_profile_calculator"},
        ],
        "Life & Family Planning": [
            {"name": "Perencana Dana Pendidikan Anak", "url": "/education-planner", "icon": "fa-graduation-cap", "endpoint": "education_planner_calculator"},
            {"name": "Perencana Dana Pernikahan", "url": "/wedding-planner", "icon": "fa-heart", "endpoint": "wedding_planner_calculator"},
            {"name": "Perencana Dana Kelahiran", "url": "/maternity-planner", "icon": "fa-baby-carriage", "endpoint": "maternity_planner"},
            {"name": "Anggaran Tujuan Finansial", "url": "/maternity-planner", "icon": "fa-book", "endpoint": "budget_planner"},
        ],
        "Loan & Mortgage Calculators": [
            {"name": "Kalkulator Cicilan KPR", "url": "/mortgage", "icon": "fa-home", "endpoint": "mortgage_calculator"},
            {"name": "Kalkulator Pinjaman Pribadi", "url": "/personal-loan", "icon": "fa-user-tie", "endpoint": "personal_loan_calculator"},
            {"name": "Kalkulator Kredit Mobil", "url": "/car-loan", "icon": "fa-car", "endpoint": "car_loan_calculator"},
            {"name": "Kalkulator Refinancing KPR", "url": "/refinance", "icon": "fa-sync-alt", "endpoint": "refinance_calculator"},
            {"name": "Kalkulator Pembayaran Pinjaman", "url": "/loan-payment", "icon": "fa-receipt", "endpoint": "loan_payment_calculator"},
        ],
        "Retirement Planning": [
            {"name": "Kalkulator Dana Pensiun", "url": "/retirement", "icon": "fa-piggy-bank", "endpoint": "retirement_calculator"},
            {"name": "Kalkulator Tabungan Pensiun", "url": "/retirement-saving", "icon": "fa-wallet", "endpoint": "retirement_saving_calculator"},
        ],
        "Savings & Budgeting": [
            {"name": "Kalkulator Alokasi Anggaran", "url": "/budget", "icon": "fa-clipboard-list", "endpoint": "budget_calculator"},
            {"name": "Kalkulator Tabungan", "url": "/savings", "icon": "fa-hand-holding-dollar", "endpoint": "savings_calculator"},
            {"name": "Kalkulator Dana Darurat", "url": "/emergency-fund", "icon": "fa-shield-halved", "endpoint": "emergency_fund_calculator"},
        ],
        "Tax Calculators": [
            {"name": "Kalkulator Pajak Penghasilan", "url": "/income-tax", "icon": "fa-percent", "endpoint": "income_tax_calculator"},
            {"name": "Kalkulator Pajak Properti", "url": "/property-tax", "icon": "fa-building-shield", "endpoint": "property_tax_calculator"},
            {"name": "Kalkulator Pajak Penjualan", "url": "/sales-tax", "icon": "fa-cash-register", "endpoint": "sales_tax_calculator"},
        ],
        "Financial Ratios & Metrics": [
            {"name": "Kalkulator Rasio Likuiditas", "url": "/liquidity-ratio", "icon": "fa-tachometer-alt", "endpoint": "liquidity_ratio_calculator"},
            {"name": "Kalkulator Rasio Utang", "url": "/debt-ratio", "icon": "fa-balance-scale-left", "endpoint": "debt_ratio_calculator"},
            {"name": "Kalkulator Rasio Profitabilitas", "url": "/profitability-ratio", "icon": "fa-chart-pie", "endpoint": "profitability_ratio_calculator"},
        ]
    }
    return render_template('index.html', categories=categories)

# --- Rute untuk Kalkulator Pertumbuhan Investasi ---
@main.route('/investment-growth', methods=['GET', 'POST'])
@login_required
def investment_growth_calculator():
    """
    Menangani logika untuk Kalkulator Pertumbuhan Investasi.
    SEKARANG: Menambahkan pembuatan tabel pertumbuhan per tahun.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            principal = float(request.form['principal'])
            annual_rate = float(request.form['annual_rate'])
            years = int(request.form['years'])
            
            # Hitung nilai akhir dan total bunga
            future_value = principal * ((1 + annual_rate / 100) ** years)
            total_interest = future_value - principal
            
            # --- LOGIKA BARU UNTUK TABEL PERTUMBUHAN ---
            growth_schedule = []
            current_balance = principal
            for year in range(1, years + 1):
                interest_earned = current_balance * (annual_rate / 100)
                ending_balance = current_balance + interest_earned
                
                growth_schedule.append({
                    "year": year,
                    "starting_balance": format_rupiah(current_balance),
                    "interest_earned": format_rupiah(interest_earned),
                    "ending_balance": format_rupiah(ending_balance)
                })
                
                current_balance = ending_balance # Saldo akhir tahun ini menjadi saldo awal tahun depan
            # --- AKHIR LOGIKA BARU ---

            result = {
                "principal": format_rupiah(principal),
                "future_value": format_rupiah(future_value),
                "total_interest": format_rupiah(total_interest),
                "years": years,
                "growth_schedule": growth_schedule # Kirim tabel ke template
            }
            
            return render_template('investment_growth.html', result=result)
        
        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('investment_growth.html', error=error_message)

    return render_template('investment_growth.html')

# --- Rute untuk Kalkulator Return on Investment (ROI) ---
@main.route('/roi', methods=['GET', 'POST'])
@login_required
def roi_calculator():
    """
    Menangani logika untuk Kalkulator ROI.
    Menghitung persentase return dari suatu investasi.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form dan ubah menjadi float
            initial_investment = float(request.form['initial_investment'])
            final_value = float(request.form['final_value'])

            # Pastikan investasi awal tidak nol untuk menghindari error pembagian
            if initial_investment == 0:
                error_message = "Investasi Awal tidak boleh nol."
                return render_template('roi.html', error=error_message)

            # Rumus ROI: ((Nilai Akhir - Investasi Awal) / Investasi Awal) * 100
            net_profit = final_value - initial_investment
            roi_percentage = (net_profit / initial_investment) * 100

            result = {
                "initial_investment": format_rupiah(initial_investment),
                "final_value": format_rupiah(final_value),
                "net_profit": format_rupiah(net_profit),
                "roi_percentage": f"{roi_percentage:.2f}%" # Format persentase
            }

            return render_template('roi.html', result=result)

        except (ValueError, KeyError):
            # Tangani jika input tidak valid atau kosong
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('roi.html', error=error_message)

    # Untuk metode GET, cukup tampilkan halaman kalkulatornya saja
    return render_template('roi.html')

# --- Rute untuk Kalkulator Anuitas ---
@main.route('/annuity', methods=['GET', 'POST'])
@login_required
def annuity_calculator():
    """
    Menangani logika untuk Kalkulator Anuitas (Pembayaran Pinjaman).
    SEKARANG: Menambahkan pembuatan tabel simulasi cicilan (amortisasi).
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form dan konversi
            principal = float(request.form['principal'])
            annual_rate = float(request.form['annual_rate'])
            years = int(request.form['years'])
            payments_per_year = int(request.form['payments_per_year'])

            # Hitung variabel dasar
            periodic_rate = (annual_rate / 100) / payments_per_year
            total_payments = years * payments_per_year

            # Hitung pembayaran periodik (cicilan)
            if periodic_rate == 0:
                payment = principal / total_payments if total_payments > 0 else 0
            else:
                numerator = periodic_rate * ((1 + periodic_rate) ** total_payments)
                denominator = ((1 + periodic_rate) ** total_payments) - 1
                if denominator == 0:
                    return render_template('annuity.html', error="Terjadi kesalahan perhitungan. Periksa input Anda.")
                payment = principal * (numerator / denominator)

            total_paid = payment * total_payments
            total_interest = total_paid - principal

            # --- LOGIKA BARU UNTUK MEMBUAT TABEL AMORTISASI ---
            amortization_schedule = []
            remaining_balance = principal

            if total_payments > 0 and payment > 0:
                for i in range(1, total_payments + 1):
                    interest_for_period = remaining_balance * periodic_rate
                    principal_for_period = payment - interest_for_period
                    remaining_balance -= principal_for_period

                    # Koreksi pembulatan di pembayaran terakhir
                    if i == total_payments:
                        principal_for_period += remaining_balance
                        remaining_balance = 0

                    amortization_schedule.append({
                        "period": i,
                        "principal_payment": format_rupiah(principal_for_period),
                        "interest_payment": format_rupiah(interest_for_period),
                        "remaining_balance": format_rupiah(remaining_balance)
                    })
            # --- AKHIR LOGIKA BARU ---

            result = {
                "principal": format_rupiah(principal),
                "payment": format_rupiah(payment),
                "total_paid": format_rupiah(total_paid),
                "total_interest": format_rupiah(total_interest),
                "payment_frequency": "Bulan" if payments_per_year == 12 else "Tahun" if payments_per_year == 1 else f"{payments_per_year} kali per tahun",
                "amortization_schedule": amortization_schedule # Kirim tabel ke template
            }

            return render_template('annuity.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('annuity.html', error=error_message)
            
    return render_template('annuity.html')

# --- Rute untuk Kalkulator Portofolio Investasi ---
@main.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio_calculator():
    """
    Menangani logika untuk Kalkulator Portofolio Investasi.
    SEKARANG: Mengirim data mentah ke client untuk kalkulasi grafik dinamis.
    """
    if request.method == 'POST':
        try:
            asset_names = request.form.getlist('asset_name')
            asset_values_str = request.form.getlist('asset_value')
            asset_returns_str = request.form.getlist('asset_return')

            assets = []
            chart_raw_data = [] # Data mentah untuk dikirim ke JavaScript
            for i in range(len(asset_names)):
                if asset_names[i] and asset_values_str[i] and asset_returns_str[i]:
                    value_float = float(asset_values_str[i])
                    return_float = float(asset_returns_str[i])
                    
                    # Menambahkan data ke list 'assets' untuk ditampilkan di tabel
                    assets.append({
                        "name": asset_names[i],
                        "value": value_float,
                        "return_rate": return_float
                    })
                    # Menambahkan data mentah yang lebih sederhana untuk grafik
                    chart_raw_data.append({
                        "name": asset_names[i],
                        "value": value_float,
                        "return_rate": return_float
                    })

            if not assets:
                return render_template('portfolio.html', error="Harap masukkan setidaknya satu aset investasi dengan lengkap.")

            total_portfolio_value = sum(asset['value'] for asset in assets)
            
            if total_portfolio_value == 0:
                 return render_template('portfolio.html', error="Total nilai portofolio tidak boleh nol.")

            weighted_average_return = 0
            for asset in assets:
                weight = (asset['value'] / total_portfolio_value)
                asset['weight'] = f"{weight * 100:.2f}%"
                weighted_average_return += weight * asset['return_rate']
                
                projected_value = asset['value'] * (1 + asset['return_rate'] / 100)
                asset['projected_value_formatted'] = format_rupiah(projected_value)
                asset['value_formatted'] = format_rupiah(asset['value'])

            projected_growth = total_portfolio_value * (weighted_average_return / 100)
            projected_total_value = total_portfolio_value + projected_growth

            result = {
                "assets": assets,
                "total_portfolio_value": format_rupiah(total_portfolio_value),
                "weighted_average_return": f"{weighted_average_return:.2f}%",
                "projected_growth": format_rupiah(projected_growth),
                "projected_total_value": format_rupiah(projected_total_value),
                # Mengirim data mentah ke template
                "chart_raw_data": chart_raw_data 
            }

            return render_template('portfolio.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            return render_template('portfolio.html', error="Input tidak valid. Pastikan semua kolom diisi dengan angka yang benar.")

    return render_template('portfolio.html')

# --- Rute untuk Kalkulator Cicilan KPR ---
@main.route('/mortgage', methods=['GET', 'POST'])
@login_required
def mortgage_calculator():
    """
    Menangani logika untuk Kalkulator Cicilan KPR.
    SEKARANG: Menambahkan pembuatan tabel simulasi cicilan (amortisasi).
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            property_price = float(request.form['property_price'])
            down_payment = float(request.form['down_payment'])
            annual_rate = float(request.form['annual_rate'])
            years = int(request.form['years'])

            # Validasi input
            if down_payment >= property_price:
                return render_template('mortgage.html', error="Uang muka harus lebih kecil dari harga properti.")

            # Hitung jumlah pinjaman dan variabel dasar
            principal = property_price - down_payment
            monthly_rate = (annual_rate / 100) / 12
            total_payments = years * 12

            # Hitung cicilan bulanan (logika anuitas)
            if monthly_rate == 0:
                monthly_payment = principal / total_payments
            else:
                numerator = monthly_rate * ((1 + monthly_rate) ** total_payments)
                denominator = ((1 + monthly_rate) ** total_payments) - 1
                if denominator == 0: # Menghindari ZeroDivisionError
                    return render_template('mortgage.html', error="Terjadi kesalahan perhitungan. Periksa kembali input Anda.")
                monthly_payment = principal * (numerator / denominator)

            total_paid = monthly_payment * total_payments
            total_interest = total_paid - principal

            # --- LOGIKA BARU UNTUK MEMBUAT TABEL AMORTISASI ---
            amortization_schedule = []
            remaining_balance = principal

            for i in range(1, total_payments + 1):
                interest_for_month = remaining_balance * monthly_rate
                principal_for_month = monthly_payment - interest_for_month
                remaining_balance -= principal_for_month

                # Koreksi pembulatan di pembayaran terakhir agar sisa pinjaman menjadi nol
                if i == total_payments:
                    principal_for_month += remaining_balance
                    remaining_balance = 0

                amortization_schedule.append({
                    "month": i,
                    "principal_payment": format_rupiah(principal_for_month),
                    "interest_payment": format_rupiah(interest_for_month),
                    "remaining_balance": format_rupiah(remaining_balance)
                })
            # --- AKHIR LOGIKA BARU ---

            result = {
                "property_price": format_rupiah(property_price),
                "down_payment": format_rupiah(down_payment),
                "principal": format_rupiah(principal),
                "monthly_payment": format_rupiah(monthly_payment),
                "total_paid": format_rupiah(total_paid),
                "total_interest": format_rupiah(total_interest),
                "years": years,
                "amortization_schedule": amortization_schedule # Kirim tabel ke template
            }

            return render_template('mortgage.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('mortgage.html', error=error_message)
            
    return render_template('mortgage.html')

# --- Rute untuk Kalkulator Pinjaman Pribadi ---
@main.route('/personal-loan', methods=['GET', 'POST'])
@login_required
def personal_loan_calculator():
    """
    Menangani logika untuk Kalkulator Pinjaman Pribadi,
    lengkap dengan tabel simulasi cicilan bulanan.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            loan_amount = float(request.form['loan_amount'])
            annual_rate = float(request.form['annual_rate'])
            years = int(request.form['years'])

            # Hitung variabel dasar (sama seperti KPR)
            principal = loan_amount
            monthly_rate = (annual_rate / 100) / 12
            total_payments = years * 12

            # Hitung cicilan bulanan
            if monthly_rate == 0:
                monthly_payment = principal / total_payments if total_payments > 0 else 0
            else:
                numerator = monthly_rate * ((1 + monthly_rate) ** total_payments)
                denominator = ((1 + monthly_rate) ** total_payments) - 1
                if denominator == 0:
                    return render_template('personal_loan.html', error="Terjadi kesalahan perhitungan. Periksa input Anda.")
                monthly_payment = principal * (numerator / denominator)

            total_paid = monthly_payment * total_payments
            total_interest = total_paid - principal

            # Buat tabel simulasi cicilan (amortisasi)
            amortization_schedule = []
            remaining_balance = principal

            if total_payments > 0:
                for i in range(1, total_payments + 1):
                    interest_for_month = remaining_balance * monthly_rate
                    principal_for_month = monthly_payment - interest_for_month
                    remaining_balance -= principal_for_month
                    
                    if i == total_payments:
                        principal_for_month += remaining_balance
                        remaining_balance = 0

                    amortization_schedule.append({
                        "month": i,
                        "principal_payment": format_rupiah(principal_for_month),
                        "interest_payment": format_rupiah(interest_for_month),
                        "remaining_balance": format_rupiah(remaining_balance)
                    })

            result = {
                "loan_amount": format_rupiah(loan_amount),
                "monthly_payment": format_rupiah(monthly_payment),
                "total_paid": format_rupiah(total_paid),
                "total_interest": format_rupiah(total_interest),
                "years": years,
                "amortization_schedule": amortization_schedule
            }

            return render_template('personal_loan.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('personal_loan.html', error=error_message)

    return render_template('personal_loan.html')

# --- Rute untuk Kalkulator Kredit Mobil ---
@main.route('/car-loan', methods=['GET', 'POST'])
@login_required
def car_loan_calculator():
    """
    Menangani logika untuk Kalkulator Kredit Mobil,
    lengkap dengan tabel simulasi cicilan bulanan.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            car_price = float(request.form['car_price'])
            down_payment = float(request.form['down_payment'])
            annual_rate = float(request.form['annual_rate'])
            years = int(request.form['years'])

            # Validasi input
            if down_payment >= car_price:
                return render_template('car_loan.html', error="Uang muka harus lebih kecil dari harga mobil.")

            # Hitung jumlah pinjaman (pokok hutang)
            principal = car_price - down_payment
            
            # Hitung variabel dasar
            monthly_rate = (annual_rate / 100) / 12
            total_payments = years * 12

            # Hitung cicilan bulanan
            if monthly_rate == 0:
                monthly_payment = principal / total_payments if total_payments > 0 else 0
            else:
                numerator = monthly_rate * ((1 + monthly_rate) ** total_payments)
                denominator = ((1 + monthly_rate) ** total_payments) - 1
                if denominator == 0:
                    return render_template('car_loan.html', error="Terjadi kesalahan perhitungan. Periksa input Anda.")
                monthly_payment = principal * (numerator / denominator)

            total_paid = monthly_payment * total_payments
            total_interest = total_paid - principal

            # Buat tabel simulasi cicilan (amortisasi)
            amortization_schedule = []
            remaining_balance = principal
            if total_payments > 0:
                for i in range(1, total_payments + 1):
                    interest_for_month = remaining_balance * monthly_rate
                    principal_for_month = monthly_payment - interest_for_month
                    remaining_balance -= principal_for_month
                    
                    if i == total_payments:
                        principal_for_month += remaining_balance
                        remaining_balance = 0

                    amortization_schedule.append({
                        "month": i,
                        "principal_payment": format_rupiah(principal_for_month),
                        "interest_payment": format_rupiah(interest_for_month),
                        "remaining_balance": format_rupiah(remaining_balance)
                    })

            result = {
                "car_price": format_rupiah(car_price),
                "down_payment": format_rupiah(down_payment),
                "principal": format_rupiah(principal),
                "monthly_payment": format_rupiah(monthly_payment),
                "total_paid": format_rupiah(total_paid),
                "total_interest": format_rupiah(total_interest),
                "years": years,
                "amortization_schedule": amortization_schedule
            }

            return render_template('car_loan.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('car_loan.html', error=error_message)

    return render_template('car_loan.html')

# --- Rute untuk Kalkulator Refinancing KPR ---
def generate_amortization_schedule(principal, annual_rate, years):
    """Fungsi bantuan untuk menghasilkan jadwal amortisasi lengkap."""
    schedule = []
    monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
    
    if monthly_payment == 0 or monthly_payment == float('inf'):
        return []

    remaining_balance = principal
    total_payments = years * 12
    monthly_rate = (annual_rate / 100) / 12

    for i in range(1, total_payments + 1):
        interest_for_month = remaining_balance * monthly_rate
        principal_for_month = monthly_payment - interest_for_month
        remaining_balance -= principal_for_month
        
        if i == total_payments:
            principal_for_month += remaining_balance
            remaining_balance = 0

        schedule.append({
            "month": i,
            "payment": monthly_payment,
            "interest": interest_for_month,
            "principal": principal_for_month,
            "balance": remaining_balance if remaining_balance > 0 else 0
        })
    return schedule

@main.route('/refinance', methods=['GET', 'POST'])
@login_required
def refinance_calculator():
    """
    Menangani logika untuk Kalkulator Refinancing KPR.
    SEKARANG: Menambahkan tabel simulasi perbandingan.
    """
    if request.method == 'POST':
        try:
            # Data KPR Saat Ini
            current_principal = float(request.form['current_principal'])
            current_rate = float(request.form['current_rate'])
            remaining_years = int(request.form['remaining_years'])
            
            # Data Penawaran KPR Baru
            new_rate = float(request.form['new_rate'])
            new_years = int(request.form['new_years'])
            refinance_cost = float(request.form['refinance_cost'])

            # Hitung cicilan
            current_payment = calculate_monthly_payment(current_principal, current_rate, remaining_years)
            new_payment = calculate_monthly_payment(current_principal, new_rate, new_years)
            
            # Buat jadwal amortisasi untuk kedua skenario
            old_schedule = generate_amortization_schedule(current_principal, current_rate, remaining_years)
            new_schedule = generate_amortization_schedule(current_principal, new_rate, new_years)

            # Gabungkan kedua jadwal untuk perbandingan
            comparison_schedule = []
            max_months = max(len(old_schedule), len(new_schedule))
            cumulative_savings = -refinance_cost  # Mulai dengan "kerugian" sebesar biaya refinancing

            for i in range(max_months):
                old_data = old_schedule[i] if i < len(old_schedule) else {"payment": 0, "balance": 0}
                new_data = new_schedule[i] if i < len(new_schedule) else {"payment": 0, "balance": 0}
                
                # Penghematan kumulatif bertambah setiap bulan
                cumulative_savings += old_data["payment"] - new_data["payment"]
                
                comparison_schedule.append({
                    "month": i + 1,
                    "old_payment": format_rupiah(old_data["payment"]),
                    "old_balance": format_rupiah(old_data["balance"]),
                    "new_payment": format_rupiah(new_data["payment"]),
                    "new_balance": format_rupiah(new_data["balance"]),
                    "cumulative_savings": format_rupiah(cumulative_savings)
                })

            monthly_savings = current_payment - new_payment
            
            result = {
                "current_payment": format_rupiah(current_payment),
                "new_payment": format_rupiah(new_payment),
                "monthly_savings": format_rupiah(monthly_savings),
                "refinance_cost": format_rupiah(refinance_cost),
                "monthly_savings_raw": monthly_savings,
                "comparison_schedule": comparison_schedule # Kirim tabel perbandingan
            }
            
            return render_template('refinance.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('refinance.html', error=error_message)

    return render_template('refinance.html')

# --- Rute untuk Kalkulator Pembayaran Pinjaman ---
@main.route('/loan-payment', methods=['GET', 'POST'])
@login_required
def loan_payment_calculator():
    """
    Menghitung dampak pembayaran tambahan terhadap jangka waktu
    dan total bunga pinjaman.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            principal = float(request.form['principal'])
            annual_rate = float(request.form['annual_rate'])
            years = int(request.form['years'])
            extra_payment = float(request.form.get('extra_payment', 0)) # Ambil pembayaran tambahan, default 0 jika kosong

            # 1. Hitung skenario standar (tanpa pembayaran tambahan)
            standard_monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
            standard_total_payments = years * 12
            standard_total_interest = (standard_monthly_payment * standard_total_payments) - principal

            # 2. Hitung skenario dengan pembayaran tambahan
            new_monthly_payment = standard_monthly_payment + extra_payment
            
            amortization_schedule = []
            remaining_balance = principal
            total_interest_paid_new = 0
            months_new = 0
            
            # Simulasi pelunasan dengan pembayaran tambahan
            while remaining_balance > 0:
                months_new += 1
                interest_for_month = remaining_balance * (annual_rate / 100 / 12)
                
                # Jika cicilan terakhir lebih kecil dari cicilan normal
                if remaining_balance + interest_for_month < new_monthly_payment:
                    principal_for_month = remaining_balance
                    current_payment = remaining_balance + interest_for_month
                    remaining_balance = 0
                else:
                    principal_for_month = new_monthly_payment - interest_for_month
                    current_payment = new_monthly_payment
                    remaining_balance -= principal_for_month

                total_interest_paid_new += interest_for_month
                
                amortization_schedule.append({
                    "month": months_new,
                    "payment": format_rupiah(current_payment),
                    "interest_payment": format_rupiah(interest_for_month),
                    "principal_payment": format_rupiah(principal_for_month),
                    "remaining_balance": format_rupiah(remaining_balance)
                })
                # Batas aman untuk mencegah infinite loop
                if months_new > standard_total_payments * 2:
                    break

            # 3. Hitung hasil perbandingan
            interest_saved = standard_total_interest - total_interest_paid_new
            months_saved = standard_total_payments - months_new
            
            # Konversi bulan yang dihemat ke format tahun dan bulan
            years_saved = months_saved // 12
            remaining_months_saved = months_saved % 12

            result = {
                "principal": format_rupiah(principal),
                "standard_monthly_payment": format_rupiah(standard_monthly_payment),
                "new_monthly_payment": format_rupiah(new_monthly_payment),
                "interest_saved": format_rupiah(interest_saved),
                "months_saved": months_saved,
                "years_saved_str": f"{years_saved} tahun, {remaining_months_saved} bulan",
                "original_term": f"{years} tahun ({standard_total_payments} bulan)",
                "new_term": f"{months_new // 12} tahun, {months_new % 12} bulan ({months_new} bulan)",
                "amortization_schedule": amortization_schedule
            }

            return render_template('loan_payment.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('loan_payment.html', error=error_message)

    return render_template('loan_payment.html')

# --- Rute untuk Kalkulator Dana Pensiun ---
@main.route('/retirement', methods=['GET', 'POST'])
@login_required
def retirement_calculator():
    """
    Menghitung dan memproyeksikan kecukupan dana pensiun,
    SEKARANG: menyertakan data untuk grafik perbandingan.
    """
    if request.method == 'POST':
        try:
            current_age = int(request.form['current_age'])
            retirement_age = int(request.form['retirement_age'])
            current_savings = float(request.form['current_savings'])
            monthly_contribution = float(request.form['monthly_contribution'])
            investment_rate = float(request.form['investment_rate'])
            monthly_expense = float(request.form['monthly_expense'])
            inflation_rate = float(request.form['inflation_rate'])
            
            if current_age >= retirement_age:
                return render_template('retirement.html', error="Usia saat ini harus lebih kecil dari usia pensiun.")

            # 1. Hitung proyeksi total dana yang akan terkumpul
            years_to_retirement = retirement_age - current_age
            months_to_retirement = years_to_retirement * 12
            monthly_inv_rate = (investment_rate / 100) / 12
            fv_current_savings = current_savings * ((1 + (investment_rate / 100)) ** years_to_retirement)
            if monthly_inv_rate == 0:
                 fv_monthly_contributions = monthly_contribution * months_to_retirement
            else:
                 fv_monthly_contributions = monthly_contribution * ((((1 + monthly_inv_rate) ** months_to_retirement) - 1) / monthly_inv_rate)
            projected_nest_egg = fv_current_savings + fv_monthly_contributions

            # 2. Hitung total dana yang dibutuhkan
            future_monthly_expense = monthly_expense * ((1 + (inflation_rate / 100)) ** years_to_retirement)
            required_nest_egg = (future_monthly_expense * 12) / 0.04
            shortfall_or_surplus = projected_nest_egg - required_nest_egg

            # 3. Buat tabel pertumbuhan DAN data untuk grafik
            growth_schedule = []
            chart_labels = []
            chart_projection_data = []
            
            balance = current_savings
            for year in range(1, years_to_retirement + 1):
                balance += monthly_contribution * 12
                interest_earned = balance * (investment_rate / 100)
                ending_balance = balance + interest_earned
                
                # Data untuk tabel
                growth_schedule.append({
                    "year": current_age + year,
                    "starting_balance": format_rupiah(balance - (monthly_contribution*12)),
                    "contributions": format_rupiah(monthly_contribution * 12),
                    "interest_earned": format_rupiah(interest_earned),
                    "ending_balance": format_rupiah(ending_balance)
                })
                
                # Data untuk grafik
                chart_labels.append(f"Usia {current_age + year}")
                chart_projection_data.append(round(ending_balance, 2))

                balance = ending_balance
            
            # 4. Susun data akhir untuk Chart.js
            chart_data = {
                "labels": chart_labels,
                "datasets": [
                    {
                        "label": "Proyeksi Dana Anda",
                        "data": chart_projection_data,
                        "borderColor": "#42a5f5",
                        "backgroundColor": "rgba(66, 165, 245, 0.2)",
                        "fill": True,
                        "tension": 0.2
                    },
                    {
                        "label": "Target Dana Dibutuhkan",
                        "data": [required_nest_egg] * years_to_retirement, # Garis lurus horizontal
                        "borderColor": "#ef5350",
                        "backgroundColor": "rgba(239, 83, 80, 0.1)",
                        "fill": False,
                        "borderDash": [10, 5] # Garis putus-putus
                    }
                ]
            }

            result = {
                "projected_nest_egg": format_rupiah(projected_nest_egg),
                "required_nest_egg": format_rupiah(required_nest_egg),
                "shortfall_or_surplus": format_rupiah(shortfall_or_surplus),
                "shortfall_or_surplus_raw": shortfall_or_surplus,
                "retirement_age": retirement_age,
                "growth_schedule": growth_schedule,
                "chart_data": chart_data # Kirim data grafik ke template
            }

            return render_template('retirement.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            return render_template('retirement.html', error="Input tidak valid. Harap isi semua kolom dengan benar.")

    return render_template('retirement.html')

# --- Rute untuk Kalkulator Tabungan Pensiun ---
@main.route('/retirement-saving', methods=['GET', 'POST'])
@login_required
def retirement_saving_calculator():
    """
    Menghitung berapa jumlah yang perlu ditabung setiap bulan
    untuk mencapai target dana pensiun.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            future_value_target = float(request.form['future_value_target'])
            current_age = int(request.form['current_age'])
            retirement_age = int(request.form['retirement_age'])
            investment_rate = float(request.form['investment_rate'])

            # Validasi dasar
            if current_age >= retirement_age:
                return render_template('retirement_saving.html', error="Usia saat ini harus lebih kecil dari usia pensiun.")

            # Hitung variabel waktu dan suku bunga
            years_to_save = retirement_age - current_age
            total_months = years_to_save * 12
            monthly_rate = (investment_rate / 100) / 12

            # Hitung kontribusi bulanan yang dibutuhkan
            # Rumus PMT = FV / ( ( ( (1+r)^n - 1 ) / r ) )
            if total_months <= 0:
                return render_template('retirement_saving.html', error="Jangka waktu menabung harus lebih dari 0.")

            if monthly_rate == 0:
                monthly_contribution_needed = future_value_target / total_months
            else:
                denominator = (((1 + monthly_rate) ** total_months) - 1) / monthly_rate
                if denominator == 0:
                     return render_template('retirement_saving.html', error="Terjadi kesalahan perhitungan. Periksa input Anda.")
                monthly_contribution_needed = future_value_target / denominator

            result = {
                "future_value_target": format_rupiah(future_value_target),
                "monthly_contribution_needed": format_rupiah(monthly_contribution_needed),
                "retirement_age": retirement_age,
                "years_to_save": years_to_save
            }

            return render_template('retirement_saving.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('retirement_saving.html', error=error_message)

    return render_template('retirement_saving.html')

# --- Rute untuk Kalkulator Anggaran Bulanan ---
@main.route('/budget')
@login_required
def budget_calculator():
    """
    Menampilkan halaman interaktif untuk kalkulator anggaran bulanan.
    Semua kalkulasi dilakukan di sisi client (JavaScript).
    """
    return render_template('budget.html')

# --- Rute untuk Kalkulator Tabungan ---
@main.route('/savings', methods=['GET', 'POST'])
@login_required
def savings_calculator():
    """
    Menghitung waktu yang dibutuhkan untuk mencapai target tabungan.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            target_goal = float(request.form['target_goal'])
            initial_savings = float(request.form['initial_savings'])
            monthly_contribution = float(request.form['monthly_contribution'])
            annual_rate = float(request.form.get('annual_rate', 0)) # Bunga bersifat opsional

            # Validasi dasar
            if target_goal <= initial_savings:
                return render_template('savings.html', error="Target tabungan harus lebih besar dari tabungan awal.")
            if monthly_contribution <= 0:
                return render_template('savings.html', error="Setoran bulanan harus lebih besar dari nol.")

            # Lakukan simulasi bulan per bulan
            months_needed = 0
            current_balance = initial_savings
            total_contributed = 0
            total_interest_earned = 0
            
            growth_schedule = []
            monthly_rate = (annual_rate / 100) / 12

            while current_balance < target_goal:
                months_needed += 1
                
                # Hitung bunga yang didapat bulan ini
                interest_this_month = current_balance * monthly_rate
                total_interest_earned += interest_this_month
                
                # Tambahkan setoran dan bunga
                current_balance += monthly_contribution + interest_this_month
                total_contributed += monthly_contribution
                
                # Tambahkan data ke tabel simulasi setiap akhir tahun atau pada bulan terakhir
                if months_needed % 12 == 0 or current_balance >= target_goal:
                    growth_schedule.append({
                        "period": f"{months_needed // 12} thn, {months_needed % 12} bln" if months_needed > 12 else f"{months_needed} bln",
                        "total_contributed": format_rupiah(total_contributed + initial_savings),
                        "total_interest": format_rupiah(total_interest_earned),
                        "ending_balance": format_rupiah(current_balance)
                    })

                # Pengaman untuk mencegah loop tak terbatas
                if months_needed > 1200: # Batas 100 tahun
                    return render_template('savings.html', error="Target terlalu tinggi atau setoran terlalu kecil, butuh lebih dari 100 tahun.")

            # Konversi total bulan ke format tahun dan bulan
            years_needed = months_needed // 12
            remaining_months = months_needed % 12
            time_str = f"{years_needed} tahun"
            if remaining_months > 0:
                time_str += f" dan {remaining_months} bulan"

            result = {
                "target_goal": format_rupiah(target_goal),
                "time_needed_str": time_str,
                "total_contributed": format_rupiah(initial_savings + total_contributed),
                "total_interest_earned": format_rupiah(total_interest_earned),
                "growth_schedule": growth_schedule
            }

            return render_template('savings.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('savings.html', error=error_message)

    return render_template('savings.html')

# --- Rute untuk Kalkulator Dana Darurat ---
@main.route('/emergency-fund', methods=['GET', 'POST'])
@login_required
def emergency_fund_calculator():
    """
    Menghitung target dana darurat ideal dan memberikan rencana menabung.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            monthly_expense = float(request.form['monthly_expense'])
            current_savings = float(request.form['current_savings'])
            risk_profile = request.form['risk_profile']

            # Tentukan pengali berdasarkan profil risiko
            multipliers = {
                "single_stable": 3,
                "married_stable": 6,
                "married_one_income": 9,
                "freelancer": 12
            }
            multiplier = multipliers.get(risk_profile, 6) # Default 6 jika tidak ada

            # Hitung target dana darurat dan kekurangannya
            target_fund = monthly_expense * multiplier
            shortfall = target_fund - current_savings

            # Siapkan rencana menabung jika ada kekurangan
            saving_plans = None
            if shortfall > 0:
                saving_plans = {
                    "plan_6_months": format_rupiah(shortfall / 6),
                    "plan_12_months": format_rupiah(shortfall / 12),
                    "plan_18_months": format_rupiah(shortfall / 18)
                }

            result = {
                "monthly_expense": format_rupiah(monthly_expense),
                "target_fund": format_rupiah(target_fund),
                "current_savings": format_rupiah(current_savings),
                "shortfall": format_rupiah(shortfall),
                "shortfall_raw": shortfall, # Untuk logika di template
                "multiplier": multiplier,
                "saving_plans": saving_plans
            }

            return render_template('emergency_fund.html', result=result)

        except (ValueError, KeyError, ZeroDivisionError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('emergency_fund.html', error=error_message)

    return render_template('emergency_fund.html')

# --- Rute untuk Kalkulator Pajak Penghasilan (PPh 21) ---
@main.route('/income-tax', methods=['GET', 'POST'])
@login_required
def income_tax_calculator():
    """
    Menghitung estimasi Pajak Penghasilan (PPh 21) untuk karyawan tetap
    berdasarkan peraturan UU HPP.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            monthly_salary = float(request.form['monthly_salary'])
            marital_status = request.form['marital_status']
            dependents = int(request.form.get('dependents', 0))

            # 1. Hitung Penghasilan Bruto Setahun
            gross_income = monthly_salary * 12

            # 2. Hitung Pengurang (Biaya Jabatan)
            position_cost = min(gross_income * 0.05, 6000000)

            # 3. Hitung Penghasilan Neto Setahun
            net_income = gross_income - position_cost

            # 4. Hitung Penghasilan Tidak Kena Pajak (PTKP)
            ptkp_individual = 54000000
            ptkp_married = 4500000 if marital_status == 'married' else 0
            ptkp_dependents = min(dependents, 3) * 4500000
            total_ptkp = ptkp_individual + ptkp_married + ptkp_dependents

            # 5. Hitung Penghasilan Kena Pajak (PKP)
            pkp = net_income - total_ptkp
            if pkp < 0:
                pkp = 0
            # Pembulatan ke bawah ribuan rupiah
            pkp = (pkp // 1000) * 1000

            # 6. Hitung Pajak Tahunan (PPh 21) dengan tarif progresif
            annual_tax = 0
            remaining_pkp = pkp
            tax_breakdown = []

            # Tarif Lapisan 1: 5%
            if remaining_pkp > 0:
                taxable_layer = min(remaining_pkp, 60000000)
                tax_layer = taxable_layer * 0.05
                annual_tax += tax_layer
                remaining_pkp -= taxable_layer
                tax_breakdown.append({'layer': '5% x ' + format_rupiah(taxable_layer), 'tax': format_rupiah(tax_layer)})
            
            # Tarif Lapisan 2: 15%
            if remaining_pkp > 0:
                taxable_layer = min(remaining_pkp, 250000000 - 60000000)
                tax_layer = taxable_layer * 0.15
                annual_tax += tax_layer
                remaining_pkp -= taxable_layer
                tax_breakdown.append({'layer': '15% x ' + format_rupiah(taxable_layer), 'tax': format_rupiah(tax_layer)})

            # Tarif Lapisan 3: 25%
            if remaining_pkp > 0:
                taxable_layer = min(remaining_pkp, 500000000 - 250000000)
                tax_layer = taxable_layer * 0.25
                annual_tax += tax_layer
                remaining_pkp -= taxable_layer
                tax_breakdown.append({'layer': '25% x ' + format_rupiah(taxable_layer), 'tax': format_rupiah(tax_layer)})

            # Tarif Lapisan 4: 30%
            if remaining_pkp > 0:
                taxable_layer = min(remaining_pkp, 5000000000 - 500000000)
                tax_layer = taxable_layer * 0.30
                annual_tax += tax_layer
                remaining_pkp -= taxable_layer
                tax_breakdown.append({'layer': '30% x ' + format_rupiah(taxable_layer), 'tax': format_rupiah(tax_layer)})

            # Tarif Lapisan 5: 35%
            if remaining_pkp > 0:
                tax_layer = remaining_pkp * 0.35
                annual_tax += tax_layer
                tax_breakdown.append({'layer': '35% x ' + format_rupiah(remaining_pkp), 'tax': format_rupiah(tax_layer)})

            monthly_tax = annual_tax / 12

            result = {
                "monthly_tax": format_rupiah(monthly_tax),
                "annual_tax": format_rupiah(annual_tax),
                "calculation": {
                    "gross_income": format_rupiah(gross_income),
                    "position_cost": format_rupiah(position_cost),
                    "net_income": format_rupiah(net_income),
                    "total_ptkp": format_rupiah(total_ptkp),
                    "pkp": format_rupiah(pkp),
                    "tax_breakdown": tax_breakdown
                }
            }
            return render_template('income_tax.html', result=result)

        except (ValueError, KeyError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan benar."
            return render_template('income_tax.html', error=error_message)

    return render_template('income_tax.html')

# --- Rute untuk Kalkulator Pajak Properti (PBB) ---
@main.route('/property-tax', methods=['GET', 'POST'])
@login_required
def property_tax_calculator():
    """
    Menghitung estimasi Pajak Bumi dan Bangunan (PBB-P2).
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            luas_tanah = float(request.form['luas_tanah'])
            njop_tanah_per_meter = float(request.form['njop_tanah_per_meter'])
            luas_bangunan = float(request.form['luas_bangunan'])
            njop_bangunan_per_meter = float(request.form['njop_bangunan_per_meter'])
            njoptkp = float(request.form['njoptkp'])
            tarif_pbb = float(request.form['tarif_pbb'])

            # 1. Hitung NJOP Bumi dan Bangunan
            njop_tanah = luas_tanah * njop_tanah_per_meter
            njop_bangunan = luas_bangunan * njop_bangunan_per_meter

            # 2. Hitung NJOP Total sebagai dasar pengenaan PBB
            njop_total = njop_tanah + njop_bangunan

            # 3. Hitung Dasar Pengenaan Pajak (DPP)
            dpp = njop_total - njoptkp
            if dpp < 0:
                dpp = 0

            # 4. Hitung PBB yang terutang
            pbb_terutang = (tarif_pbb / 100) * dpp

            result = {
                "pbb_terutang": format_rupiah(pbb_terutang),
                "calculation": {
                    "njop_tanah": format_rupiah(njop_tanah),
                    "njop_bangunan": format_rupiah(njop_bangunan),
                    "njop_total": format_rupiah(njop_total),
                    "njoptkp": format_rupiah(njoptkp),
                    "dpp": format_rupiah(dpp)
                }
            }
            return render_template('property_tax.html', result=result)

        except (ValueError, KeyError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('property_tax.html', error=error_message)

    return render_template('property_tax.html')

# --- Rute untuk Kalkulator Pajak Penjualan ---
@main.route('/sales-tax', methods=['GET', 'POST'])
@login_required
def sales_tax_calculator():
    """
    Menghitung jumlah pajak penjualan (PPN) dan total harga.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari form
            price_before_tax = float(request.form['price_before_tax'])
            tax_rate = float(request.form['tax_rate'])

            # Hitung jumlah pajak dan total harga
            tax_amount = price_before_tax * (tax_rate / 100)
            total_price = price_before_tax + tax_amount

            result = {
                "price_before_tax": format_rupiah(price_before_tax),
                "tax_rate": f"{tax_rate}%",
                "tax_amount": format_rupiah(tax_amount),
                "total_price": format_rupiah(total_price)
            }
            return render_template('sales_tax.html', result=result)

        except (ValueError, KeyError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('sales_tax.html', error=error_message)

    return render_template('sales_tax.html')

# --- Rute untuk Kalkulator Rasio Likuiditas ---
@main.route('/liquidity-ratio', methods=['GET', 'POST'])
@login_required
def liquidity_ratio_calculator():
    """
    Menghitung tiga rasio likuiditas utama: Current Ratio, Quick Ratio, dan Cash Ratio.
    """
    if request.method == 'POST':
        try:
            # Ambil data Aset Lancar
            cash = float(request.form.get('cash', 0))
            receivables = float(request.form.get('receivables', 0))
            inventory = float(request.form.get('inventory', 0))
            other_current_assets = float(request.form.get('other_current_assets', 0))
            
            # Ambil data Utang Lancar
            payables = float(request.form.get('payables', 0))
            short_term_debt = float(request.form.get('short_term_debt', 0))
            other_current_liabilities = float(request.form.get('other_current_liabilities', 0))

            # 1. Hitung Total Aset dan Utang Lancar
            total_current_assets = cash + receivables + inventory + other_current_assets
            total_current_liabilities = payables + short_term_debt + other_current_liabilities
            
            if total_current_liabilities == 0:
                return render_template('liquidity_ratio.html', error="Total Utang Lancar tidak boleh nol untuk menghitung rasio.")

            # 2. Hitung Rasio-rasio
            # a. Current Ratio (Rasio Lancar)
            current_ratio = total_current_assets / total_current_liabilities
            if current_ratio >= 2:
                cr_status = ("Sangat Baik", "#2e7d32") # Hijau Tua
            elif current_ratio >= 1:
                cr_status = ("Baik", "#66bb6a") # Hijau
            else:
                cr_status = ("Perlu Perhatian", "#ef5350") # Merah

            # b. Quick Ratio (Rasio Cepat)
            quick_assets = total_current_assets - inventory
            quick_ratio = quick_assets / total_current_liabilities
            if quick_ratio >= 1:
                qr_status = ("Baik", "#66bb6a")
            elif quick_ratio >= 0.8:
                qr_status = ("Cukup", "#ffa726") # Oranye
            else:
                qr_status = ("Rendah", "#ef5350")

            # c. Cash Ratio (Rasio Kas)
            cash_ratio = cash / total_current_liabilities
            if cash_ratio >= 0.5:
                crr_status = ("Sangat Kuat", "#2e7d32")
            elif cash_ratio >= 0.2:
                crr_status = ("Cukup", "#ffa726")
            else:
                crr_status = ("Rendah", "#ef5350")

            result = {
                "current_ratio": {"value": f"{current_ratio:.2f}", "status": cr_status[0], "color": cr_status[1]},
                "quick_ratio": {"value": f"{quick_ratio:.2f}", "status": qr_status[0], "color": qr_status[1]},
                "cash_ratio": {"value": f"{cash_ratio:.2f}", "status": crr_status[0], "color": crr_status[1]},
                "calculation": {
                    "total_current_assets": format_rupiah(total_current_assets),
                    "total_current_liabilities": format_rupiah(total_current_liabilities)
                }
            }
            return render_template('liquidity_ratio.html', result=result)

        except (ValueError, KeyError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('liquidity_ratio.html', error=error_message)

    return render_template('liquidity_ratio.html')

# --- Rute untuk Kalkulator Rasio Utang ---
@main.route('/debt-ratio', methods=['GET', 'POST'])
@login_required
def debt_ratio_calculator():
    """
    Menghitung Debt-to-Asset Ratio dan Debt-to-Equity Ratio.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari Laporan Posisi Keuangan (Neraca)
            total_debt = float(request.form.get('total_debt', 0))
            total_assets = float(request.form.get('total_assets', 0))
            total_equity = float(request.form.get('total_equity', 0))

            # Validasi input
            if total_assets == 0:
                return render_template('debt_ratio.html', error="Total Aset tidak boleh nol untuk menghitung rasio.")
            
            # 1. Debt-to-Asset Ratio
            # Mengukur persentase aset yang dibiayai oleh utang.
            debt_to_asset_ratio = total_debt / total_assets
            if debt_to_asset_ratio < 0.4:
                dta_status = ("Sehat", "#2e7d32") # Hijau Tua
            elif debt_to_asset_ratio <= 0.6:
                dta_status = ("Waspada", "#ffa726") # Oranye
            else:
                dta_status = ("Berisiko", "#ef5350") # Merah
            
            # 2. Debt-to-Equity Ratio
            # Membandingkan utang dengan modal sendiri.
            if total_equity == 0:
                # Jika ekuitas nol dan utang ada, rasio dianggap tak terhingga (sangat berisiko)
                debt_to_equity_ratio = float('inf') if total_debt > 0 else 0
            else:
                debt_to_equity_ratio = total_debt / total_equity
            
            if debt_to_equity_ratio < 1.0:
                dte_status = ("Sehat", "#2e7d32")
            elif debt_to_equity_ratio <= 2.0:
                dte_status = ("Waspada", "#ffa726")
            else:
                dte_status = ("Berisiko", "#ef5350")

            result = {
                "debt_to_asset": {"value": f"{debt_to_asset_ratio:.2f}", "status": dta_status[0], "color": dta_status[1]},
                "debt_to_equity": {"value": f"{debt_to_equity_ratio:.2f}" if debt_to_equity_ratio != float('inf') else "∞", "status": dte_status[0], "color": dte_status[1]},
            }
            return render_template('debt_ratio.html', result=result)

        except (ValueError, KeyError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('debt_ratio.html', error=error_message)

    return render_template('debt_ratio.html')

# --- Rute untuk Kalkulator Rasio Profitabilitas ---
@main.route('/profitability-ratio', methods=['GET', 'POST'])
@login_required
def profitability_ratio_calculator():
    """
    Menghitung Net Profit Margin, Return on Assets, dan Return on Equity.
    """
    if request.method == 'POST':
        try:
            # Ambil data dari Laporan Laba Rugi dan Neraca
            net_income = float(request.form.get('net_income', 0))
            revenue = float(request.form.get('revenue', 0))
            total_assets = float(request.form.get('total_assets', 0))
            total_equity = float(request.form.get('total_equity', 0))

            # Validasi input
            if revenue == 0:
                return render_template('profitability_ratio.html', error="Pendapatan (Revenue) tidak boleh nol.")

            # 1. Net Profit Margin (NPM)
            npm = (net_income / revenue) * 100
            if npm > 20:
                npm_status = ("Sangat Baik", "#2e7d32")
            elif npm > 10:
                npm_status = ("Baik", "#66bb6a")
            elif npm > 5:
                npm_status = ("Cukup", "#ffa726")
            else:
                npm_status = ("Rendah", "#ef5350")
            
            # 2. Return on Assets (ROA)
            if total_assets == 0: roa = 0
            else: roa = (net_income / total_assets) * 100
            
            if roa > 20:
                roa_status = ("Sangat Efisien", "#2e7d32")
            elif roa > 5:
                roa_status = ("Efisien", "#66bb6a")
            else:
                roa_status = ("Kurang Efisien", "#ef5350")

            # 3. Return on Equity (ROE)
            if total_equity == 0: roe = 0
            else: roe = (net_income / total_equity) * 100
            
            if roe > 20:
                roe_status = ("Sangat Baik", "#2e7d32")
            elif roe > 15:
                roe_status = ("Baik", "#66bb6a")
            else:
                roe_status = ("Perlu Ditingkatkan", "#ffa726")

            result = {
                "npm": {"value": f"{npm:.2f}%", "status": npm_status[0], "color": npm_status[1]},
                "roa": {"value": f"{roa:.2f}%", "status": roa_status[0], "color": roa_status[1]},
                "roe": {"value": f"{roe:.2f}%", "status": roe_status[0], "color": roe_status[1]},
            }
            return render_template('profitability_ratio.html', result=result)

        except (ValueError, KeyError):
            error_message = "Input tidak valid. Harap isi semua kolom dengan angka."
            return render_template('profitability_ratio.html', error=error_message)

    return render_template('profitability_ratio.html')

@main.route('/risk-profile')
@login_required
def risk_profile_calculator():
    """
    Menampilkan halaman kuesioner interaktif untuk menentukan profil risiko.
    """
    return render_template('risk_profile.html')

@main.route('/education-planner')
@login_required
def education_planner_calculator():
    """
    Menampilkan halaman perencana dana pendidikan yang komprehensif.
    Semua logika utama ada di sisi client (JavaScript).
    """
    return render_template('education_planner.html')

@main.route('/wedding-planner')
@login_required
def wedding_planner_calculator():
    """Menampilkan halaman Perencana Dana Pernikahan."""
    return render_template('wedding_planner.html')

@main.route('/maternity-planner')
@login_required
def maternity_planner():
    """Menampilkan halaman Perencana Dana Kelahiran."""
    return render_template('maternity_planner.html')

@main.route('/budget-planner')
@login_required
def budget_planner():
    """Menampilkan halaman Perencana Dana."""
    return render_template('budget_planner.html')