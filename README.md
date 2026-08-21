# eDOT Automation

Repository ini berisi implementasi automation testing sebagai bagian dari **Take Home Test QA Automation Engineer eDOT**.

Project dibagi menjadi dua bagian utama sesuai dengan requirement yang diberikan, yaitu automation untuk Web menggunakan Playwright dan Mobile menggunakan Maestro.

## Struktur Project

```
eDOT-Automation
├── Playwright/   # Web Automation
└── Maestro/      # Mobile Automation
```

## Combined Allure Report (Local)

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
make test-all          # menjalankan Web lalu Mobile ke allure-results/
make generate-all      # membuat allure-report/ dari hasil yang sudah ada
make open-all          # membuka combined report
make allure-all        # menjalankan seluruh alur, generate, lalu membuka report
```

`test-all` selalu membersihkan root `allure-results/` terlebih dahulu agar report hanya memuat execution saat ini. Kedua framework dijalankan secara serial; jika salah satu gagal, framework berikutnya tetap dijalankan dan command akhir tetap gagal setelah evidence dikumpulkan.

Evidence dalam combined report tetap melekat pada test asalnya:

- Playwright failure screenshot berada pada test terkait; setup login failure dapat ditemukan pada `Execution → Set up`.
- Maestro melampirkan `Maestro Execution Output` dan `Maestro Screen Recording` (`video/mp4`) pada step eksekusi Maestro.
- Pada Allure `SUITES`, `Playwright` menandai Web automation dan `Maestro` menandai Mobile automation.

Combined report ini adalah workflow lokal. GitHub Actions yang ada tetap menjalankan dan mempublikasikan report Playwright secara terpisah; mobile CI belum dikonfigurasi.

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

### 🚀CI/CD & Automation Report

Project Playwright telah diintegrasikan dengan GitHub Actions sehingga automation akan berjalan secara otomatis setiap kali terdapat perubahan pada branch main.

Workflow yang dijalankan meliputi:

Install seluruh dependency
Menjalankan Playwright automation secara headless
Generate Allure Report
Upload Allure Results sebagai workflow artifact
Publish Allure Report ke GitHub Pages

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

Flow dibuat secara modular agar mudah digunakan kembali (reusable) dan mudah dikembangkan.

Dokumentasi lengkap dapat dilihat pada:

> `Maestro/README.md`

---

## Tujuan Repository

Repository ini dibuat sebagai implementasi dari Take Home Test QA Automation Engineer eDOT dengan fokus pada:

- Manual Test Case Design
- Web Automation Testing
- Mobile Automation Testing
- Reporting
- Best Practice Automation Framework

---

## Author

**Muhamad Suryana**

QA Automation Engineer [www.msuryana.site](www.msuryana.site)
