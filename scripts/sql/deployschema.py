import pyodbc
import time

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=nexus-sql-abhirup.database.windows.net;"
    "DATABASE=clearbank-db;"
    "UID=nexusadmin;"
    "PWD=NexusP@ss2026!;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

schemas = [
    "IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='core')     EXEC('CREATE SCHEMA core')",
    "IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='payments') EXEC('CREATE SCHEMA payments')",
    "IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='risk')     EXEC('CREATE SCHEMA risk')",
    "IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='trading')  EXEC('CREATE SCHEMA trading')",
    "IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='meta')     EXEC('CREATE SCHEMA meta')",
]

tables = [

    # core.customers
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='core' AND t.name='customers')
    CREATE TABLE core.customers (
        customer_id   INT           IDENTITY(1,1) PRIMARY KEY,
        full_name     NVARCHAR(200) NOT NULL,
        email         NVARCHAR(200) NOT NULL UNIQUE,
        phone         NVARCHAR(20),
        date_of_birth DATE,
        nationality   NVARCHAR(100),
        address_line1 NVARCHAR(300),
        city          NVARCHAR(100),
        province      NVARCHAR(100),
        postal_code   NVARCHAR(20),
        country       NVARCHAR(100) DEFAULT 'Canada',
        risk_rating   NVARCHAR(10)  CHECK (risk_rating IN ('LOW','MEDIUM','HIGH')),
        kyc_status    NVARCHAR(20)  DEFAULT 'PENDING',
        segment       NVARCHAR(50),
        created_at    DATETIME2     DEFAULT GETUTCDATE(),
        updated_at    DATETIME2     DEFAULT GETUTCDATE()
    )
    """,

    # core.accounts
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='core' AND t.name='accounts')
    CREATE TABLE core.accounts (
        account_id     INT           IDENTITY(1,1) PRIMARY KEY,
        customer_id    INT           NOT NULL REFERENCES core.customers(customer_id),
        account_number NVARCHAR(30)  NOT NULL UNIQUE,
        account_type   NVARCHAR(30)  CHECK (account_type IN ('CHEQUING','SAVINGS','TFSA','RRSP','LOC')),
        currency       CHAR(3)       DEFAULT 'CAD',
        balance        DECIMAL(18,2) DEFAULT 0.00,
        credit_limit   DECIMAL(18,2) DEFAULT 0.00,
        status         NVARCHAR(20)  DEFAULT 'ACTIVE',
        opened_date    DATE          DEFAULT CAST(GETUTCDATE() AS DATE),
        closed_date    DATE,
        created_at     DATETIME2     DEFAULT GETUTCDATE()
    )
    """,

    # core.kyc_verifications
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='core' AND t.name='kyc_verifications')
    CREATE TABLE core.kyc_verifications (
        kyc_id          INT          IDENTITY(1,1) PRIMARY KEY,
        customer_id     INT          NOT NULL REFERENCES core.customers(customer_id),
        document_type   NVARCHAR(50),
        document_number NVARCHAR(100),
        verified_by     NVARCHAR(100),
        verified_at     DATETIME2,
        expiry_date     DATE,
        outcome         NVARCHAR(20) CHECK (outcome IN ('APPROVED','REJECTED','PENDING')),
        notes           NVARCHAR(MAX),
        created_at      DATETIME2    DEFAULT GETUTCDATE()
    )
    """,

    # payments.transactions
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='payments' AND t.name='transactions')
    CREATE TABLE payments.transactions (
        transaction_id   BIGINT        IDENTITY(1,1) PRIMARY KEY,
        account_id       INT           NOT NULL REFERENCES core.accounts(account_id),
        transaction_type NVARCHAR(30)  CHECK (transaction_type IN ('DEBIT','CREDIT','TRANSFER','FX','PAYMENT')),
        amount           DECIMAL(18,2) NOT NULL,
        currency         CHAR(3)       DEFAULT 'CAD',
        fx_rate          DECIMAL(10,6) DEFAULT 1.000000,
        cad_equivalent   DECIMAL(18,2),
        channel          NVARCHAR(30),
        merchant_name    NVARCHAR(200),
        merchant_category NVARCHAR(100),
        description      NVARCHAR(500),
        reference_number NVARCHAR(100) UNIQUE,
        status           NVARCHAR(20)  DEFAULT 'COMPLETED',
        fraud_flag       BIT           DEFAULT 0,
        fraud_score      DECIMAL(5,4)  DEFAULT 0.0000,
        transaction_date DATETIME2     NOT NULL,
        created_at       DATETIME2     DEFAULT GETUTCDATE()
    )
    """,

    # Index on transactions
    """
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_transactions_date')
    CREATE INDEX IX_transactions_date ON payments.transactions(transaction_date)
    """,

    # payments.payment_methods
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='payments' AND t.name='payment_methods')
    CREATE TABLE payments.payment_methods (
        method_id    INT          IDENTITY(1,1) PRIMARY KEY,
        customer_id  INT          NOT NULL REFERENCES core.customers(customer_id),
        method_type  NVARCHAR(30) CHECK (method_type IN ('VISA','MASTERCARD','AMEX','INTERAC','WIRE','EFT')),
        last_four    CHAR(4),
        expiry_month TINYINT,
        expiry_year  SMALLINT,
        is_default   BIT          DEFAULT 0,
        is_active    BIT          DEFAULT 1,
        created_at   DATETIME2    DEFAULT GETUTCDATE()
    )
    """,

    # risk.fraud_alerts
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='risk' AND t.name='fraud_alerts')
    CREATE TABLE risk.fraud_alerts (
        alert_id        INT          IDENTITY(1,1) PRIMARY KEY,
        transaction_id  BIGINT       NOT NULL REFERENCES payments.transactions(transaction_id),
        alert_type      NVARCHAR(50),
        severity        NVARCHAR(20) CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
        ml_score        DECIMAL(5,4),
        rule_triggered  NVARCHAR(100),
        status          NVARCHAR(20) DEFAULT 'OPEN',
        investigated_by NVARCHAR(100),
        resolved_at     DATETIME2,
        notes           NVARCHAR(MAX),
        created_at      DATETIME2    DEFAULT GETUTCDATE()
    )
    """,

    # risk.aml_screenings
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='risk' AND t.name='aml_screenings')
    CREATE TABLE risk.aml_screenings (
        screening_id     INT          IDENTITY(1,1) PRIMARY KEY,
        customer_id      INT          NOT NULL REFERENCES core.customers(customer_id),
        screening_type   NVARCHAR(50),
        watchlist_hit    BIT          DEFAULT 0,
        pep_flag         BIT          DEFAULT 0,
        sanction_flag    BIT          DEFAULT 0,
        risk_score       DECIMAL(5,4),
        outcome          NVARCHAR(20) CHECK (outcome IN ('CLEAR','REVIEW','ESCALATE','BLOCK')),
        screened_at      DATETIME2    DEFAULT GETUTCDATE(),
        next_review_date DATE
    )
    """,

    # trading.trades
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='trading' AND t.name='trades')
    CREATE TABLE trading.trades (
        trade_id        BIGINT        IDENTITY(1,1) PRIMARY KEY,
        customer_id     INT           NOT NULL REFERENCES core.customers(customer_id),
        instrument_type NVARCHAR(20)  CHECK (instrument_type IN ('EQUITY','FX','FIXED_INCOME','ETF','OPTION')),
        instrument_code NVARCHAR(20),
        direction       NVARCHAR(10)  CHECK (direction IN ('BUY','SELL','SHORT')),
        quantity        DECIMAL(18,6) NOT NULL,
        price           DECIMAL(18,6) NOT NULL,
        notional_cad    DECIMAL(18,2),
        commission      DECIMAL(10,2) DEFAULT 0.00,
        venue           NVARCHAR(50),
        settlement_date DATE,
        status          NVARCHAR(20)  DEFAULT 'EXECUTED',
        trade_date      DATETIME2     NOT NULL,
        created_at      DATETIME2     DEFAULT GETUTCDATE()
    )
    """,

    # trading.positions
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='trading' AND t.name='positions')
    CREATE TABLE trading.positions (
        position_id      INT           IDENTITY(1,1) PRIMARY KEY,
        customer_id      INT           NOT NULL REFERENCES core.customers(customer_id),
        instrument_code  NVARCHAR(20)  NOT NULL,
        quantity_held    DECIMAL(18,6) NOT NULL,
        avg_cost_cad     DECIMAL(18,6) NOT NULL,
        current_price    DECIMAL(18,6),
        market_value_cad DECIMAL(18,2),
        unrealised_pnl   DECIMAL(18,2),
        last_updated     DATETIME2     DEFAULT GETUTCDATE()
    )
    """,

    # meta.watermarks
    """
    IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id
                   WHERE s.name='meta' AND t.name='watermarks')
    CREATE TABLE meta.watermarks (
        watermark_id    INT           IDENTITY(1,1) PRIMARY KEY,
        table_name      NVARCHAR(100) NOT NULL UNIQUE,
        last_watermark  DATETIME2     NOT NULL,
        last_run_status NVARCHAR(20)  DEFAULT 'SUCCESS',
        rows_loaded     INT           DEFAULT 0,
        pipeline_name   NVARCHAR(100),
        updated_at      DATETIME2     DEFAULT GETUTCDATE()
    )
    """,

    # Seed watermarks
    """
    IF NOT EXISTS (SELECT 1 FROM meta.watermarks WHERE table_name='payments.transactions')
    INSERT INTO meta.watermarks (table_name, last_watermark, pipeline_name) VALUES
        ('payments.transactions', '2020-01-01 00:00:00', 'pl_transactions_to_bronze'),
        ('trading.trades',        '2020-01-01 00:00:00', 'pl_trades_to_bronze'),
        ('core.customers',        '2020-01-01 00:00:00', 'pl_customers_to_bronze'),
        ('risk.fraud_alerts',     '2020-01-01 00:00:00', 'pl_fraud_to_bronze')
    """,
]

def deploy():
    print("Connecting to clearbank-db...")
    for attempt in range(1, 6):
        try:
            conn = pyodbc.connect(conn_str, timeout=30)
            print("Connected.\n")
            break
        except Exception as e:
            if "40613" in str(e):
                print(f"  Database waking up — attempt {attempt}/5, waiting 20s...")
                time.sleep(20)
            else:
                raise

    conn.autocommit = True
    cursor = conn.cursor()

    print("Creating schemas...")
    for stmt in schemas:
        cursor.execute(stmt)
    print("  Schemas done.\n")

    print("Creating tables...")
    for i, stmt in enumerate(tables, 1):
        try:
            cursor.execute(stmt)
            print(f"  Statement {i}/{len(tables)} done.")
        except Exception as e:
            print(f"  Statement {i} FAILED: {e}")
            raise

    conn.close()
    print("\nSchema deployed successfully.")

if __name__ == "__main__":
    deploy()