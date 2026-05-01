import pandas as pd
import json
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

# ── Setup ────────────────────────────────────────────────
fake = Faker('en_CA')
Faker.seed(99)
random.seed(99)

OUTPUT_DIR = Path('C:\\Users\\wwwda\\Downloads\\nexus project\\data\\raw')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Reference Data ───────────────────────────────────────
PROVINCES    = ['ON', 'BC', 'QC', 'AB', 'MB', 'SK', 'NS']
SEGMENTS     = ['RETAIL', 'PREMIUM', 'PRIVATE', 'SMB']
RISK         = ['LOW', 'MEDIUM', 'HIGH']
CHANNELS     = ['MOBILE', 'WEB', 'ATM', 'BRANCH', 'API']
INSTRUMENTS  = ['AAPL', 'TD.TO', 'GBPUSD', 'SPY', 'CA10Y', 'BTC-USD', 'MSFT', 'RY.TO']
MERCHANTS    = ['Tim Hortons', 'Loblaws', 'Amazon CA', 'Shopify', 'Rogers', 'Bell', 'Uber', 'Netflix']
MCC          = ['GROCERY', 'UTILITIES', 'TRANSFER', 'RETAIL', 'TELECOM', 'ENTERTAINMENT']
TXN_TYPES    = ['DEBIT', 'CREDIT', 'TRANSFER', 'PAYMENT', 'FX']
ALERT_TYPES  = ['VELOCITY', 'GEOLOCATION', 'UNUSUAL_AMOUNT', 'PATTERN', 'DEVICE_CHANGE']
SEVERITIES   = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
EVENT_TYPES  = ['page_view', 'button_click', 'login', 'logout', 'transfer_init', 'search']
SCREENS      = ['dashboard', 'payments', 'accounts', 'profile', 'invest', 'support']
DEVICES      = ['iOS', 'Android', 'Web']
ACC_TYPES    = ['CHEQUING', 'SAVINGS', 'TFSA']
INST_TYPES   = ['EQUITY', 'FX', 'FIXED_INCOME', 'ETF']
VENUES       = ['TSX', 'NYSE', 'OTC']
DIRECTIONS   = ['BUY', 'SELL']
STATUSES_TXN = ['COMPLETED', 'COMPLETED', 'COMPLETED', 'PENDING', 'FAILED']
STATUSES_TRD = ['EXECUTED', 'EXECUTED', 'SETTLED', 'CANCELLED']
KYC_STATUSES = ['APPROVED', 'APPROVED', 'APPROVED', 'PENDING', 'REJECTED']
ALERT_STATUS = ['OPEN', 'OPEN', 'RESOLVED', 'ESCALATED']
RULES        = ['RULE_001', 'RULE_002', 'RULE_003', 'RULE_004', 'ML_MODEL_V2']

def rnd_date(start_days=730, end_days=0):
    delta = random.randint(end_days, start_days)
    return datetime.utcnow() - timedelta(days=delta)

# ── 1. customers_export.csv ──────────────────────────────
def gen_customers_csv(n=10000):
    print('Generating customers_export.csv...')
    rows = []
    for i in range(n):
        rows.append({
            'customer_id':   i + 1,
            'full_name':     fake.name(),
            'email':         fake.unique.email(),
            'phone':         fake.phone_number()[:20],
            'address_line1': fake.street_address()[:200],
            'city':          fake.city(),
            'province':      random.choice(PROVINCES),
            'postal_code':   fake.postcode()[:10],
            'country':       'Canada',
            'nationality':   random.choice(['Canadian', 'American', 'British', 'Indian', 'Chinese']),
            'risk_rating':   random.choices(RISK, weights=[60, 30, 10])[0],
            'kyc_status':    random.choices(KYC_STATUSES, weights=[60, 15, 15, 7, 3])[0],
            'segment':       random.choices(SEGMENTS, weights=[50, 30, 10, 10])[0],
            'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
            'created_at':    rnd_date(1460, 30).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at':    rnd_date(30, 0).strftime('%Y-%m-%d %H:%M:%S'),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'customers_export.csv', index=False)
    size_kb = (OUTPUT_DIR / 'customers_export.csv').stat().st_size / 1024
    print(f'  ✓ customers_export.csv — {n:,} rows — {size_kb:.1f} KB\n')

# ── 2. transactions_2026.csv ─────────────────────────────
def gen_transactions_csv(n=50000):
    print('Generating transactions_2026.csv...')
    rows = []
    for _ in range(n):
        amount     = round(random.uniform(1, 15000), 2)
        fraud_flag = random.choices([0, 1], weights=[97, 3])[0]
        rows.append({
            'transaction_id':    str(uuid.uuid4()),
            'account_id':        random.randint(1, 17981),
            'transaction_type':  random.choice(TXN_TYPES),
            'amount':            amount,
            'currency':          'CAD',
            'fx_rate':           1.0,
            'cad_equivalent':    amount,
            'channel':           random.choice(CHANNELS),
            'merchant_name':     random.choice(MERCHANTS),
            'merchant_category': random.choice(MCC),
            'description':       fake.sentence(nb_words=4),
            'reference_number':  'TXN-' + str(uuid.uuid4())[:13],
            'status':            random.choices(STATUSES_TXN, weights=[80, 5, 5, 7, 3])[0],
            'fraud_flag':        fraud_flag,
            'fraud_score':       round(random.uniform(0.5, 1.0), 4) if fraud_flag else round(random.uniform(0, 0.3), 4),
            'transaction_date':  rnd_date(365, 0).strftime('%Y-%m-%d %H:%M:%S'),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'transactions_2026.csv', index=False)
    size_kb = (OUTPUT_DIR / 'transactions_2026.csv').stat().st_size / 1024
    print(f'  ✓ transactions_2026.csv — {n:,} rows — {size_kb:.1f} KB\n')

# ── 3. mobile_events.json (newline-delimited) ────────────
def gen_mobile_events_json(n=25000):
    print('Generating mobile_events.json...')
    with open(OUTPUT_DIR / 'mobile_events.json', 'w') as f:
        for _ in range(n):
            event = {
                'event_id':    str(uuid.uuid4()),
                'event_type':  random.choice(EVENT_TYPES),
                'session_id':  str(uuid.uuid4())[:12],
                'user_id':     f'usr_{random.randint(1, 10000):05d}',
                'screen':      random.choice(SCREENS),
                'device':      random.choice(DEVICES),
                'os_version':  f'{random.randint(14, 17)}.{random.randint(0, 5)}',
                'app_version': f'3.{random.randint(0, 9)}.{random.randint(0, 9)}',
                'duration_ms': random.randint(200, 15000),
                'ab_variant':  random.choice(['A', 'B']),
                'geo_province': random.choice(PROVINCES),
                'timestamp':   rnd_date(30, 0).strftime('%Y-%m-%dT%H:%M:%S'),
            }
            f.write(json.dumps(event) + '\n')
    size_kb = (OUTPUT_DIR / 'mobile_events.json').stat().st_size / 1024
    print(f'  ✓ mobile_events.json — {n:,} events — {size_kb:.1f} KB\n')

# ── 4. fraud_alerts.json (JSON array) ───────────────────
def gen_fraud_alerts_json(n=2500):
    print('Generating fraud_alerts.json...')
    alerts = []
    for _ in range(n):
        created = rnd_date(90, 0)
        alerts.append({
            'alert_id':        str(uuid.uuid4()),
            'transaction_id':  str(uuid.uuid4()),
            'alert_type':      random.choice(ALERT_TYPES),
            'severity':        random.choices(SEVERITIES, weights=[30, 40, 20, 10])[0],
            'ml_score':        round(random.uniform(0.5, 1.0), 4),
            'rule_triggered':  random.choice(RULES),
            'status':          random.choices(ALERT_STATUS, weights=[40, 10, 35, 15])[0],
            'investigated_by': random.choice([None, 'analyst_maria', 'analyst_john', 'analyst_priya']),
            'resolved_at':     (created + timedelta(hours=random.randint(1, 72))).strftime('%Y-%m-%dT%H:%M:%S') if random.random() > 0.4 else None,
            'notes':           fake.sentence(nb_words=8),
            'created_at':      created.strftime('%Y-%m-%dT%H:%M:%S'),
        })
    with open(OUTPUT_DIR / 'fraud_alerts.json', 'w') as f:
        json.dump(alerts, f, indent=2)
    size_kb = (OUTPUT_DIR / 'fraud_alerts.json').stat().st_size / 1024
    print(f'  ✓ fraud_alerts.json — {n:,} alerts — {size_kb:.1f} KB\n')

# ── 5. legacy_accounts.xml ───────────────────────────────
def gen_legacy_xml(n=5000):
    print('Generating legacy_accounts.xml...')
    root = ET.Element('ClearBankAccounts')
    root.set('exported_at', datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
    root.set('source', 'legacy_core_banking_v3')
    root.set('record_count', str(n))
    for i in range(n):
        acc = ET.SubElement(root, 'Account')
        ET.SubElement(acc, 'AccountId').text       = str(i + 1)
        ET.SubElement(acc, 'AccountNumber').text    = str(uuid.uuid4().int)[:16]
        ET.SubElement(acc, 'AccountType').text      = random.choice(ACC_TYPES)
        ET.SubElement(acc, 'Balance').text          = str(round(random.uniform(0, 250000), 2))
        ET.SubElement(acc, 'Currency').text         = 'CAD'
        ET.SubElement(acc, 'CustomerSegment').text  = random.choice(SEGMENTS)
        ET.SubElement(acc, 'Province').text         = random.choice(PROVINCES)
        ET.SubElement(acc, 'Status').text           = random.choices(['ACTIVE', 'FROZEN', 'CLOSED'], weights=[80, 10, 10])[0]
        ET.SubElement(acc, 'OpenedDate').text       = rnd_date(1460, 30).strftime('%Y-%m-%d')
        ET.SubElement(acc, 'LastActivityDate').text = rnd_date(30, 0).strftime('%Y-%m-%d')
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(
        OUTPUT_DIR / 'legacy_accounts.xml',
        encoding='utf-8',
        xml_declaration=True
    )
    size_kb = (OUTPUT_DIR / 'legacy_accounts.xml').stat().st_size / 1024
    print(f'  ✓ legacy_accounts.xml — {n:,} accounts — {size_kb:.1f} KB\n')

# ── 6. trades_feed.parquet ───────────────────────────────
def gen_trades_parquet(n=25000):
    print('Generating trades_feed.parquet...')
    rows = []
    for _ in range(n):
        price    = round(random.uniform(10, 5000), 4)
        quantity = round(random.uniform(1, 10000), 2)
        rows.append({
            'trade_id':        str(uuid.uuid4()),
            'customer_id':     random.randint(1, 10000),
            'instrument':      random.choice(INSTRUMENTS),
            'instrument_type': random.choice(INST_TYPES),
            'direction':       random.choice(DIRECTIONS),
            'quantity':        quantity,
            'price':           price,
            'notional_cad':    round(price * quantity, 2),
            'commission':      round(random.uniform(0, 50), 2),
            'venue':           random.choice(VENUES),
            'settlement_date': (rnd_date(730, 2) + timedelta(days=2)).strftime('%Y-%m-%d'),
            'status':          random.choices(STATUSES_TRD, weights=[50, 30, 15, 5])[0],
            'trade_date':      rnd_date(730, 0).strftime('%Y-%m-%d %H:%M:%S'),
        })
    df = pd.DataFrame(rows)
    df.to_parquet(OUTPUT_DIR / 'trades_feed.parquet', index=False)
    size_kb = (OUTPUT_DIR / 'trades_feed.parquet').stat().st_size / 1024
    print(f'  ✓ trades_feed.parquet — {n:,} rows — {size_kb:.1f} KB\n')

# ── Main ─────────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 50)
    print('  ClearBank Raw File Generator')
    print(f'  Output: {OUTPUT_DIR.resolve()}')
    print('=' * 50 + '\n')

    gen_customers_csv()
    gen_transactions_csv()
    gen_mobile_events_json()
    gen_fraud_alerts_json()
    gen_legacy_xml()
    gen_trades_parquet()

    print('=' * 50)
    print('All raw files written successfully!')
    print('=' * 50)

    print('\nFile Summary:')
    print(f'  {"File":<35} {"Size":>10}')
    print(f'  {"-"*35} {"-"*10}')
    for f in sorted(OUTPUT_DIR.iterdir()):
        size_kb = f.stat().st_size / 1024
        if size_kb >= 1024:
            print(f'  {f.name:<35} {size_kb/1024:>8.1f} MB')
        else:
            print(f'  {f.name:<35} {size_kb:>8.1f} KB')

    print(f'\n✓ Ready to upload to ADLS raw-landing container.')