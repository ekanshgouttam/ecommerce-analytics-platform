from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
BRONZE_DIR = PROCESSED_DIR / "bronze"

for _d in (RAW_DIR, BRONZE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

RAW_FILENAMES = [
    "2019-Oct.csv.zip",
    "2019-Nov.csv.zip",
    "2019-Dec.csv.zip",
    "2020-Jan.csv.zip",
    "2020-Feb.csv.zip",
]

RAW_EVENT_COLUMNS = [
    "event_time", "event_type", "product_id", "category_id",
    "category_code", "brand", "price", "user_id", "user_session",
]

VALID_EVENT_TYPES = {"view", "cart", "remove_from_cart", "purchase"}