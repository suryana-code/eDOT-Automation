# eDOT Automation - Playwright + Pytest

Suite ini adalah automasi pengujian end-to-end sederhana untuk aplikasi eDOT dengan menggunakan Playwright dan Pytest.

## Tujuan Project

- Memvalidasi alur `register company` di aplikasi eDOT.
- Mengecek bahwa company baru dapat dibuat, detailnya ditampilkan benar, dan dapat dihapus kembali.
- Menjaga test environment bersih dengan cleanup data setelah test selesai.

## Lingkup Test

Project ini mencakup:

- Login ke dashboard menggunakan credentials dari `.env`
- Membuka halaman `Companies`
- Menambahkan company baru melalui wizard multi-step
- Memverifikasi company card dan status `Active`
- Membuka halaman detail company dan memvalidasi data
- Menghapus company yang dibuat dalam satu alur test

Bukan fokus project ini:

- coverage API atau database
- CI/CD pipeline
- test paralel multi-browser
- regression suite yang lengkap untuk semua halaman

## Struktur Project

- `conftest.py` - fixture pytest dan Playwright, session auth, screenshot on failure
- `pages/` - Page Object Model untuk setiap halaman utama
  - `login_page.py`
  - `dashboard_page.py`
  - `company_page.py`
- `tests/` - test case
  - `test_login.py`
  - `test_company.py`
- `utils/` - helper dan generator data
  - `data_generator.py`
  - `config.py`
- `requirements.txt` - daftar dependency Python
- `pytest.ini` - konfigurasi pytest
- `Makefile` - perintah untuk menjalankan automation
- `.gitignore` - file dan folder yang tidak perlu dicommit
- `.env` - environment runtime (tidak dicommit)

## Requirement

- Python 3.9+ (virtual environment direkomendasikan)
- Playwright browser binaries
- `allure` CLI bila ingin generate report

## Setup Lokal

1. Buat dan aktifkan virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Install Playwright browser binaries:

```bash
playwright install
```

4. Buat file `.env` di root project. Contoh:

```bash
BASE_URL=https://your-edot-app-url
EMAIL=user@example.com
PASSWORD=yourpassword
```

## Menjalankan Test

- Run semua test headless:

```bash
make test
```

- Run test dengan browser tampil:

```bash
make headed
```

- Run test dan lihat Allure report:

```bash
make allure
```

- Run test headed dan Allure report:

```bash
make allure-headed
```

- Hapus report dan cache hasil test:

```bash
make clean
```

## Cara Kerja Automation

- `conftest.py` memuat env dan menyediakan fixture `config`, `storage_state`, serta `authenticated_page`.
- `storage_state` menyimpan session login Playwright di `auth/storage_state.json` agar login tidak dilakukan berulang.
- `authenticated_page` membuka browser dengan storage state dan membuka `base_url`.
- Jika test gagal, screenshot otomatis disimpan ke folder `screenshots/` dan dilampirkan ke Allure.
- `company_page.py` menggunakan Page Object Model untuk memisahkan locator dan aksi halaman.

## Test Case Utama

- `tests/test_company.py`:
  - membuat company baru dengan data dummy dari `utils/data_generator.py`
  - memverifikasi button dan field pada wizard
  - memverifikasi notifikasi success / redirect ke halaman companies
  - memeriksa card company yang dibuat
  - membuka halaman detail dan memverifikasi data company
  - menghapus company dan memverifikasi deletion

## Asumsi dan Batasan

- Aplikasi eDOT accessible dari `BASE_URL`.
- Credential yang dipakai valid dan dapat login.
- API/backend tidak mengalami downtime saat test dijalankan.
- Test ini dibuat sebagai sanity/functional smoke test sederhana.

## Cara Menambah Test Baru

1. Tambahkan halaman baru di `pages/` bila diperlukan.
2. Buat locator baru dalam page object dan aksi helper.
3. Tambahkan test case di `tests/`.
4. Gunakan data generator di `utils/data_generator.py` bila butuh data random.

## Reporting

- Report Allure dihasilkan ke folder `allure-results/`.
- Bila `allure` tersedia, perintah `make allure` akan membuka report di browser.

## Catatan Tambahan

- Folder `auth/storage_state.json`, `screenshots/`, dan report Allure sudah di-ignore di `.gitignore`.
- Jika ada perubahan UI locator, update page object di `pages/company_page.py`.
- Ini adalah dokumentasi untuk project lokal, tanpa implementasi CI/CD.
