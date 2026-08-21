# eDOT Automation - Playwright + Pytest

Suite ini merupakan implementasi automation testing untuk aplikasi web eSuite menggunakan Playwright dan Pytest sebagai bagian dari Take Home Test QA Automation Engineer eDOT.

Framework dibangun menggunakan pendekatan Page Object Model (POM), session authentication (`storage_state`), serta mendukung pelaporan menggunakan Allure Report.

## Tujuan Project

- Memvalidasi alur `register company` di aplikasi eDOT.
- Mengecek bahwa company baru dapat dibuat, detailnya ditampilkan benar, dan dapat dihapus kembali.
- Menjaga test environment bersih dengan cleanup data setelah test selesai.

## Lingkup Test

Project ini mencakup:

- Login ke dashboard menggunakan credentials dari shared `.env` di repository root
- Membuka halaman `Companies`
- Menambahkan company baru melalui wizard multi-step, termasuk cascade Country → Province → City → District → Zone (label UI: Sub District) → Postal Code
- Memverifikasi company card dan status `Active`
- Membuka halaman detail company dan memvalidasi Tier 2 data: name, industry type, company type, address, postal code, email, dan phone
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
  - `ai_helper.py` - AI runtime generator, schema validation, retry, dan offline fallback
  - `config.py`
- `requirements.txt` - daftar dependency Python
- `pytest.ini` - konfigurasi pytest
- `Makefile` - perintah untuk menjalankan automation
- `.gitignore` - file dan folder yang tidak perlu dicommit
- `../.env` - shared environment runtime (tidak dicommit)

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

4. Buat file `.env` di root repository (`../.env` saat berada di folder `Playwright`). Contoh:

```bash
BASE_URL=https://your-edot-app-url
EMAIL=user@example.com
PASSWORD=yourpassword
EDOT_AI_API_KEY=optional-api-key
EDOT_AI_MODEL=gpt-4.1-mini
EDOT_TEST_DATA_SEED=20260819
EDOT_TEST_RUN_ID=optional-repeatable-run-id
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

- Jalankan Web dan Mobile dalam satu local Allure report dari root repository:

```bash
cd ..
make test-all
make generate-all
```

Hasil combined berada pada `../allure-results/` dan `../allure-report/`. Command Playwright individual di atas tetap memakai folder report lokal `Playwright/`.

- Buat laporan failure triage dari hasil Allure yang sudah ada (tidak menjalankan test dan tidak mengubah hasil test):

```bash
make triage
```

Laporan dibuat di `triage-report.md`. Jika `EDOT_AI_API_KEY` tidak tersedia atau provider AI gagal, laporan tetap dibuat dengan status **AI unavailable; human triage required** tanpa mengarang verdict.

- Buat evidence failure yang disengaja (hanya jalankan eksplisit; tidak dikoleksi oleh `make test`):

```bash
pytest tests/evidence_failure.py --alluredir=allure-results
make triage
```

- Hapus report dan cache hasil test:

```bash
make clean
```

## Cara Kerja Automation

- `conftest.py` memuat env dan menyediakan fixture `config`, `storage_state`, serta `authenticated_page`.
- `storage_state` menyimpan session login Playwright di `auth/storage_state.json` agar login tidak dilakukan berulang.
- `authenticated_page` membuka browser dengan storage state dan membuka `base_url`.
- Jika test gagal pada execution (`call`) dan menggunakan fixture `authenticated_page`, `pytest_runtest_makereport` menyimpan full-page screenshot ke `screenshots/<nama_test>.png` dan melampirkannya ke Allure.
- Jika login gagal saat fixture `storage_state` dibuat, screenshot disimpan ke `screenshots/storage_state_login_failure.png` dan dilampirkan ke Allure sebagai `Login Setup Failure Screenshot`. Karena failure terjadi pada fixture setup sebelum test body berjalan, attachment dapat ditemukan pada Allure melalui `Test → Execution → Set up → Login Setup Failure Screenshot`.
- `company_page.py` menggunakan Page Object Model untuk memisahkan locator dan aksi halaman.
- `data_generator.py` menggunakan AI pada runtime bila `EDOT_AI_API_KEY` tersedia. Output divalidasi schema; bila key tidak tersedia, provider gagal, atau output invalid setelah dua percobaan, generator memakai fallback Faker deterministik berdasarkan `EDOT_TEST_DATA_SEED`; `EDOT_TEST_RUN_ID` dapat diset untuk membuat ulang data yang sama. Bila tidak diset, run identifier dibuat unik agar company dari run sebelumnya tidak tertarget. Data yang dipakai test dilampirkan ke Allure sebagai `Actual Company Test Data`.
- `CustomerData` di `utils/data_generator.py` menyediakan contract AI/fallback tervalidasi (name, contact, address, phone) untuk integrasi Maestro pada tahap berikutnya; suite Maestro belum diubah dalam scope ini.
- `utils/failure_triage.py` dijalankan setelah suite untuk membaca `allure-results/*-result.json` secara read-only. AI hanya memberi proposal verdict (`Script/Environment Defect`, `Product Bug`, atau `Flaky`) untuk human review. Ia tidak dapat mengubah assertion, expected value, status test, source code, maupun membuat/menutup bug. Analisa mengikuti urutan: exception, locator, precondition, expected value, lalu reproducibility.

## Test Case Utama

- `tests/test_company.py`:
  - membuat company baru dengan data dummy dari `utils/data_generator.py`
  - memverifikasi button dan field pada wizard, termasuk Postal Code yang diisi otomatis setelah Zone dipilih
  - memverifikasi notifikasi success / redirect ke halaman companies
  - memeriksa card company yang dibuat
  - membuka halaman detail dan memverifikasi Tier 2 data company, termasuk Postal Code
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
- Bila `allure` tersedia, perintah `make allure` atau `make allure-headed` akan membuka report di browser.
- Folder `allure-results/` dan `allure-report/` tidak disimpan di repository karena merupakan artefak hasil eksekusi.
- Screenshot failure juga tersedia secara lokal pada folder `screenshots/`.
- Untuk failure pada test execution (`call`), buka test yang gagal di Allure lalu periksa attachment pada execution test tersebut.
- Untuk failure login saat pembuatan `storage_state`, buka test yang terdampak melalui `Allure → Test → Execution → Set up → Login Setup Failure Screenshot`. Attachment setup ini tidak harus muncul pada attachment execution/call utama.
- Evidence hasil eksekusi (Allure Report) dapat dilihat pada folder:

```
../docs/evidence/
```

## CI/CD

Project ini menggunakan GitHub Actions untuk menjalankan automation secara otomatis setiap kali terdapat push ke branch `main`.

Workflow akan:

1. Install seluruh dependency
2. Menjalankan Playwright automation
3. Generate Allure Report
4. Upload Allure Results sebagai artifact
5. Publish Allure Report ke GitHub Pages

### Live Report

https://suryana-code.github.io/eDOT-Automation/

### GitHub Actions

https://github.com/suryana-code/eDOT-Automation/actions

yang berisi screenshot hasil execution sebagai referensi reviewer.

## Catatan Tambahan

- Folder `auth/storage_state.json`, `screenshots/`, `allure-results/`, dan `allure-report/` diabaikan melalui `.gitignore` karena merupakan file runtime.
- Evidence hasil execution disimpan pada folder `docs/evidence/`.
- Jika terdapat perubahan UI atau locator, cukup lakukan pembaruan pada Page Object tanpa mengubah test case.
- Repository ini difokuskan pada implementasi automation sesuai requirement Take Home Test QA Automation Engineer eDOT.
