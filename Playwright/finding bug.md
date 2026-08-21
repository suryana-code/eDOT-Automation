# Log Temuan Bug

Dokumen ini digunakan untuk mencatat seluruh temuan bug pada automation atau exploratory testing eDOT. Setiap temuan baru diberi ID berurutan dan mengikuti template pada bagian **Template Bug Reusable**.

## Indeks Temuan

| ID      | Title                                                  | Module             | Severity | Priority | Status |
| ------- | ------------------------------------------------------ | ------------------ | -------- | -------- | ------ |
| BUG-001 | Company yang dihapus masih terlihat pada tab `Companies` | Company Management | Major    | High     | Open   |

## Template Bug yang Dapat Digunakan Kembali

Salin bagian berikut untuk membuat temuan baru. Ganti ID dengan nomor berikutnya, lalu lengkapi field yang relevan.

```markdown
## BUG-XXX: [Judul bug singkat dan dapat ditindaklanjuti]

### Ringkasan Issue

| Field             | Detail                                         |
| ----------------- | ---------------------------------------------- |
| **Issue Type**    | Bug                                            |
| **Status**        | Open                                           |
| **Priority**      | High / Medium / Low                            |
| **Severity**      | Blocker / Critical / Major / Minor / Trivial   |
| **Module**        | [Feature atau module]                          |
| **Component**     | [Page, flow, atau component]                   |
| **Environment**   | [URL, browser, OS, build, atau test environment] |
| **Reported Date** | [DD Bulan YYYY]                                |
| **Reporter**      | [Nama atau tim]                                |

### Deskripsi

[Apa yang salah dan pada kondisi apa hal tersebut terjadi?]

### Prakondisi

- [Account, data, izin, atau setup yang diperlukan]

### Langkah Reproduksi

1. [Langkah 1]
2. [Langkah 2]
3. [Langkah 3]

### Hasil yang Diharapkan

- [Perilaku yang diharapkan]

### Hasil Aktual

- [Perilaku yang diamati]

### Dampak

- [Dampak pada user, bisnis, data, atau testing]

### Evidence

- [Link screenshot, video, log, atau report]

### Area Investigasi yang Disarankan

- [Area UI, API, state, data, atau integrasi yang relevan]

### Kriteria Penerimaan

- [Kondisi yang mengonfirmasi bug sudah diperbaiki]

### Catatan Verifikasi

[Cakupan retest dan pemeriksaan regression setelah perbaikan.]
```

## BUG-001: Company yang Dihapus Masih Terlihat pada Tab Companies

### Ringkasan Issue

| Field             | Detail                                                 |
| ----------------- | ------------------------------------------------------ |
| **Issue Type**    | Bug                                                    |
| **Title**         | Company yang dihapus masih terlihat pada tab `Companies` |
| **Status**        | Open                                                   |
| **Priority**      | High                                                   |
| **Severity**      | Major                                                  |
| **Module**        | Company Management                                     |
| **Component**     | Companies tab / Company deletion                       |
| **Environment**   | eDOT web application                                   |
| **Reported Date** | 19 August 2026                                         |

### Deskripsi

Setelah company dihapus, company tersebut masih ditampilkan pada tab `Companies`. Saat user menekan **Manage** pada company yang masih tampil, data detail company bernilai `null`.

Hal ini menunjukkan bahwa record company mungkin sudah dihapus dari data sumber, tetapi daftar Companies tidak di-refresh atau menampilkan data stale.

### Prakondisi

- User sudah terautentikasi pada aplikasi web eDOT
- Setidaknya satu company ada pada tab **Companies**
- User memiliki izin untuk menghapus company

### Langkah Reproduksi

1. Buka tab **Companies**.
2. Pilih company yang sudah ada.
3. Hapus company.
4. Kembali ke atau refresh tab **Companies**.
5. Cari atau temukan company yang dihapus.
6. Tekan **Manage** pada company yang dihapus.

### Hasil yang Diharapkan

- Company yang dihapus hilang dari tab **Companies**
- Company yang dihapus tidak dapat ditemukan melalui daftar atau pencarian company
- Tidak ada aksi **Manage** yang tersedia untuk company yang dihapus

### Hasil Aktual

- Company yang dihapus tetap terlihat pada tab **Companies**
- User masih dapat menekan **Manage**
- Data detail company setelah membuka **Manage** bernilai `null`

### Dampak

- User dapat mengira bahwa penghapusan tidak berhasil
- Daftar Companies berisi record stale atau invalid
- User dapat membuka entry company yang tidak memiliki data detail valid
- Hal ini dapat mengurangi kepercayaan terhadap data company dan memicu tindakan lanjutan yang keliru

### Evidence

- Jam recording: [View video evidence](https://jam.dev/c/23b3b183-d28c-44eb-937f-9fd4101a8ea2)

### Area Investigasi yang Disarankan

- Refresh atau invalidate daftar Companies setelah response delete berhasil
- Verifikasi bahwa record yang dihapus tidak ada pada response API daftar Companies
- Periksa apakah daftar menggunakan cached data yang tidak dibersihkan setelah penghapusan
- Verifikasi bahwa UI menangani response detail company `null` dengan menghapus entry stale atau menampilkan not-found state yang sesuai

### Kriteria Penerimaan

- Company yang berhasil dihapus tidak lagi muncul pada tab **Companies** tanpa memerlukan restart browser penuh
- Refresh halaman tidak memunculkan kembali company yang dihapus
- Company yang dihapus tidak dapat dibuka melalui **Manage**
- Jika ditemukan entry stale, UI menampilkan not-found state yang jelas dan menghapus atau refresh entry invalid tersebut
- Company yang sudah ada tetap terlihat dan data detailnya tidak terpengaruh

### Catatan Verifikasi

Uji ulang flow penghapusan setelah perbaikan menggunakan keduanya:

- Company yang dihapus dari daftar Companies
- Refresh halaman setelah penghapusan

Pastikan company yang dihapus tidak ada di daftar dan tidak ada halaman detail `null` yang dapat dibuka.
