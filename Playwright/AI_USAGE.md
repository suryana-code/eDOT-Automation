# Penggunaan AI

Dokumen ini menjelaskan fitur AI yang benar-benar diimplementasikan pada project Playwright. AI bersifat opsional saat runtime dan tidak pernah digunakan untuk mengubah hasil test.

## 1. Pembuatan Test Data dengan AI

### Tujuan dan cakupan data

`utils/ai_helper.py` menghasilkan test data bisnis bergaya Indonesia yang tervalidasi. Data yang didukung adalah:

- **Data company:** nama company, email, nomor ponsel Indonesia, alamat jalan, industry, company type, language, cascade alamat yang didukung aplikasi, postal code, dan branch name.
- **Data customer:** nama, contact, alamat jalan, dan nomor ponsel Indonesia. Ini adalah contract tervalidasi untuk pekerjaan mobile di masa mendatang; belum digunakan oleh test Playwright saat ini.

Alur company saat ini memanggil `CompanyData.generate_with_metadata()` di `tests/test_company.py`. Data company yang dikembalikan adalah data yang sama dengan yang dikirim ke registration wizard dan digunakan oleh assertion detail yang sudah ada.

### Request AI dan validasi output

Jika `EDOT_AI_API_KEY` tersedia, `AIDataGenerator` mengirim request ke OpenAI Responses API (`/v1/responses`) dengan `store: false`. Model default adalah `gpt-4.1-mini`, kecuali `EDOT_AI_MODEL` diatur.

Structured JSON diminta menggunakan strict JSON Schema yang berasal dari model Pydantic:

- `CompanyTestData` mewajibkan nilai eSuite yang diuji, termasuk location cascade yang didukung dan postal code `40286`.
- `CustomerTestData` mewajibkan nama, contact, alamat, serta nomor telepon yang dimulai dengan `628`.

Respons divalidasi kembali secara lokal menggunakan `model_validate`. Field tambahan dilarang. JSON invalid, provider error, output text yang tidak tersedia, dan schema-validation failure diperlakukan sebagai percobaan gagal dan tidak diteruskan ke test.

## Exact Prompt yang Digunakan

Kedua implementasi mengirim satu string melalui field request `input`. Tidak ada system prompt atau field `instructions` terpisah pada implementation saat ini. Structured-output JSON Schema dikirim melalui field `text.format.schema`, bukan sebagai bagian dari text prompt di bawah.

### AI Test Data Generation

#### Company test data

Template `input` berikut dikembalikan oleh `AIDataGenerator._company_prompt(run_id)`:

```text
Return only JSON that matches the supplied schema.
Generate coherent, realistic Indonesian business test data for an eSuite company.
Use a legal Indonesian-style company name of at most 30 characters containing exactly this run identifier: QA-{run_id}.
Use an email at example.test and an Indonesian mobile phone starting with 628.
The target application only accepts this verified location cascade: Indonesia, JAWA BARAT,
KOTA BANDUNG, BUAHBATU, JATISARI, postal code 40286. Set industry to Technology,
company_type to Marketplace, language to Indonesia, and branch_name to Headquarter.
The street address must be a realistic single-line Bandung address. Do not add commentary.
```

`{run_id}` diisi saat runtime dari `EDOT_TEST_RUN_ID`; jika environment variable tersebut tidak tersedia, nilainya adalah delapan karakter unik berbasis UUID yang dibuat oleh `AIDataGenerator`.

#### Customer test data

Template `input` berikut dikembalikan oleh `AIDataGenerator._customer_prompt(run_id)`:

```text
Return only JSON that matches the supplied schema.
Generate realistic Indonesian customer data for future mobile test use: name, contact,
street address, and mobile phone starting with 628. Include QA-{run_id} in the name.
Do not add commentary.
```

`{run_id}` menggunakan sumber runtime yang sama. Customer prompt telah diimplementasikan dalam generator, tetapi data customer belum digunakan oleh Playwright suite saat ini.

### AI Failure Triage

Template `input` berikut dikembalikan oleh `_triage_prompt(failed_test)`:

```text
You are a QA failure-triage assistant. This is advisory-only human review.
You must not propose changes to assertions, expected values, test code, test execution,
bug trackers, or Allure results. Do not state that a test passed.

Classify the existing failure as exactly one of: Script/Environment Defect,
Product Bug, Flaky. Analyse evidence in this exact order and return five concise
evidence_sequence entries with these labels: (1) Exception/timeout/assertion,
(2) Locator correctness and uniqueness, (3) Previous steps and preconditions,
(4) Expected-value correctness, (5) Reproducibility/intermittency.
If evidence is missing, explicitly say so rather than inventing it.

Allure evidence follows:
```

Setelah text di atas, implementation menambahkan `json.dumps(evidence, ensure_ascii=False)` ke string `input`. Object `evidence` diisi saat runtime dari Allure result dengan field berikut:

```text
{
  "test_name": failed_test.name,
  "status": failed_test.status,
  "exception_or_assertion": failed_test.error,
  "trace": failed_test.trace[:MAX_ATTACHMENT_CHARS],
  "previous_steps": failed_test.steps,
  "attachments": failed_test.attachments
}
```

`MAX_ATTACHMENT_CHARS` bernilai `4_000`. Isi attachment text/JSON telah dibatasi sebelum menjadi bagian dari `failed_test.attachments`; attachment biner digantikan dengan keterangan bahwa isinya tidak dimasukkan ke AI prompt.

### Retry dan deterministic fallback

Generator melakukan maksimal dua percobaan AI. Jika API key tidak tersedia, request AI tidak dibuat dan fallback digunakan langsung. Jika provider gagal atau output tetap invalid setelah dua percobaan, generator menggunakan fallback Faker (`id_ID`).

Fallback deterministik untuk kombinasi `EDOT_TEST_DATA_SEED` dan `EDOT_TEST_RUN_ID` yang sama. Jika run ID tidak disediakan, generator membuat run ID unik delapan karakter berbasis UUID agar tidak bertabrakan dengan company dari run sebelumnya.

### Attachment Allure

Sebelum form company diisi, `tests/test_company.py` memanggil `attach_generated_company_data()`. `utils/data_generator.py` melampirkan data tepat yang dikirimkan ke Allure sebagai JSON bernama **Actual Company Test Data**, termasuk sumbernya (`ai` atau `fallback`) dan jumlah percobaan AI.

## 2. AI Failure Triage

### Tujuan dan waktu eksekusi

`utils/failure_triage.py` adalah command post-suite yang bersifat advisory-only. Script ini tidak menjalankan test. Script membaca folder `allure-results` yang sudah ada dan menghasilkan Markdown report.

Jalankan setelah suite menghasilkan Allure result:

```bash
make triage
```

Command membaca `allure-results/*-result.json` tanpa mengubah atau menghapus artifact Allure, lalu menulis `triage-report.md`.

### Input dan evidence

Hanya Allure result berstatus `failed` atau `broken` yang dimasukkan. Untuk setiap result, script membaca:

- nama test, full name, dan status;
- error message dan trace;
- Allure step yang tercatat; serta
- metadata attachment. Isi attachment text dan JSON dibatasi hingga 4.000 karakter; isi attachment biner tidak dikirim ke AI.

Jika AI tersedia, evidence dianalisa dalam urutan berikut:

1. Exception, timeout, atau failed assertion.
2. Locator correctness dan uniqueness.
3. Previous steps dan preconditions.
4. Expected-value correctness.
5. Reproducibility atau intermittent behaviour.

### Verdict dan report

Strict schema `TriageAdvice` hanya mengizinkan verdict berikut:

- `Script/Environment Defect`
- `Product Bug`
- `Flaky`

Report mencakup nama test, status, error, evidence yang tersedia, verdict, confidence, reasoning singkat, evidence sequence, dan recommended human follow-up.

### Fallback saat AI tidak tersedia

Failure triage mencoba request AI maksimal dua kali. Jika `EDOT_AI_API_KEY` tidak tersedia, provider gagal, atau respons tidak lolos schema validation, Markdown report tetap dibuat. Report menyatakan **AI unavailable; human triage required** dan sengaja tidak membuat verdict.

Jika `allure-results` tidak ada atau tidak berisi result `failed`/`broken`, report dibuat dengan pesan `No failed or broken Allure test result was found.`

## 3. AI Guardrails

Kedua fitur AI sengaja dibatasi:

- AI hanya menyediakan test data atau teks triage advisory.
- AI tidak mengubah test code, Page Object, assertion, expected value, atau source file.
- AI tidak dapat skip, xfail, memicu retry terhadap test Playwright, atau menandai Playwright test sebagai passed.
- Playwright dan pytest tetap menjadi sumber kebenaran untuk PASS/FAIL.
- Triage script tidak menjalankan pytest, mengubah Allure result, membuat bug, atau menutup bug.
- Ketika AI tidak tersedia, test tetap berjalan dengan fallback tervalidasi dan triage melaporkan advisory tidak tersedia tanpa menyembunyikan failure.

## 4. Konfigurasi

Atur konfigurasi AI opsional melalui runtime environment atau `.env`; jangan commit secret.

```bash
EDOT_AI_API_KEY=your-api-key
EDOT_AI_MODEL=gpt-4.1-mini
EDOT_TEST_DATA_SEED=20260819
EDOT_TEST_RUN_ID=optional-repeatable-run-id
```

- `EDOT_AI_API_KEY` mengaktifkan request untuk data generation dan failure triage.
- `EDOT_AI_MODEL` mengganti model default.
- `EDOT_TEST_DATA_SEED` mengatur seed Faker fallback (default: `20260819`).
- `EDOT_TEST_RUN_ID` membuat nilai fallback dapat direproduksi. Jika tidak diatur, generator membuat run ID unik.

## 5. Menjalankan

Make target yang tersedia saat ini:

```bash
make test          # menjalankan pytest suite normal
make headed        # menjalankan suite dengan browser terlihat
make allure        # menjalankan test lalu membuka Allure result
make allure-headed # menjalankan headed test lalu membuka Allure result
make allure-ci     # menjalankan test dan membuat allure-report
make triage        # menganalisa allure-results yang sudah ada saja
make clean         # menghapus output Allure dan pytest cache
```

Untuk membuat artifact failure triage eksplisit tanpa memengaruhi normal test discovery:

```bash
pytest tests/evidence_failure.py --alluredir=allure-results
make triage
```

`tests/evidence_failure.py` sengaja gagal tanpa membuka aplikasi atau membuat application test data. Nama file tidak mengikuti pola `test_*.py`, sehingga tidak dikoleksi oleh suite normal.

## 6. Perilaku Fallback

| Kondisi                                                | Perilaku test data                                                              | Perilaku triage                                                                                        |
| ------------------------------------------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| API key tidak tersedia                                 | Langsung menggunakan fallback Faker tervalidasi; tidak ada request AI.          | Membuat report tanpa verdict buatan dan meminta human triage.                                          |
| Request AI provider gagal                              | Mencoba maksimal dua kali, lalu menggunakan fallback Faker tervalidasi.         | Mencoba maksimal dua kali, lalu menulis AI-unavailable advisory.                                       |
| Output AI invalid                                      | Menolak output melalui validasi Pydantic lokal; mencoba kembali, lalu fallback. | Menolak output melalui validasi `TriageAdvice`; mencoba kembali, lalu menulis AI-unavailable advisory. |
| Allure result tidak tersedia atau tidak berisi failure | Tidak berlaku.                                                                  | Membuat report valid yang menyatakan tidak ada result failed/broken.                                   |

## 7. Keterbatasan

- Failure triage belum dirangkai otomatis ke command test; `make triage` harus dijalankan setelah Allure result tersedia.
- AI triage berbasis evidence dan advisory. Script tidak menjalankan ulang test atau menginspeksi aplikasi live, sehingga proposalnya harus direview manusia.
- Attachment Allure biner diidentifikasi, tetapi isinya tidak dimasukkan ke prompt AI.
- Company schema sengaja membatasi field seperti industry, company type, dan location value pada cascade yang saat ini didukung oleh application flow yang diuji.
- Customer generation sudah diimplementasikan, tetapi belum digunakan oleh Playwright suite.
