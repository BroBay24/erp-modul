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

def import_provinces(env):
    """Import provinsi dari CSV ke res.country.state."""
    _logger.info("Importing provinces from CSV...")
    country_id = env.ref('base.id')
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
                _logger.warning("Kode provinsi '%s' tidak ditemukan di mapping untuk: %s", prov_id, prov_name)
                continue
            
            # Cek apakah provinsi sudah ada
            existing = env['res.country.state'].search([
                ('code', '=', state_code),
                ('country_id', '=', country_id.id),
            ], limit=1)
            
            if not existing:
                env['res.country.state'].create({
                    'name': prov_name.title(),
                    'code': state_code,
                    'country_id': country_id.id,
                })

def _post_init_hook(env):
    """Load data provinsi dan kabupaten/kota dari file CSV setelah module diinstall."""
    import_provinces(env)
    _logger.info("Loading data Kabupaten/Kota Indonesia dari CSV...")

    # Cari country Indonesia
    country_id = env.ref('base.id')  # 'base.id' adalah XML ID untuk Indonesia

    if not country_id:
        _logger.error("Country Indonesia tidak ditemukan!")
        return

    # Baca file regencies.csv
    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'regencies.csv')

    if not os.path.isfile(csv_file):
        _logger.warning("File CSV tidak ditemukan: %s", csv_file)
        return

    # Cache semua state (provinsi) Indonesia yang sudah ada di Odoo
    states = env['res.country.state'].search([('country_id', '=', country_id.id)])
    state_map = {state.code: state.id for state in states}

    # Baca CSV dan insert ke database
    created_count = 0
    skipped_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Format CSV: id,province_id,name
            regency_code = row.get('id', '').strip()
            province_id_csv = row.get('province_id', '').strip()
            regency_name = row.get('name', '').strip()

            # Cari kode state Odoo dari mapping
            state_code = PROVINCE_CODE_MAP.get(province_id_csv)

            if not state_code:
                _logger.warning(
                    "Kode provinsi '%s' tidak ditemukan di mapping untuk: %s",
                    province_id_csv, regency_name
                )
                skipped_count += 1
                continue

            state_id = state_map.get(state_code)

            if not state_id:
                _logger.warning(
                    "State dengan kode '%s' tidak ditemukan di Odoo untuk: %s",
                    state_code, regency_name
                )
                skipped_count += 1
                continue

            # Cek apakah kota sudah ada (hindari duplikat)
            existing = env['res.city'].search([
                ('name', '=', regency_name),
                ('state_id', '=', state_id),
                ('country_id', '=', country_id.id),
            ], limit=1)

            if not existing:
                env['res.city'].create({
                    'name': regency_name,
                    'code': regency_code,
                    'state_id': state_id,
                    'country_id': country_id.id,
                })
                created_count += 1
            else:
                skipped_count += 1

    _logger.info(
        "Selesai! %d kabupaten/kota ditambahkan, %d dilewati (sudah ada/error).",
        created_count, skipped_count
    )