"""
Persistence layer - Database management (repository pattern)

This module handles all data persistence using SQLite with event-based tracking.
It follows the repository pattern to separate persistence concerns from domain logic.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pathlib import Path

from habit import Habit

class HabitDatabase:
  def __init__(self, db_path: str = "data/habits.db"):
    """
      Initialize databse connection and create schema if needed.
      Args:
        db_path: Path to the SQLite database file (default: "data/habits.db")
    """
    self.db_path = db_path

    # Create data directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # Initialize database schema (create tables)
    self._init_database()

  def _init_database(self) -> None:
    """
      Create database tables if they don't exist.

      Creates two tables:
      1. habits - stores habit definitions
      2. completion_events - logs each completion with timestamp
    """

    #Get database connection
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    #Create habits table
    cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS habits (
          habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          description TEXT,
          periodicity TEXT NOT NULL CHECK(periodicity IN ('daily', 'weekly')),
          created_at TEXT NOT NULL
        )
      """
    )

    # Create completion_events table
    cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS completion_events (
          event_id INTEGER PRIMARY KEY AUTOINCREMENT,
          habit_id INTEGER NOT NULL,
          completed_at TEXT NOT NULL,
          FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE
          )
      """
    )

    # Create index for faster queries
    cursor.execute(
      """
        CREATE INDEX IF NOT EXISTS idx_completion_events_habit_id
        ON completion_events(habit_id)
      """
    )

    conn.commit() # Save the changes
    conn.close()  # Close the connection

  def _get_connection(self) -> sqlite3.Connection:
    """
      Create and return a database connection.

      Returns:
        SQLite connection object with row factory enabled
    """
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

  def _row_to_habit(self, row: sqlite3.Row) -> Habit:
    """
      Convert a database row to a Habit instance.

      Args:
        row: SQLite row object from query

      Returns:
        Habit instance created rom row data
    """
    return Habit(
      habit_id=row["habit_id"],
      name=row["name"],
      description=row["description"],
      periodicity=row["periodicity"],
      created_at=datetime.fromisoformat(row["created_at"])
    )

  def create_habit(self, habit: Habit) -> int:
    """ 
      Save a new habit to the database.

      Args:
        habit: Habit instance to save

      Returns:
        The habit_id assigned by the database
    """
    conn = self._get_connection()
    cursor = conn.cursor()
    cursor.execute(
      """
        INSERT INTO habits (name, description, periodicity, created_at)
        VALUES (?, ?, ?, ?)
      """,  (
        habit.name, 
        habit.description,
        habit.periodicity,
        habit.created_at.isoformat()
      )
    )

    habit_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return habit_id
  
  def get_habit(self, habit_id: int) -> Optional[Habit]:
    """
      Retrieve a habit by its ID.

      Args:
        habit_id: The unique identifier of the habit

      Returns:
        Habit instance if found, None otherwise
    """
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
        SELECT habit_id, name, description, periodicity, created_at
        FROM habits
        WHERE habit_id = ?
      """, (habit_id,))

    row = cursor.fetchone()
    conn.close()
    if row:
      return self._row_to_habit(row)
    return None

  def get_all_habits(self) -> List[Habit]:
    """
      Retrieve all habits from the database.

      Returns:
        List of all Habit instances
    """
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
        SELECT habit_id, name, description, periodicity, created_at
        FROM habits
        ORDER BY created_at DESC
      """)
    rows = cursor.fetchall()
    conn.close()
  
    return [self._row_to_habit(row) for row in rows]

  def record_completion(self, habit_id: int, completed_at: datetime = None):
    """
      Record a habit completion event.

      This appends a new timestamp to the completion log.

      Args:
        habit_id: The habit that was completed
        completed_at: When the habit was completed (defaults to now)

      Returns:
        The event_id of the recorded completion

      Raises:
        ValueError: If habit_id doesn't exist
    """
    # Verify habit exists
    if not self.get_habit(habit_id):
      raise ValueError(f"Habit with id {habit_id} does not exist")

    # If no time provided, use now
    if completed_at is None:
      completed_at = datetime.now()

    # Save to database
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
        INSERT INTO completion_events (habit_id, completed_at)
        VALUES (?, ?)
      """, 
      (habit_id, completed_at.isoformat())
    )

    # Get the event_id
    event_id = cursor.lastrowid

    # Save and Close
    conn.commit()
    conn.close()
    
    return event_id

  def get_completion_events(self, habit_id: int) -> List[datetime]:
    """
      Get all completion events for a specific habit

      args:
        habit_id: the habit to get events for

      returns: 
        list of datetime objects when the habit was completed
        sorted from most recent to oldest
    """
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      SELECT completed_at
      FROM completion_events
      WHERE habit_id = ?
      ORDER BY completed_at DESC
      """,
      (habit_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    #Convert ISO strings to datetime objects
    return [datetime.fromisoformat(row["completed_at"]) for row in rows]

  def is_habit_completed_today(self, habit_id: int) -> bool:
    """
    Check if a habit was completed today (for daily habits)

    Args:
      habit_id: the habit to check

    Returns:
      true if completed today, false otherwise
    """
    events = self.get_completion_events(habit_id)

    if not events:
      return False

    # Get today's date 
    today = datetime.now().date()

    # Check if most recent event was today
    most_recent_event = events[0]
    return most_recent_event.date() == today

  def is_habit_completed_this_week(self, habit_id: int) -> bool:
    """
    Check if a habit was completed this week (for weekly habits)

    Args: 
      habit_id: the habit to check
    Returns:
      True if completed this week, False otherwise
    """
    events = self.get_completion_events(habit_id)

    if not events:
      return False

    # Get start of this week (Monday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # check if any event is from this week
    return any(event >= start_of_week for event in events)
  
  def delete_habit(self, habit_id: int) -> bool:
    """
    Delete a habit and all its completion events.

    Args:
      habit_id: the habit to delete
    Returns:
      True if deleted successfully, False if habit not found
    """

    # Check if habit exists
    if not self.get_habit(habit_id):
      return False
    
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      DELETE FROM habits
      WHERE habit_id = ?
      """,
      (habit_id,)
    )

    conn.commit()
    conn.close()

    return True

  def get_all_completion_data(self) -> Dict[int, List[datetime]]:
    """
    Get all completion events grouped by habit_id.

    Returns:
      Dictionary mapping habit_id to list of completion datetimes
    """
    conn = self._get_connection()
    cursor = conn.cursor()

    cursor.execute(
      """
      SELECT habit_id, completed_at
      FROM completion_events
      ORDER BY habit_id, completed_at
      """
    )

    rows = cursor.fetchall()
    conn.close()

    # Group by habit_id
    completion_data = {}
    for row in rows:
      habit_id = row["habit_id"]
      completed_at = datetime.fromisoformat(row["completed_at"])

      if habit_id not in completion_data:
        completion_data[habit_id] = []

      completion_data[habit_id].append(completed_at)
  
    return completion_data

    