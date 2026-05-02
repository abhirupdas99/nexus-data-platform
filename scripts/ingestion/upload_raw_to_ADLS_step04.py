from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────
STORAGE_ACCOUNT = "nexusstorageabhirup"
CONTAINER       = "raw-landing"
LOCAL_DIR       = Path("C:\\Users\\wwwda\\Downloads\\nexus project\\data\\raw")
TODAY           = datetime.utcnow().strftime("%Y/%m/%d")

# ── Authenticate via Azure CLI login ─────────────────────
print("Authenticating to Azure...")
credential       = DefaultAzureCredential()
client           = BlobServiceClient(
    f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=credential
)
container_client = client.get_container_client(CONTAINER)
print("  ✓ Authenticated\n")

# ── Upload ───────────────────────────────────────────────
def upload_files():
    files = sorted(LOCAL_DIR.iterdir())
    print(f"Uploading {len(files)} files to {CONTAINER}/ingest/{TODAY}/\n")
    print(f"  {'File':<35} {'Size':>10}  Status")
    print(f"  {'-'*35} {'-'*10}  ------")

    total_bytes = 0
    for filepath in files:
        if not filepath.is_file():
            continue
        blob_name  = f"ingest/{TODAY}/{filepath.name}"
        size_kb    = filepath.stat().st_size / 1024
        total_bytes += filepath.stat().st_size

        with open(filepath, "rb") as data:
            container_client.upload_blob(
                name=blob_name,
                data=data,
                overwrite=True
            )

        if size_kb >= 1024:
            size_str = f"{size_kb/1024:.1f} MB"
        else:
            size_str = f"{size_kb:.1f} KB"

        print(f"  {filepath.name:<35} {size_str:>10}  ✓ Uploaded")

    print(f"\n{'='*55}")
    print(f"All files uploaded successfully!")
    print(f"Container : {CONTAINER}")
    print(f"Path      : ingest/{TODAY}/")
    print(f"Total size: {total_bytes/1024/1024:.1f} MB")
    print(f"{'='*55}")
    print(f"\n✓ Files are ready for ADF ingestion in Step 4.")

if __name__ == "__main__":
    upload_files()