"""
Seed script: create 5 predefined habits + 4 weeks of completion data.

Usage:
  python seed_data.py --reset
  python seed_data.py --db-path "data/habits.db" --reset

Notes:
- Uses your HabitDatabase methods (create_habit, record_completion).
- Data is deterministic (no randomness), so it's suitable for tests.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from habit import Habit
from database import HabitDatabase


def _dt(d: datetime, hour: int, minute: int) -> datetime:
  """Return datetime on the same date with a fixed time."""
  return d.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _date_range(start_date: datetime, days: int) -> list[datetime]:
  """Generate [start_date, start_date+1day, ...] as datetimes at 00:00."""
  base = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
  return [base + timedelta(days=i) for i in range(days)]


def seed(db_path: str, reset: bool) -> None:
  db_file = Path(db_path)

  if reset and db_file.exists():
    db_file.unlink()

  db = HabitDatabase(db_path)

  # 4 weeks = 28 days. Use a fixed window ending today (inclusive).
  today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  start = today - timedelta(days=27)
  days = _date_range(start, 28)

  # Create habits at the start date (so completions make logical sense)
  habit_creation_date = start.replace(hour=6, minute=0)

  # 5 predefined habits (3 daily, 2 weekly)
  predefined = [
    Habit(name="Morning walk", description="10 minutes walk after waking up", periodicity="daily", created_at=habit_creation_date),
    Habit(name="Drink water", description="Drink at least 2 liters of water", periodicity="daily", created_at=habit_creation_date),
    Habit(name="Read book", description="Read 20 minutes", periodicity="daily", created_at=habit_creation_date),
    Habit(name="Weekly review", description="Review goals and plan next week", periodicity="weekly", created_at=habit_creation_date),
    Habit(name="Call family", description="Call family or close friend", periodicity="weekly", created_at=habit_creation_date),
  ]

  # Create habits and store their IDs
  habit_ids: dict[str, int] = {}
  for habit in predefined:
    hid = db.create_habit(habit)
    habit_ids[habit.name] = hid

  # Daily completion patterns (realistic with misses)
  # - Morning walk: misses ~4 days
  walk_miss_days = {3, 10, 17, 24}
  # - Drink water: misses ~10 days (less consistent)
  water_miss_days = {1, 4, 6, 9, 12, 15, 18, 20, 23, 26}
  # - Read book: misses ~7 days
  read_miss_days = {2, 5, 8, 14, 16, 21, 27}

  for i, d in enumerate(days):
    if i not in walk_miss_days:
      db.record_completion(habit_ids["Morning walk"], completed_at=_dt(d, 7, 15))
    if i not in water_miss_days:
      db.record_completion(habit_ids["Drink water"], completed_at=_dt(d, 12, 30))
    if i not in read_miss_days:
      db.record_completion(habit_ids["Read book"], completed_at=_dt(d, 21, 10))

  # Weekly completion patterns:
  # We mark one completion per week. Choose different days to prove weekday doesn't matter.
  # Weeks are based on Monday-start (same as your database helper logic).
  week_starts: list[datetime] = []
  for d in days:
    if d.weekday() == 0:  # Monday
      week_starts.append(d)
  # If start isn't a Monday, still include the first week's Monday by shifting forward.
  if not week_starts:
    first_monday = start + timedelta(days=(7 - start.weekday()) % 7)
    week_starts = [first_monday + timedelta(days=7 * k) for k in range(4)]

  # Ensure we only use 4 week buckets within our 28-day window
  week_starts = week_starts[:4]

  # Weekly review: complete weeks 1, 2, 4 (miss week 3)
  weekly_review_weeks = {0, 1, 3}
  # Call family: complete all 4 weeks
  call_family_weeks = {0, 1, 2, 3}

  for w, monday in enumerate(week_starts):
    if w in weekly_review_weeks:
      # Thursday of that week
      db.record_completion(habit_ids["Weekly review"], completed_at=_dt(monday + timedelta(days=3), 19, 0))
    if w in call_family_weeks:
      # Sunday of that week
      db.record_completion(habit_ids["Call family"], completed_at=_dt(monday + timedelta(days=6), 16, 0))

  print("Seed complete.")
  print(f"Database: {db_path}")
  print("Created habits:")
  for name, hid in habit_ids.items():
    print(f"  - {hid}: {name}")
  print("Tip: run view_database.py or open the CLI to verify.")


def main() -> None:
  parser = argparse.ArgumentParser(description="Seed habits + 4 weeks completion data.")
  parser.add_argument("--db-path", default="data/habits.db", help="SQLite DB path (default: data/habits.db)")
  parser.add_argument("--reset", action="store_true", help="Delete DB file before seeding")
  args = parser.parse_args()

  seed(db_path=args.db_path, reset=args.reset)


if __name__ == "__main__":
  main()