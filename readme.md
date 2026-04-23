// create folder structure from scratch

$folders = @(
  "adf/pipelines","adf/datasets","adf/linked_services","adf/triggers",
  "databricks/notebooks","databricks/schemas","databricks/jobs",
  "scripts/setup","scripts/ingestion","scripts/streaming","scripts/quality",
  "kql/dashboards","kql/alerts","kql/investigation",
  "sql/schema","sql/queries","sql/stored_procedures",
  "data/samples","docs","config","tests"
)
$folders | ForEach-Object { New-Item -ItemType Directory -Force -Path $\_ }

> End-to-end Azure data platform processing 6.3M+ banking transactions
> through a production-grade medallion architecture.

## Architecture

```
8 Data Sources → ADF Ingestion → ADLS Bronze → Databricks
→ ADLS Silver → Databricks → ADLS Gold → Power BI / Databricks SQL
                                     ↓
                         Azure Monitor + KQL Observability
```

## Technology Stack

| Layer          | Technology                      |
| -------------- | ------------------------------- |
| Ingestion      | Azure Data Factory + Event Hubs |
| Storage        | ADLS Gen2 + Delta Lake          |
| Transformation | Databricks + PySpark            |
| Orchestration  | ADF Pipelines + Triggers        |
| Monitoring     | Azure Monitor + KQL + Workbooks |
| Serving        | Power BI + Databricks SQL       |
| Security       | Azure Key Vault + RBAC          |

## Data Sources (8 Heterogeneous)

- PaySim Transactions (6.3M rows, CSV)
- Customer Master Data (SQL Server, CDC incremental)
- Insurance Claims (nested JSON)
- Market Price Feed (real-time streaming via Event Hubs)
- Loan Applications (PDF, Azure Form Recognizer)
- Legacy Banking Feed (XML)
- Web Clickstream (streaming via Event Hubs)
- Portfolio Holdings (Parquet, quarterly)

## Key Engineering Challenges Solved

- Schema drift detection and auto-healing
- Exactly-once streaming with Delta MERGE
- Late-arriving data with 30-day watermarks
- Data skew resolution with broadcast joins
- Small files compaction with OPTIMIZE ZORDER
- Incremental loading with CDC watermark pattern
- Zero-row silent failure alerting (KQL)
- Secret rotation with Azure Key Vault RBAC

## Status

- [x] Step 1: Development environment setup
- [ ] Step 2: Azure infrastructure provisioning
- [ ] Step 3: Bronze ingestion layer
- [ ] Step 4: Silver transformation layer
- [ ] Step 5: Gold aggregation layer
- [ ] Step 6: Monitoring and alerting
- [ ] Step 7: Power BI dashboard

---

_Built to demonstrate enterprise Azure data engineering skills
for a Data Platform Support Engineer role._
