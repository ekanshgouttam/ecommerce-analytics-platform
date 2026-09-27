from src.utils.db import get_connection

conn = get_connection()
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*), MIN(event_date), MAX(event_date) FROM staging_events")
    print(cur.fetchone())
    cur.execute("SELECT event_type, COUNT(*) FROM staging_events GROUP BY event_type ORDER BY 2 DESC")
    for row in cur.fetchall():
        print(row)
conn.close()