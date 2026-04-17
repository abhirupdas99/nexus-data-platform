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
