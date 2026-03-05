""" Test for the analytics module (Functional Programming) """

from datetime import datetime, timedelta
from habit import Habit
from database import HabitDatabase
import analytics

def test_daily_habit_longest_streak():
    """Test the longest streak calculation for a daily habit"""
    base = datetime(2026, 3, 4, 12, 0, 0)
    events = [
        base,
        base + timedelta(days=1),
        base + timedelta(days=2),
        base + timedelta(days=4),
        base + timedelta(days=5),
    ]

    streak, tied = analytics.calculate_longest_streak_for_habit(events, "daily")
    assert streak == 3
    assert len(tied) == 1

def test_weekly_habit_longest_streak():
    """Test longest streak calculation for a weekly habit"""
    base = datetime(2026, 3, 4, 12, 0, 0)
    events = [
        base,
        base + timedelta(days=7),
        base + timedelta(days=14),
        base + timedelta(days=28),
    ]

    streak, tied = analytics.calculate_longest_streak_for_habit(events, "weekly")
    assert streak == 3
    

