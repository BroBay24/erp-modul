# l10n\_id\_city — Indonesia: Wilayah Lengkap (Provinsi, Kab/Kota, Kecamatan, Desa)

> **Versi**: 18.0.2.0.0 | **Target Odoo**: 18.0 | **Lisensi**: LGPL-3

Modul lokalisasi Indonesia untuk Odoo 18 yang menyediakan **hierarki data wilayah administratif lengkap** — dari Provinsi hingga Kelurahan/Desa — dan mengintegrasikannya langsung ke form **Kontak** (`res.partner`).

---

## Fitur Utama

| Fitur | Keterangan |
|---|---|
| **Import Provinsi** | Muat 38 Provinsi ke `res.country.state` dengan kode ISO 3166-2:ID |
| **Import Kabupaten/Kota** | Muat 510+ Kabupaten/Kota ke `res.city` |
| **Import Kecamatan** | Muat data Kecamatan ke `res.district` *(memerlukan `districts.csv`)* |
| **Import Kelurahan/Desa** | Muat data Kelurahan/Desa ke `res.village` dari `villages.csv` |
| **Cascading Dropdown** | Form Kontak menyediakan 4 level dropdown yang saling memfilter |
| **Anti-duplikat** | Setiap level import mengecek keberadaan data sebelum membuat rekaman baru |

---

## Hierarki Model Data

```
res.country (Indonesia)
  └── res.country.state        (Provinsi)         [Odoo built-in]
        └── res.city            (Kabupaten/Kota)   [base_address_extended]
              └── res.district  (Kecamatan)         [modul ini]
                    └── res.village (Kelurahan/Desa) [modul ini]
```

---

## Dependensi

- **`base`** — Modul inti Odoo (`res.country`, `res.country.state`, `res.partner`)
- **`contacts`** — UI form kontak standar Odoo
- **`base_address_extended`** — Menyediakan model `res.city` dan field `city_id` pada `res.partner`

---

## Struktur Direktori

```
l10n_id_city/
├── __manifest__.py              # Deklarasi modul
├── __init__.py                  # Entry point Python
├── hooks.py                     # Post-install hook: pipeline import CSV
├── models/
│   ├── __init__.py
│   ├── res_city.py              # Extend res.city: tambah field `code`
│   ├── res_district.py          # Model baru: res.district (Kecamatan)
│   ├── res_village.py           # Model baru: res.village (Kelurahan/Desa)
│   └── res_partner.py           # Extend res.partner: tambah district_id, village_id
├── views/
│   └── res_partner_views.xml    # Inherit form Kontak: tambah 4 dropdown wilayah
├── security/
│   └── ir.model.access.csv      # Hak akses untuk res.district & res.village
└── data/
    ├── provinces.csv            # 38 Provinsi  (format: id;name)
    ├── regencies.csv            # 510+ Kab/Kota (format: id;province_id;name)
    ├── districts.csv            # Kecamatan     (format: id;regency_id;name) *opsional*
    └── villages.csv             # Kel/Desa      (format: id;district_id;name)
```

---

## Detail Teknis

### 1. Model

#### `res.district` (`models/res_district.py`)
Kecamatan yang berelasi ke `res.city` sebagai parent.

| Field | Tipe | Keterangan |
|---|---|---|
| `name` | `Char` | Nama kecamatan (required) |
| `regency_id` | `Many2one(res.city)` | Parent Kabupaten/Kota |
| `state_id` | `Many2one(res.country.state)` | Related dari `regency_id.state_id` |
| `country_id` | `Many2one(res.country)` | Related dari `regency_id.country_id` |
| `code` | `Char` | Kode wilayah Kemendagri |

#### `res.village` (`models/res_village.py`)
Kelurahan/Desa yang berelasi ke `res.district` sebagai parent.

| Field | Tipe | Keterangan |
|---|---|---|
| `name` | `Char` | Nama kelurahan/desa (required) |
| `district_id` | `Many2one(res.district)` | Parent Kecamatan |
| `city_id` | `Many2one(res.city)` | Related dari `district_id.regency_id` |
| `state_id` | `Many2one(res.country.state)` | Related dari `district_id.state_id` |
| `country_id` | `Many2one(res.country)` | Related dari `district_id.country_id` |
| `code` | `Char` | Kode wilayah Kemendagri |

#### `res.partner` (extend via `models/res_partner.py`)

| Field | Tipe | Domain |
|---|---|---|
| `city_id` | `Many2one(res.city)` | `[('state_id','=',state_id),('country_id','=',country_id)]` |
| `district_id` | `Many2one(res.district)` | `[('regency_id','=',city_id)]` |
| `village_id` | `Many2one(res.village)` | `[('district_id','=',district_id)]` |

---

### 2. Pipeline Import Data (`hooks.py`)

`_post_init_hook` dipanggil otomatis setelah modul berhasil diinstal. Urutan eksekusi:

```
_post_init_hook(env)
  │
  ├── _get_indonesia(env)           → Cari res.country kode='ID'
  ├── import_provinces(env)         → provinces.csv → res.country.state
  ├── import_regencies(env, ...)    → regencies.csv → res.city
  │     └── return regency_map {csv_id → odoo_id}
  ├── import_districts(env, ...)    → districts.csv → res.district (jika ada)
  │     └── return district_map {csv_id → odoo_id}
  └── import_villages(env, ...)     → villages.csv  → res.village
```

**Penting:** Import Villages membutuhkan Kecamatan (`res.district`) sudah ada di database. Jika `districts.csv` tidak disediakan, import Kelurahan/Desa akan dilewati secara otomatis dengan pesan log yang informatif.

#### Mapping Provinsi (`PROVINCE_CODE_MAP`)
File CSV menggunakan kode numerik BPS (contoh: `'31'` = DKI Jakarta), sedangkan Odoo menggunakan kode ISO 3166-2:ID (contoh: `'JK'`). `PROVINCE_CODE_MAP` bertugas sebagai jembatan antara dua sistem kode ini, mencakup seluruh 38 provinsi Indonesia.

---

### 3. Format CSV

#### `provinces.csv`
```csv
id;name
11;ACEH
12;SUMATERA UTARA
```

#### `regencies.csv`
```csv
id;province_id;name
1101;11;KAB. ACEH SELATAN
```

#### `districts.csv` *(diperlukan untuk aktifkan fitur Kecamatan & Desa)*
```csv
id;regency_id;name
110101;1101;BAKONGAN
```

#### `villages.csv`
```csv
id;district_id;name
1101012001;110101;Keude Bakongan
```

---

### 4. Hak Akses (`security/ir.model.access.csv`)

| Access ID | Model | Group | R | W | C | D |
|---|---|---|---|---|---|---|
| `access_res_city_public` | `res.city` | Semua | ✅ | ❌ | ❌ | ❌ |
| `access_res_city_manager` | `res.city` | `base.group_system` | ✅ | ✅ | ✅ | ✅ |
| `access_res_district_public` | `res.district` | Semua | ✅ | ❌ | ❌ | ❌ |
| `access_res_district_manager` | `res.district` | `base.group_system` | ✅ | ✅ | ✅ | ✅ |
| `access_res_village_public` | `res.village` | Semua | ✅ | ❌ | ❌ | ❌ |
| `access_res_village_manager` | `res.village` | `base.group_system` | ✅ | ✅ | ✅ | ✅ |

---

## Panduan Instalasi

1. Salin folder `l10n_id_city` ke direktori `custom-addons` Odoo Anda.
2. Pastikan path `custom-addons` terdaftar di `odoo.conf` pada key `addons_path`.
3. *(Opsional)* Siapkan file `data/districts.csv` untuk mengaktifkan fitur Kecamatan dan Kelurahan/Desa.
4. Aktifkan **Developer Mode** di Odoo.
5. Klik **Apps → Update Apps List**.
6. Cari *"Indonesia - Wilayah Lengkap"* dan klik **Install**.
7. Hook akan berjalan otomatis — pantau log Odoo untuk melihat progres import.

---

## Panduan Pengujian

Setelah instalasi selesai:

1. Buka menu **Contacts → New**.
2. Pilih **Country**: Indonesia.
3. Pilih **State** (Provinsi) — daftar akan terisi sesuai data CSV.
4. Pilih **City** (Kabupaten/Kota) — difilter berdasarkan Provinsi.
5. Pilih **Kecamatan** — difilter berdasarkan Kabupaten/Kota.
6. Pilih **Kelurahan/Desa** — difilter berdasarkan Kecamatan.

---

## Catatan Pengembang

> **Mengapa tidak pakai `env.ref('base.id')`?**
> `env.ref()` memerlukan XML ID yang terdaftar di `ir.model.data`. Kode `base.id` tidak mewakili negara Indonesia secara umum di semua instalasi Odoo. Pendekatan yang lebih robust adalah `env['res.country'].search([('code', '=', 'ID')], limit=1)` yang mencari berdasarkan kode ISO 3166-1 alpha-2 (`ID`) — dijamin konsisten di semua environment.

> **Mengapa file `res.district.py` diubah menjadi `res_district.py`?**
> Python tidak mendukung import module dengan titik di nama file menggunakan sintaks `from . import`. Nama file module Python harus menggunakan underscore sebagai pemisah kata.

---

## Lisensi

```
LGPL-3 — Lesser General Public License v3
Dikembangkan oleh: Bayfr
```
