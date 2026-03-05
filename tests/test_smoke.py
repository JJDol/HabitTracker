"""Smoke test: verify basic imports work"""

from habit import Habit
from database import HabitDatabase

def test_imports_work():
    """Test that all main modules can be imported without errors"""
    import habit
    import database
    import analytics
    # If we got here without ImportError, test passes
    assert True

def test_create_and_read_habit():
    # Create test database
    db = HabitDatabase("data/test.db")

    # Create a new habit
    habit = Habit(name="Test Habit", description="This is a test habit", periodicity="daily")
    habit_id = db.create_habit(habit)

    # Read 
    loaded = db.get_habit(habit_id)

    # Check it matches
    assert loaded.name == "Test Habit"
    assert loaded.periodicity == "daily"

def test_delete_habit():
    """Test deleting a habit from the database"""
    db = HabitDatabase("data/test.db")

    # Create a habit
    habit = Habit(name="Test habit", description="This is for deletion test", periodicity="daily")
    habit_id = db.create_habit(habit)

    # Verify it exists
    assert db.get_habit(habit_id) is not None

    # Delete it
    result = db.delete_habit(habit_id)
    assert result == True

    # Verify it's gone
    assert db.get_habit(habit_id) is None

