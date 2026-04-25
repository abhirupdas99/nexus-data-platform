# ============================================================
# PROJECT NEXUS - Step 2: Azure Infrastructure Provisioning
# Run from: C:\Users\wwwda\Downloads\nexus project
# ============================================================

# ----- My CONFIGURATION (already set) -----
$SUFFIX      = "abhirup"           # Your suffix — do not change
$LOCATION    = "canadacentral"            # Must match existing RG, Storage, and KV
$RG          = "nexus-rg"

# Auto-generated names from suffix
$STORAGE     = "nexusstorage$SUFFIX"    # nexusstorageabhirup
$SQLSERVER   = "nexus-sql-$SUFFIX" # nexus-sqlserver-abhirup
$KEYVAULT    = "nexus-kv-$SUFFIX"       # nexus-kv-abhirup 
$EHNAMESPACE = "nexus-eh-$SUFFIX"       # nexus-eh-abhirup
$WORKSPACE   = "nexus-law-$SUFFIX"      # nexus-law-abhirup
$ADF         = "nexus-adf-$SUFFIX"      # nexus-adf-abhirup
$DATABRICKS  = "nexus-dbr-$SUFFIX"      # provisioned in Step 5

# SQL credentials
$SQL_ADMIN   = "nexusadmin"
$SQL_PASS    = "NexusP@ss2026!"

Write-Host '✓ Variables set. Starting provisioning...' -ForegroundColor Green
