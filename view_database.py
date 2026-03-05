"""
Simple script to view what's in the habits.db database
"""

import sqlite3
from pathlib import Path

db_path = "data/habits.db"

if not Path(db_path).exists():
    print(f"Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("DATABASE CONTENTS")
print("="*60)

# Show all habits
print("\n--- HABITS TABLE ---")
cursor.execute("SELECT * FROM habits")
habits = cursor.fetchall()

if habits:
    for row in habits:
        print(f"\nHabit ID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  Description: {row[2]}")
        print(f"  Periodicity: {row[3]}")
        print(f"  Created at: {row[4]}")
else:
    print("  (No habits found)")

# Show all completion events
print("\n\n--- COMPLETION EVENTS TABLE ---")
cursor.execute("SELECT * FROM completion_events")
events = cursor.fetchall()

if events:
    for row in events:
        print(f"\nEvent ID: {row[0]}")
        print(f"  Habit ID: {row[1]}")
        print(f"  Completed at: {row[2]}")
else:
    print("  (No completion events found)")

# Show table structure
print("\n\n--- DATABASE SCHEMA ---")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
schemas = cursor.fetchall()

for schema in schemas:
    print(f"\n{schema[0]}")

conn.close()

print("\n" + "="*60)
