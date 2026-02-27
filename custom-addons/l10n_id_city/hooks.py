import csv
import os
import logging

_logger = logging.getLogger(__name__)

# Mapping kode provinsi CSV -> kode state Odoo (res.country.state)
# Kode Odoo menggunakan kode ISO 3166-2:ID
PROVINCE_CODE_MAP = {
    '11': 'AC',  # Aceh
    '12': 'SU',  # Sumatera Utara
    '13': 'SB',  # Sumatera Barat
    '14': 'RI',  # Riau
    '15': 'JA',  # Jambi
    '16': 'SS',  # Sumatera Selatan
    '17': 'BE',  # Bengkulu
    '18': 'LA',  # Lampung
    '19': 'BB',  # Kepulauan Bangka Belitung
    '21': 'KR',  # Kepulauan Riau
    '31': 'JK',  # DKI Jakarta
    '32': 'JB',  # Jawa Barat
    '33': 'JT',  # Jawa Tengah
    '34': 'YO',  # DI Yogyakarta
    '35': 'JI',  # Jawa Timur
    '36': 'BT',  # Banten
    '51': 'BA',  # Bali
    '52': 'NB',  # Nusa Tenggara Barat
    '53': 'NT',  # Nusa Tenggara Timur
    '61': 'KB',  # Kalimantan Barat
    '62': 'KT',  # Kalimantan Tengah
    '63': 'KS',  # Kalimantan Selatan
    '64': 'KI',  # Kalimantan Timur
    '65': 'KU',  # Kalimantan Utara
    '71': 'SA',  # Sulawesi Utara
    '72': 'ST',  # Sulawesi Tengah
    '73': 'SN',  # Sulawesi Selatan
    '74': 'SG',  # Sulawesi Tenggara
    '75': 'GO',  # Gorontalo
    '76': 'SR',  # Sulawesi Barat
    '81': 'MA',  # Maluku
    '82': 'MU',  # Maluku Utara
    '91': 'PA',  # Papua
    '92': 'PB',  # Papua Barat
    '93': 'PS',  # Papua Selatan
    '94': 'PT',  # Papua Tengah
    '95': 'PE',  # Papua Pegunungan
    '96': 'PD',  # Papua Barat Daya
}


def _get_indonesia(env):
    """Ambil record res.country untuk Indonesia (kode ISO: ID)."""
    country = env['res.country'].search([('code', '=', 'ID')], limit=1)
    if not country:
        _logger.error("Country Indonesia (kode 'ID') tidak ditemukan di database!")
    return country


def import_provinces(env):
    """Import provinsi dari CSV ke res.country.state jika belum ada."""
    _logger.info("Importing provinces from CSV...")
    country = _get_indonesia(env)
    if not country:
        return

    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'provinces.csv')

    if not os.path.isfile(csv_file):
        _logger.warning("File CSV tidak ditemukan: %s", csv_file)
        return

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            prov_id = row.get('id', '').strip()
            prov_name = row.get('name', '').strip()
            state_code = PROVINCE_CODE_MAP.get(prov_id)

            if not state_code:
                _logger.warning(
                    "Kode provinsi '%s' tidak ditemukan di mapping untuk: %s",
                    prov_id, prov_name
                )
                continue

            existing = env['res.country.state'].search([
                ('code', '=', state_code),
                ('country_id', '=', country.id),
            ], limit=1)

            if not existing:
                env['res.country.state'].create({
                    'name': prov_name.title(),
                    'code': state_code,
                    'country_id': country.id,
                })
                _logger.info("Provinsi '%s' (%s) berhasil ditambahkan.", prov_name, state_code)


def import_regencies(env, country, state_map):
    """Load data Kabupaten/Kota dari file CSV."""
    _logger.info("Loading data Kabupaten/Kota Indonesia dari CSV...")
    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'regencies.csv')

    if not os.path.isfile(csv_file):
        _logger.warning("File CSV tidak ditemukan: %s", csv_file)
        return {}

    created_count = 0
    skipped_count = 0
    # Map: regency CSV id (str) -> res.city record id (int)
    regency_map = {}

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            regency_code = row.get('id', '').strip()
            province_id_csv = row.get('province_id', '').strip()
            regency_name = row.get('name', '').strip()

            state_code = PROVINCE_CODE_MAP.get(province_id_csv)
            if not state_code:
                _logger.warning(
                    "Kode provinsi '%s' tidak ditemukan di mapping untuk kota: %s",
                    province_id_csv, regency_name
                )
                skipped_count += 1
                continue

            state_id = state_map.get(state_code)
            if not state_id:
                _logger.warning(
                    "State dengan kode '%s' tidak ditemukan di Odoo untuk kota: %s",
                    state_code, regency_name
                )
                skipped_count += 1
                continue

            existing = env['res.city'].search([
                ('name', '=', regency_name),
                ('state_id', '=', state_id),
                ('country_id', '=', country.id),
            ], limit=1)

            if existing:
                regency_map[regency_code] = existing.id
                skipped_count += 1
            else:
                new_city = env['res.city'].create({
                    'name': regency_name,
                    'code': regency_code,
                    'state_id': state_id,
                    'country_id': country.id,
                })
                regency_map[regency_code] = new_city.id
                created_count += 1

    _logger.info(
        "Kabupaten/Kota: %d ditambahkan, %d dilewati (sudah ada).",
        created_count, skipped_count
    )
    return regency_map


def import_districts(env, regency_map):
    """Import Kecamatan dari CSV ke res.district. Mengembalikan dict {district_csv_id: res.district.id}."""
    _logger.info("Loading data Kecamatan Indonesia dari CSV...")

    # Gunakan regency_map (csv_id -> res.city.id) untuk menghubungkan kecamatan
    # District CSV tidak ada file terpisah di sini, skip jika tidak ada
    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'districts.csv')
    district_map = {}

    if not os.path.isfile(csv_file):
        _logger.info("File districts.csv tidak ditemukan, lewati import kecamatan.")
        return district_map

    created_count = 0
    skipped_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            district_code = row.get('id', '').strip()
            regency_id_csv = row.get('regency_id', '').strip()
            district_name = row.get('name', '').strip()

            city_odoo_id = regency_map.get(regency_id_csv)
            if not city_odoo_id:
                skipped_count += 1
                continue

            existing = env['res.district'].search([
                ('name', '=', district_name),
                ('regency_id', '=', city_odoo_id),
            ], limit=1)

            if existing:
                district_map[district_code] = existing.id
                skipped_count += 1
            else:
                new_district = env['res.district'].create({
                    'name': district_name,
                    'code': district_code,
                    'regency_id': city_odoo_id,
                })
                district_map[district_code] = new_district.id
                created_count += 1

    _logger.info(
        "Kecamatan: %d ditambahkan, %d dilewati (sudah ada).",
        created_count, skipped_count
    )
    return district_map


def import_villages(env, regency_map):
    """Import Kelurahan/Desa dari villages.csv ke res.village.

    villages.csv format: id;district_id;name
    Catatan: district_id pada CSV mengacu ke kode kecamatan, namun karena
    file districts.csv tidak tersedia terpisah, kita derive regency dari
    4 digit pertama kode village -> regency_code (4 digit pertama dari village code).
    """
    _logger.info("Loading data Kelurahan/Desa Indonesia dari CSV...")
    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'villages.csv')

    if not os.path.isfile(csv_file):
        _logger.warning("File villages.csv tidak ditemukan: %s", csv_file)
        return

    created_count = 0
    skipped_count = 0

    # Bangun district_map dari DB yang sudah ada (district_code -> res.district.id)
    all_districts = env['res.district'].search([])
    district_map = {d.code: d.id for d in all_districts if d.code}

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            village_code = row.get('id', '').strip()
            district_id_csv = row.get('district_id', '').strip()
            village_name = row.get('name', '').strip()

            district_odoo_id = district_map.get(district_id_csv)
            if not district_odoo_id:
                skipped_count += 1
                continue

            existing = env['res.village'].search([
                ('name', '=', village_name),
                ('district_id', '=', district_odoo_id),
            ], limit=1)

            if existing:
                skipped_count += 1
            else:
                env['res.village'].create({
                    'name': village_name,
                    'code': village_code,
                    'district_id': district_odoo_id,
                })
                created_count += 1

    _logger.info(
        "Kelurahan/Desa: %d ditambahkan, %d dilewati (sudah ada / kecamatan tidak ditemukan).",
        created_count, skipped_count
    )


def _post_init_hook(env):
    """Load hierarki data wilayah Indonesia dari CSV setelah modul diinstal.

    Urutan import: Provinsi -> Kabupaten/Kota -> Kecamatan -> Kelurahan/Desa
    """
    # 1. Cari country Indonesia
    country = _get_indonesia(env)
    if not country:
        return

    # 2. Import Provinsi
    import_provinces(env)

    # 3. Rebuild state_map setelah import provinsi
    states = env['res.country.state'].search([('country_id', '=', country.id)])
    state_map = {state.code: state.id for state in states}

    # 4. Import Kabupaten/Kota, dapatkan mapping CSV id -> Odoo id
    regency_map = import_regencies(env, country, state_map)

    # 5. Import Kecamatan (jika file districts.csv tersedia)
    district_map = import_districts(env, regency_map)

    # 6. Import Kelurahan/Desa (membutuhkan kecamatan sudah ada di DB)
    if district_map:
        import_villages(env, regency_map)
    else:
        _logger.info(
            "Melewati import Kelurahan/Desa karena data Kecamatan tidak tersedia. "
            "Sediakan file data/districts.csv dan jalankan ulang hook untuk mengaktifkan fitur ini."
        )

    _logger.info("Import data wilayah Indonesia selesai.")