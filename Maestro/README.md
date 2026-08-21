# Automation Mobile Maestro

## Gambaran Umum

Repository ini berisi suite test mobile Maestro untuk aplikasi eWork SFA.
Test mencakup:

- Login dan verifikasi dashboard
- Pembuatan customer dengan validasi Tier 2
- Verifikasi customer setelah dibuat

## Setup dan Menjalankan Test

### Prasyarat

- Maestro CLI terinstal dan tersedia melalui `maestro --version`
- Versi Maestro yang digunakan dan sudah diverifikasi lokal: `2.6.1`
- Device Android yang terhubung terlihat melalui `adb devices`
- Package aplikasi `id.edot.ework` terinstal pada device target
- Dependency Python diinstal dengan `pip install -r requirements.txt`
- Allure CLI hanya diperlukan saat menggunakan `make allure`

### Environment variable

Buat file `.env` lokal bersama di root repository (`../.env` saat dijalankan dari `Maestro/`) dengan credential dan konfigurasi aplikasi yang diperlukan oleh flow login:

- `APP_ID` (example: `id.edot.ework`)
- `COMPANY_ID`
- `USER_NAME`
- `PASSWORD`

`pytest/conftest.py` secara eksplisit memuat `.env` root repository melalui `python-dotenv`. Jangan menaruh credential pada command YAML atau melakukan commit credential lokal.

### Fallback account Take Home Test

Flow Maestro saat ini menggunakan fallback company/account yang disediakan dalam Take Home Test, bukan company yang dibuat oleh flow Web: Company ID `5049209` dan username `salesmanqaauto`. Password hanya disimpan pada `.env` lokal di root dan sengaja tidak didokumentasikan di sini. Sesuai catatan assignment, fallback ini dapat kedaluwarsa.

### Menjalankan melalui Makefile

```bash
make test
```

Jalankan command ini dari direktori `Maestro/`. Command tersebut setara dengan:

```bash
pytest -v -s pytest/test_mobile.py
```

### CI Maestro

Workflow manual tersedia di `.github/workflows/maestro.yaml`. CI memakai Ubuntu, Android Emulator API 35 `google_apis` `x86_64`, dan Maestro `2.6.1`.

CI tetap memakai wrapper lokal yang sama:

```bash
cd Maestro
make test
```

Sebelum menjalankan workflow, buat GitHub Secrets berikut:

- `MAESTRO_APP_ID`
- `MAESTRO_COMPANY_ID`
- `MAESTRO_USER_NAME`
- `MAESTRO_PASSWORD`
- `MAESTRO_APK_URL`
- `MAESTRO_APK_SHA256`

`MAESTRO_APK_URL` harus mengarah ke asset GitHub Release `edot-maestro-apk.zip`. ZIP berisi `base.apk`, `split_config.arm64_v8a.apk`, dan `split_config.xxhdpi.apk`. Workflow memverifikasi SHA256, memasang split APK menggunakan `adb install-multiple -r`, lalu memastikan package `id.edot.ework` tersedia sebelum menjalankan test.

Workflow meng-upload `allure-results/`, `recordings/`, dan `allure-report/` bila tersedia. Artifact tetap dikumpulkan saat test gagal. Kompatibilitas split ARM64 pada emulator `x86_64` API 35 belum terverifikasi sampai workflow dijalankan pertama kali.

### Allure Report Web + Mobile Gabungan

Untuk menjalankan Playwright dan Maestro secara parallel ke satu direktori result Allure lokal, jalankan command berikut dari root repository:

```bash
make test-all
make generate-all
```

`make test-all` menulis result sementara masing-masing framework ke `.allure/playwright-results/` dan `.allure/maestro-results/`, lalu menggabungkan eksekusi saat ini ke `.allure/results/`. `make generate-all` membuat report HTML gabungan di `.allure/report/`. Hal ini tidak mengubah command Maestro individual di atas atau workflow CI Playwright yang sudah ada.

### Menjalankan Flow Maestro Langsung untuk Debugging Login

Skenario customer lengkap harus dijalankan melalui Pytest karena Pytest membuat data customer dinamis. Untuk debugging flow login reusable secara langsung, export terlebih dahulu nilai dari `.env` root bersama:

```bash
set -a
. ../.env
set +a
maestro test -p android flows/login/login.yaml
```

### Membuat dan Membuka Allure Report

```bash
make allure
```

`pytest.ini` menulis result Allure ke `allure-results/`; `make allure` menjalankan wrapper Pytest yang sama dan membuka result tersebut dengan `allure serve`.

Jika Allure CLI belum terinstal, jalankan `make test` dan instal Allure sebelum membuka `allure-results/`.

### Catatan

- `.env` root repository menyediakan credential dan konfigurasi aplikasi untuk wrapper Pytest
- Faker pada `pytest/conftest.py` membuat data customer dinamis untuk setiap eksekusi test
- Pytest memuat `.env`, menyiapkan data, memanggil Maestro, dan melampirkan data serta log ke Allure
- File YAML di bawah `flows/` berisi langkah automation mobile
- Login dipisahkan ke flow bersama pada `flows/login/login.yaml`
- Verifikasi customer dilakukan pada **New Customer List** karena tidak ada halaman detail setelah registrasi. Flow hanya memverifikasi `OUTLET_NAME`; Address tidak diassert karena tidak reliable pada UI/card yang tersedia
- `startRecording` dan `stopRecording` merekam Login dan Create Customer ke subdirektori unik di `recordings/`
- Wrapper melampirkan output `text/plain` dan recording `video/mp4` pada step Allure `Run Maestro main flow`
- Jika tersedia, `ffmpeg`/`ffprobe` hanya memakai MP4 H.264 terkompresi dengan resolusi yang sama; jika tidak, MP4 asli dipakai
