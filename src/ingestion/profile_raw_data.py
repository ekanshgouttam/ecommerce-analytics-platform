from pathlib import Path
from zipfile import ZipFile
import csv
from collections import Counter


RAW_DIR = Path("data/raw")

FILES = [
    "2019-Oct.csv.zip",
    "2019-Nov.csv.zip",
    "2019-Dec.csv.zip",
    "2020-Jan.csv.zip",
    "2020-Feb.csv.zip",
]


def profile_file(zip_path: Path):
    print(f"\n{'=' * 70}")
    print(f"FILE: {zip_path.name}")
    print("=" * 70)

    with ZipFile(zip_path) as z:
        csv_files = z.namelist()

        if not csv_files:
            print("ERROR: ZIP contains no files.")
            return

        csv_name = csv_files[0]
        print(f"CSV inside ZIP: {csv_name}")

        with z.open(csv_name) as f:
            reader = csv.DictReader(
                (line.decode("utf-8") for line in f)
            )

            columns = reader.fieldnames

            print("\nColumns:")
            for column in columns:
                print(f"  - {column}")

            row_count = 0
            event_counts = Counter()
            unique_users = set()
            unique_sessions = set()
            unique_products = set()
            unique_categories = set()
            unique_brands = set()

            null_counts = Counter()

            min_time = None
            max_time = None

            for row in reader:
                row_count += 1

                # Event statistics
                event_type = row["event_type"]
                event_counts[event_type] += 1

                # Unique entities
                if row["user_id"]:
                    unique_users.add(row["user_id"])
                else:
                    null_counts["user_id"] += 1

                if row["user_session"]:
                    unique_sessions.add(row["user_session"])
                else:
                    null_counts["user_session"] += 1

                if row["product_id"]:
                    unique_products.add(row["product_id"])
                else:
                    null_counts["product_id"] += 1

                if row["category_id"]:
                    unique_categories.add(row["category_id"])
                else:
                    null_counts["category_id"] += 1

                if row["brand"]:
                    unique_brands.add(row["brand"])
                else:
                    null_counts["brand"] += 1

                # Timestamp
                timestamp = row["event_time"]

                if min_time is None or timestamp < min_time:
                    min_time = timestamp

                if max_time is None or timestamp > max_time:
                    max_time = timestamp

                # Null detection for all columns
                for column, value in row.items():
                    if value == "":
                        null_counts[column] += 1

    print(f"\nRows:              {row_count:,}")
    print(f"Unique users:      {len(unique_users):,}")
    print(f"Unique sessions:   {len(unique_sessions):,}")
    print(f"Unique products:   {len(unique_products):,}")
    print(f"Unique categories: {len(unique_categories):,}")
    print(f"Unique brands:     {len(unique_brands):,}")

    print("\nEvent types:")
    for event, count in event_counts.most_common():
        print(f"  {event:<20} {count:,}")

    print("\nDate range:")
    print(f"  First event: {min_time}")
    print(f"  Last event:  {max_time}")

    print("\nMissing values:")
    for column, count in null_counts.items():
        if count > 0:
            print(f"  {column:<20} {count:,}")


def main():
    print("REES46 COSMETICS DATASET PROFILER")
    print("=" * 70)

    for filename in FILES:
        zip_path = RAW_DIR / filename

        if not zip_path.exists():
            print(f"\nWARNING: Missing file: {zip_path}")
            continue

        profile_file(zip_path)


if __name__ == "__main__":
    main()