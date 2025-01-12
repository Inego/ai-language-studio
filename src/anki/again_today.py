import sqlite3
import datetime
import argparse
import sys

parser = argparse.ArgumentParser(description='Process Anki cards reviewed today with ease 1.')
parser.add_argument('db_path', help='Path to the Anki collection.anki2 database file')
args = parser.parse_args()

try:
    conn = sqlite3.connect(args.db_path)
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Error connecting to the database: {e}")
    sys.exit(1)

# Get today's date in seconds since the epoch
today = datetime.date.today()
today_start = int(datetime.datetime(today.year, today.month, today.day).timestamp())

# Select cards reviewed today with ease 1 (Again), joining with decks and ordering by deck name
cursor.execute('''
    SELECT d.name, n.flds
    FROM revlog r
    JOIN cards c ON r.cid = c.id
    JOIN notes n ON c.nid = n.id
    JOIN decks d ON c.did = d.id
    WHERE r.ease = 1 AND r.id > ?
    ORDER BY d.name COLLATE BINARY
''', (today_start * 1000,))

results = cursor.fetchall()

current_deck = None
for deck_name, fields_str in results:
    fields = fields_str.split('\x1f')
    first_field = fields[0] if fields else ""

    if deck_name != current_deck:
        current_deck = deck_name
        print(f"{deck_name}:")

    print(f"  {first_field}")

conn.close()
