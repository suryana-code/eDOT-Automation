# eDOT Automation

Repository ini berisi implementasi automation testing sebagai bagian dari **Take Home Test QA Automation Engineer eDOT**.

Project dibagi menjadi dua bagian utama sesuai dengan requirement yang diberikan, yaitu automation untuk Web menggunakan Playwright dan Mobile menggunakan Maestro.

## Struktur Project

```
eDOT-Automation
├── Playwright/   # Automation Web
└── Maestro/      # Automation Mobile
```

## Allure Report Gabungan (Lokal)

Web dan mobile tetap dapat dijalankan secara individual dari folder framework masing-masing:

```bash
cd Playwright && make test
cd Playwright && make headed
cd Playwright && make allure-headed

cd Maestro && make test
cd Maestro && make allure
```

Untuk satu execution lokal yang menggabungkan Playwright dan Maestro ke dalam satu report Allure, jalankan dari root repository:

```bash
make test-all          # menjalankan Web + Mobile parallel dan merge ke .allure/results/
make generate-all      # membuat .allure/report/ dari hasil yang sudah ada
make open-all          # membuka combined report
make allure-all        # menjalankan seluruh alur, generate, lalu membuka report
```

`test-all` selalu membersihkan `.allure/` terlebih dahulu agar report hanya memuat execution saat ini. Playwright dan Maestro dijalankan parallel ke `.allure/playwright-results/` dan `.allure/maestro-results/`, lalu digabung ke `.allure/results/`. Jika salah satu gagal, command akhir tetap gagal setelah evidence dikumpulkan.

Evidence dalam combined report tetap melekat pada test asalnya:

- Playwright failure screenshot berada pada test terkait; setup login failure dapat ditemukan pada `Execution → Set up`
- Maestro melampirkan `Maestro Execution Output` dan `Maestro Screen Recording` (`video/mp4`) pada step eksekusi Maestro
- Pada Allure `SUITES`, `Playwright` menandai Web automation dan `Maestro` menandai Mobile automation

Report standalone tetap berada di folder framework masing-masing. Report gabungan adalah workflow lokal; seluruh `.allure/` merupakan runtime artifact dan tidak di-commit. GitHub Actions yang ada tetap menjalankan dan mempublikasikan report Playwright secara terpisah; mobile CI belum dikonfigurasi.

---

## 📌 Playwright

Folder **Playwright** berisi implementasi automation testing untuk aplikasi web **eSuite** menggunakan:

- Python
- Pytest
- Playwright
- Page Object Model (POM)
- Allure Report

Automation mencakup skenario:

- Login
- Create Company
- Verify Company Detail
- Delete Company

Dokumentasi lengkap dapat dilihat pada:

> `Playwright/README.md`

### 🚀CI/CD dan Automation Report

Project Playwright telah diintegrasikan dengan GitHub Actions sehingga automation akan berjalan secara otomatis setiap kali terdapat perubahan pada branch main.

Workflow yang dijalankan meliputi:

- Menginstal seluruh dependency
- Menjalankan automation Playwright secara headless
- Membuat Allure Report
- Mengunggah Allure Results sebagai workflow artifact
- Mempublikasikan Allure Report ke GitHub Pages

#### Live Report

🌐 https://suryana-code.github.io/eDOT-Automation/

#### GitHub Actions

## ⚙️ https://github.com/suryana-code/eDOT-Automation/actions

## 📌 Maestro

Folder **Maestro** berisi implementasi automation testing untuk aplikasi Android **eWork SFA** menggunakan Maestro.

Automation akan mencakup skenario:

- Login
- Create Customer
- Verify Customer

Flow dibuat secara modular agar mudah digunakan kembali dan mudah dikembangkan.

Dokumentasi lengkap dapat dilihat pada:

> `Maestro/README.md`

---

## Tujuan Repository

Repository ini dibuat sebagai implementasi dari Take Home Test QA Automation Engineer eDOT dengan fokus pada:

- Manual Test Case Design
- Automation Testing Web
- Automation Testing Mobile
- Reporting
- Best Practice Automation Framework

---

## Author

**Muhamad Suryana**

QA Automation Engineer [www.msuryana.site](www.msuryana.site)
