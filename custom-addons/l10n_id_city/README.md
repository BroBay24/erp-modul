# l10n_id_city (Indonesia - Kabupaten/Kota)

Modul ini adalah ekstensi lokalisasi Indonesia untuk Odoo 18. Modul ini bertujuan untuk melengkapi data regional Indonesia dengan menambahkan data Provinsi (State) dan Kabupaten/Kota (City) yang sesuai dengan struktur data Odoo standar.

## Fitur Utama

1. **Import Data Provinsi Otomatis**: Secara otomatis memetakan dan memuat data Provinsi di Indonesia ke dalam model standar `res.country.state` milik Odoo.
2. **Import Data Kabupaten/Kota Otomatis**: Memuat ratusan data Kabupaten/Kota di seluruh Indonesia menggunakan data CSV yang tersedia, lalu menambahkannya ke model `res.city`.
3. **Penyempurnaan Form Kontak**: Menambahkan field terstruktur `city_id` pada form `res.partner` (Kontak) yang terintegrasi dengan field Provinsi, sehingga pencarian Kabupaten/Kota secara otomatis difilter berdasarkan Provinsi yang dipilih secara *cascading*.

## Dependensi

Modul ini memerlukan dependensi berikut yang harus sudah terinstal di database Odoo Anda:
- `base`: Modul inti Odoo.
- `contacts`: Modul manajemen kontak/partner.
- `base_address_extended`: Modul yang menyediakan model `res.city` dan struktur data kota lanjutan (Sangat Krusial).

## Struktur Teknis

- `__manifest__.py`: Deklarasi dan konfigurasi modul.
- `hooks.py`: Berisi skrip Python `_post_init_hook` yang bertugas untuk mem-parsing file CSV dan membuat data awal (Provinsi dan Kota) seketika setelah modul ini diinstal. Skrip menggunakan pemisah titik koma (`;`) pada proses import CSV.
- `models/res_city.py`: Mendefinisikan ekstensi/turunan (*inherit*) dari model standar `res.city` untuk menambahkan field `code` (sebagai kode identitas dari Kemendagri).
- `views/res_partner_views.xml`: Melakukan *inherit* pada form view standar Odoo `res.partner.form` dan menimpa field input kota teks standar dengan input dropdown `city_id`.
- `security/ir.model.access.csv`: Mendefinisikan tingkat hak akses untuk objek model `res.city` (Catatan: Model ini direferensikan menggunakan ID eksternal `base_address_extended.model_res_city`).
- `data/provinces.csv`: Dataset statis berisi daftar 38 Provinsi dengan kode wilayah.
- `data/regencies.csv`: Dataset statis berisi 510+ entri daftar Kabupaten/Kota beserta *parent ID* ke provinsi asal.

## Detail Skrip Import (`hooks.py`)

Proses import dilakukan secara dinamis melalui pendekatan *hook* dibandingkan dengan *XML data import* konvensional. Pendekatan ini dipilih untuk menjaga integritas data dengan memeriksa ketersediaan data negara dasar (Indonesia `base.id`) dan menghindari duplikasi wilayah dengan mencari apakah entri tersebut sudah pernah disimpan.

1. **Pemetaan Provinsi (PROVINCE_CODE_MAP)**: Memetakan ID provinsi pada file raw CSV ke dalam kode ISO 3166-2:ID yang dikenali oleh Odoo (contoh: ID `'31'` dipetakan ke `'JK'` untuk DKI Jakarta).
2. **Fase 1 - `import_provinces`**: Mengekstrak data `provinces.csv`. Jika data belum ada, rekaman provinsi baru dibuat di tabel dasar `res.country.state`.
3. **Fase 2 - `_post_init_hook`**: Pertama-tama memanggil `import_provinces` kemudian mengekstrak data dari `regencies.csv`. Fungsi ini mencari kecocokan Provinsi asal menggunakan *dictionary mapping* yang lalu mengambil State Odoo ID. Data Kabupaten/Kota kemudian di-insert ke dalam `res.city` menggunakan ID negara dasar `res.country.id` (Indonesia) dan Provinsi `res.country.state.id` tersebut.

## Panduan Instalasi dan Pengujian

1. Salin seluruh konten folder ini ke dalam direktori *addons* / *custom-addons* Anda.
2. Pastikan file konfigurasi Odoo.conf Anda merujuk ke direktori Addons yang membungkus folder modul ini.
3. Dari *Developer Mode* di antarmuka web Odoo, klik **Update Apps List**.
4. Cari `Indonesia - Kabupaten/Kota` dan klik Install. Modul akan otomatis mengimpor seluruh set data dalam beberapa saat.
5. Setelah instalasi selesai, buka modul Kontak -> Buat baru. Anda bisa memilih Provinsi di Indonesia (State) lalu opsi pada pilihan *City* akan menyesuaikan secara dinamis berdasar wilayah yang dipilih.

## Lisensi
Aplikasi ini dikembangkan untuk kebutuhan internal.
LGPL-3

---
**Catatan Penting Pengembangan**:
Aplikasi ini di-build menargetkan versi Odoo 18, beberapa API fungsional seperti format pemanggilan referensi di Odoo (khususnya untuk akses model `env.ref()` dan perujukan ID bawaan Odoo seperti `base.id`) telah disesuaikan spesifik berdasarkan pustaka dasar yang ada.
