"""
Generate dummy Iceberg table on GCS.

pip install pyiceberg[gcs] pyarrow gcsfs sqlalchemy
"""
from pyiceberg.catalog.sql import SqlCatalog
import pyarrow as pa

# Update with your project and bucket
PROJECT_ID = "payments-dev-495611"
BUCKET = "demobucket_na"

catalog = SqlCatalog(
    "demo",
    **{
        "uri": "sqlite:///iceberg_catalog.db",
        "warehouse": f"gs://{BUCKET}/warehouse",
    }
)

schema = pa.schema([
    pa.field("id", pa.string()),
    pa.field("source_event_id", pa.string()),
    pa.field("payment_id", pa.string()),
    pa.field("payload", pa.string()),
    pa.field("created_by", pa.string()),
    pa.field("created_at", pa.timestamp("us")),
    pa.field("last_updated_by", pa.string()),
    pa.field("last_updated_at", pa.timestamp("us")),
    pa.field("amway_country", pa.string()),
    pa.field("amway_vertical", pa.string()),
    pa.field("amway_tenant", pa.string()),
    pa.field("amway_channel", pa.string()),
    pa.field("project_version", pa.string()),
    pa.field("version", pa.int64()),
    pa.field("eligible_payments", pa.string()),
    pa.field("eligible_refunds", pa.string()),
    pa.field("status", pa.string()),
])

catalog.create_namespace_if_not_exists("db")
table = catalog.create_table("db.payments", schema=schema)

data = pa.table({
    "id": ["uuid-001", "uuid-002", "uuid-003", "uuid-004", "uuid-005"],
    "source_event_id": ["evt-101", "evt-102", "evt-103", "evt-104", "evt-105"],
    "payment_id": ["pay-201", "pay-202", "pay-203", "pay-204", "pay-205"],
    "payload": [
        '{"amount": 150.00, "currency": "USD"}',
        '{"amount": 89.99, "currency": "EUR"}',
        '{"amount": 250.50, "currency": "USD"}',
        '{"amount": 45.00, "currency": "GBP"}',
        '{"amount": 1200.00, "currency": "USD"}',
    ],
    "created_by": ["system", "admin", "system", "user-10", "system"],
    "created_at": [
        pa.scalar(1717232400000000, type=pa.timestamp("us")),
        pa.scalar(1717335000000000, type=pa.timestamp("us")),
        pa.scalar(1717402500000000, type=pa.timestamp("us")),
        pa.scalar(1717516500000000, type=pa.timestamp("us")),
        pa.scalar(1717582800000000, type=pa.timestamp("us")),
    ],
    "last_updated_by": ["system", "admin", "batch-job", "user-10", "system"],
    "last_updated_at": [
        pa.scalar(1717232400000000, type=pa.timestamp("us")),
        pa.scalar(1717398000000000, type=pa.timestamp("us")),
        pa.scalar(1717412400000000, type=pa.timestamp("us")),
        pa.scalar(1717573800000000, type=pa.timestamp("us")),
        pa.scalar(1717582800000000, type=pa.timestamp("us")),
    ],
    "amway_country": ["US", "DE", "US", "GB", "IN"],
    "amway_vertical": ["health", "beauty", "nutrition", "health", "home"],
    "amway_tenant": ["tenant-1", "tenant-2", "tenant-1", "tenant-3", "tenant-4"],
    "amway_channel": ["online", "retail", "online", "mobile", "online"],
    "project_version": ["1.0.0", "1.0.0", "1.1.0", "1.1.0", "2.0.0"],
    "version": [1, 1, 2, 1, 1],
    "eligible_payments": ["credit_card", "bank_transfer", "credit_card,debit_card", "paypal", "upi"],
    "eligible_refunds": ["full", "partial", "full", "none", "full"],
    "status": ["ACTIVE", "ACTIVE", "COMPLETED", "PENDING", "ACTIVE"],
})

table.append(data)
print("Done! Iceberg table created at:")
print(f"  gs://{BUCKET}/warehouse/db/payments/metadata/")
