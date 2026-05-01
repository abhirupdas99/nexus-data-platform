import pyodbc
import random
import uuid
import time
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('en_CA')
Faker.seed(42)
random.seed(42)

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=nexus-sql-abhirup.database.windows.net;"
    "DATABASE=clearbank-db;"
    "UID=nexusadmin;"
    "PWD=NexusP@ss2026!;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

PROVINCES   = ['ON','BC','QC','AB','MB','SK','NS']
SEGMENTS    = ['RETAIL','PREMIUM','PRIVATE','SMB']
RISK        = ['LOW','MEDIUM','HIGH']
CHANNELS    = ['MOBILE','WEB','ATM','BRANCH','API']
ACC_TYPES   = ['CHEQUING','SAVINGS','TFSA','RRSP','LOC']
TXN_TYPES   = ['DEBIT','CREDIT','TRANSFER','PAYMENT','FX']
MERCHANTS   = ['Tim Hortons','Loblaws','Amazon CA','Shopify','TD Visa','Hydro One','Rogers','Bell','Uber','Netflix']
MCC         = ['GROCERY','UTILITIES','TRANSFER','RETAIL','TELECOM','ENTERTAINMENT','TRANSPORT']
INSTRUMENTS = ['AAPL','TD.TO','GBPUSD','CADUSD','CA10Y','SPY','BTC-USD','MSFT','RY.TO','ENB.TO']
INST_TYPES  = ['EQUITY','FX','FIXED_INCOME','ETF','OPTION']
DIRECTIONS  = ['BUY','SELL','SHORT']
VENUES      = ['TSX','NYSE','OTC','INTERNAL']
DOC_TYPES   = ['PASSPORT','DRIVERS_LICENSE','PR_CARD','NATIONAL_ID']
KYC_STATUS  = ['APPROVED','APPROVED','APPROVED','PENDING','REJECTED']
METHODS     = ['VISA','MASTERCARD','AMEX','INTERAC','EFT']
SCREEN_TYPES= ['ONBOARDING','PERIODIC','TRIGGERED']
OUTCOMES    = ['CLEAR','CLEAR','CLEAR','REVIEW','ESCALATE','BLOCK']
ALERT_TYPES = ['VELOCITY','GEOLOCATION','UNUSUAL_AMOUNT','PATTERN']
SEVERITIES  = ['LOW','MEDIUM','HIGH','CRITICAL']

def rnd_date(start_days=730, end_days=0):
    delta = random.randint(end_days, start_days)
    return datetime.utcnow() - timedelta(days=delta)

def connect():
    print("Connecting to clearbank-db...")
    for attempt in range(1, 6):
        try:
            conn = pyodbc.connect(conn_str, timeout=30)
            conn.autocommit = True
            print("  Connected.\n")
            return conn
        except Exception as e:
            if "40613" in str(e):
                print(f"  Database waking up — attempt {attempt}/5, waiting 20s...")
                time.sleep(20)
            else:
                raise
    raise Exception("Could not connect after 5 attempts")

# ── 1. Customers ─────────────────────────────────────────
def generate_customers(cursor, n=10000):
    print(f"Generating {n} customers...")
    batch = []
    for _ in range(n):
        batch.append((
            fake.name(),
            fake.unique.email(),
            fake.phone_number()[:20],
            fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
            random.choice(['Canadian','American','British','Indian','Chinese','Filipino','Nigerian']),
            fake.street_address()[:300],
            fake.city()[:100],
            random.choice(PROVINCES),
            fake.postcode()[:20],
            'Canada',
            random.choices(RISK, weights=[60,30,10])[0],
            random.choices(KYC_STATUS, weights=[60,15,15,7,3])[0],
            random.choices(SEGMENTS, weights=[50,30,10,10])[0],
            rnd_date(1460, 30),
            rnd_date(30, 0),
        ))
        if len(batch) >= 500:
            cursor.executemany("""
                INSERT INTO core.customers
                (full_name,email,phone,date_of_birth,nationality,
                 address_line1,city,province,postal_code,country,
                 risk_rating,kyc_status,segment,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO core.customers
            (full_name,email,phone,date_of_birth,nationality,
             address_line1,city,province,postal_code,country,
             risk_rating,kyc_status,segment,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Customers done.\n")

# ── 2. Accounts ──────────────────────────────────────────
def generate_accounts(cursor):
    print("Generating accounts...")
    cursor.execute("SELECT customer_id, created_at FROM core.customers")
    customers = cursor.fetchall()
    batch = []
    for cust in customers:
        n_acc = random.choices([1,2,3], weights=[40,40,20])[0]
        for _ in range(n_acc):
            acc_type = random.choice(ACC_TYPES)
            balance  = round(random.uniform(0, 250000), 2)
            batch.append((
                cust.customer_id,
                str(uuid.uuid4().int)[:16],
                acc_type,
                'CAD',
                balance,
                round(random.uniform(0,50000),2) if acc_type == 'LOC' else 0,
                random.choices(['ACTIVE','ACTIVE','ACTIVE','FROZEN','CLOSED'], weights=[70,10,10,5,5])[0],
                rnd_date(1400, 30),
            ))
            if len(batch) >= 500:
                cursor.executemany("""
                    INSERT INTO core.accounts
                    (customer_id,account_number,account_type,currency,
                     balance,credit_limit,status,opened_date)
                    VALUES (?,?,?,?,?,?,?,?)
                """, batch)
                batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO core.accounts
            (customer_id,account_number,account_type,currency,
             balance,credit_limit,status,opened_date)
            VALUES (?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Accounts done.\n")

# ── 3. KYC Verifications ─────────────────────────────────
def generate_kyc(cursor):
    print("Generating KYC verifications...")
    cursor.execute("SELECT customer_id FROM core.customers")
    customer_ids = [r.customer_id for r in cursor.fetchall()]
    batch = []
    for cid in customer_ids:
        verified_at = rnd_date(400, 10)
        batch.append((
            cid,
            random.choice(DOC_TYPES),
            str(uuid.uuid4())[:20].upper(),
            random.choice(['automated_kyc','agent_smith','agent_jones','agent_chen']),
            verified_at,
            (verified_at + timedelta(days=random.randint(365,1825))).date(),
            random.choices(['APPROVED','PENDING','REJECTED'], weights=[75,15,10])[0],
            fake.sentence(nb_words=6),
        ))
        if len(batch) >= 500:
            cursor.executemany("""
                INSERT INTO core.kyc_verifications
                (customer_id,document_type,document_number,verified_by,
                 verified_at,expiry_date,outcome,notes)
                VALUES (?,?,?,?,?,?,?,?)
            """, batch)
            batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO core.kyc_verifications
            (customer_id,document_type,document_number,verified_by,
             verified_at,expiry_date,outcome,notes)
            VALUES (?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ KYC done.\n")

# ── 4. Payment Methods ───────────────────────────────────
def generate_payment_methods(cursor):
    print("Generating payment methods...")
    cursor.execute("SELECT customer_id FROM core.customers")
    customer_ids = [r.customer_id for r in cursor.fetchall()]
    batch = []
    for cid in customer_ids:
        n_methods = random.choices([1,2,3], weights=[40,40,20])[0]
        for i in range(n_methods):
            batch.append((
                cid,
                random.choice(METHODS),
                str(random.randint(1000,9999)),
                random.randint(1,12),
                random.randint(2025,2030),
                1 if i == 0 else 0,
                1,
            ))
            if len(batch) >= 500:
                cursor.executemany("""
                    INSERT INTO payments.payment_methods
                    (customer_id,method_type,last_four,expiry_month,expiry_year,is_default,is_active)
                    VALUES (?,?,?,?,?,?,?)
                """, batch)
                batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO payments.payment_methods
            (customer_id,method_type,last_four,expiry_month,expiry_year,is_default,is_active)
            VALUES (?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Payment methods done.\n")

# ── 5. Transactions ──────────────────────────────────────
def generate_transactions(cursor):
    print("Generating 100,000 transactions...")
    cursor.execute("SELECT account_id FROM core.accounts WHERE status='ACTIVE'")
    account_ids = [r.account_id for r in cursor.fetchall()]
    batch = []
    for i in range(100000):
        amount     = round(random.uniform(1, 15000), 2)
        fraud_flag = 1 if random.random() < 0.025 else 0
        txn_date   = rnd_date(730, 0)
        batch.append((
            random.choice(account_ids),
            random.choice(TXN_TYPES),
            amount,
            'CAD',
            1.0,
            amount,
            random.choice(CHANNELS),
            random.choice(MERCHANTS),
            random.choice(MCC),
            fake.sentence(nb_words=4),
            'TXN-' + str(uuid.uuid4())[:13],
            random.choices(['COMPLETED','COMPLETED','COMPLETED','PENDING','FAILED'], weights=[80,5,5,7,3])[0],
            fraud_flag,
            round(random.uniform(0.5,1),4) if fraud_flag else round(random.uniform(0,0.3),4),
            txn_date,
        ))
        if len(batch) >= 1000:
            cursor.executemany("""
                INSERT INTO payments.transactions
                (account_id,transaction_type,amount,currency,fx_rate,cad_equivalent,
                 channel,merchant_name,merchant_category,description,reference_number,
                 status,fraud_flag,fraud_score,transaction_date)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            batch = []
        if i % 10000 == 0 and i > 0:
            print(f"  {i:,} transactions inserted...")
    if batch:
        cursor.executemany("""
            INSERT INTO payments.transactions
            (account_id,transaction_type,amount,currency,fx_rate,cad_equivalent,
             channel,merchant_name,merchant_category,description,reference_number,
             status,fraud_flag,fraud_score,transaction_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Transactions done.\n")

# ── 6. Fraud Alerts ──────────────────────────────────────
def generate_fraud_alerts(cursor):
    print("Generating fraud alerts...")
    cursor.execute("SELECT transaction_id FROM payments.transactions WHERE fraud_flag=1")
    txn_ids = [r.transaction_id for r in cursor.fetchall()]
    batch = []
    for tid in txn_ids:
        batch.append((
            tid,
            random.choice(ALERT_TYPES),
            random.choices(SEVERITIES, weights=[30,40,20,10])[0],
            round(random.uniform(0.5,1.0),4),
            random.choice(['RULE_001','RULE_002','RULE_003','RULE_004','ML_MODEL_V2']),
            random.choices(['OPEN','RESOLVED','ESCALATED'], weights=[50,35,15])[0],
            random.choice([None,'analyst_maria','analyst_john','analyst_priya']),
            rnd_date(10,0) if random.random() > 0.5 else None,
            fake.sentence(nb_words=8),
        ))
        if len(batch) >= 500:
            cursor.executemany("""
                INSERT INTO risk.fraud_alerts
                (transaction_id,alert_type,severity,ml_score,rule_triggered,
                 status,investigated_by,resolved_at,notes)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, batch)
            batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO risk.fraud_alerts
            (transaction_id,alert_type,severity,ml_score,rule_triggered,
             status,investigated_by,resolved_at,notes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Fraud alerts done.\n")

# ── 7. AML Screenings ────────────────────────────────────
def generate_aml(cursor):
    print("Generating AML screenings...")
    cursor.execute("SELECT customer_id FROM core.customers")
    customer_ids = [r.customer_id for r in cursor.fetchall()]
    batch = []
    for cid in customer_ids:
        n_screens = random.choices([1,2], weights=[70,30])[0]
        for _ in range(n_screens):
            risk_score = round(random.uniform(0,1),4)
            batch.append((
                cid,
                random.choice(SCREEN_TYPES),
                1 if risk_score > 0.85 else 0,
                1 if risk_score > 0.90 else 0,
                1 if risk_score > 0.95 else 0,
                risk_score,
                random.choices(OUTCOMES, weights=[60,20,10,10,5,5])[0],
                rnd_date(365,0),
                (datetime.utcnow() + timedelta(days=random.randint(90,365))).date(),
            ))
            if len(batch) >= 500:
                cursor.executemany("""
                    INSERT INTO risk.aml_screenings
                    (customer_id,screening_type,watchlist_hit,pep_flag,sanction_flag,
                     risk_score,outcome,screened_at,next_review_date)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, batch)
                batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO risk.aml_screenings
            (customer_id,screening_type,watchlist_hit,pep_flag,sanction_flag,
             risk_score,outcome,screened_at,next_review_date)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ AML screenings done.\n")

# ── 8. Trades ────────────────────────────────────────────
def generate_trades(cursor):
    print("Generating 25,000 trades...")
    cursor.execute("SELECT customer_id FROM core.customers")
    customer_ids = [r.customer_id for r in cursor.fetchall()]
    trading_customers = random.sample(customer_ids, 3000)
    batch = []
    for _ in range(25000):
        price    = round(random.uniform(10, 5000), 4)
        quantity = round(random.uniform(1, 10000), 2)
        trade_date = rnd_date(730, 0)
        batch.append((
            random.choice(trading_customers),
            random.choice(INST_TYPES),
            random.choice(INSTRUMENTS),
            random.choice(DIRECTIONS),
            quantity,
            price,
            round(price * quantity, 2),
            round(random.uniform(0,50),2),
            random.choice(VENUES),
            (trade_date + timedelta(days=2)).date(),
            random.choices(['EXECUTED','EXECUTED','CANCELLED','SETTLED'], weights=[70,15,10,5])[0],
            trade_date,
        ))
        if len(batch) >= 1000:
            cursor.executemany("""
                INSERT INTO trading.trades
                (customer_id,instrument_type,instrument_code,direction,quantity,
                 price,notional_cad,commission,venue,settlement_date,status,trade_date)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO trading.trades
            (customer_id,instrument_type,instrument_code,direction,quantity,
             price,notional_cad,commission,venue,settlement_date,status,trade_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Trades done.\n")

# ── 9. Positions ─────────────────────────────────────────
def generate_positions(cursor):
    print("Generating positions...")
    cursor.execute("SELECT customer_id FROM core.customers")
    customer_ids = [r.customer_id for r in cursor.fetchall()]
    trading_customers = random.sample(customer_ids, 2000)
    batch = []
    for cid in trading_customers:
        n_pos = random.choices([1,2,3,4], weights=[40,30,20,10])[0]
        held_instruments = random.sample(INSTRUMENTS, min(n_pos, len(INSTRUMENTS)))
        for inst in held_instruments:
            qty      = round(random.uniform(1, 5000), 2)
            avg_cost = round(random.uniform(10, 3000), 4)
            cur_price= round(avg_cost * random.uniform(0.7, 1.4), 4)
            mkt_val  = round(qty * cur_price, 2)
            pnl      = round(mkt_val - (qty * avg_cost), 2)
            batch.append((cid, inst, qty, avg_cost, cur_price, mkt_val, pnl))
            if len(batch) >= 500:
                cursor.executemany("""
                    INSERT INTO trading.positions
                    (customer_id,instrument_code,quantity_held,avg_cost_cad,
                     current_price,market_value_cad,unrealised_pnl)
                    VALUES (?,?,?,?,?,?,?)
                """, batch)
                batch = []
    if batch:
        cursor.executemany("""
            INSERT INTO trading.positions
            (customer_id,instrument_code,quantity_held,avg_cost_cad,
             current_price,market_value_cad,unrealised_pnl)
            VALUES (?,?,?,?,?,?,?)
        """, batch)
    print("  ✓ Positions done.\n")

# ── Main ─────────────────────────────────────────────────
def main():
    conn   = connect()
    cursor = conn.cursor()

    generate_customers(cursor)
    generate_accounts(cursor)
    generate_kyc(cursor)
    generate_payment_methods(cursor)
    generate_transactions(cursor)
    generate_fraud_alerts(cursor)
    generate_aml(cursor)
    generate_trades(cursor)
    generate_positions(cursor)

    conn.close()
    print("=" * 40)
    print("All data generated successfully!")
    print("=" * 40)

if __name__ == "__main__":
    main()