"""
Analytics layer - Functional Programming Approach

This layer provides pure functions for analyzing habit tracking data.

Functions:
  get_all_habits: Returns all habits
  get_habits_by_periodicity: Filters habits by daily/weekly
  calculate_longest_streak_for_habit: Finds the best streak ever achieved for a specific habit
  calculate_longest_streak_all: Finds the best streak ever achieved for all habits
  
"""

from datetime import datetime, timedelta
from typing import Dict, List, Literal, Tuple
from habit import Habit

Periodicity = Literal["daily", "weekly"]

# ============================================================================
# 1) Returning a list of all currently tracked habits
# ============================================================================
def get_all_habits(habits: List[Habit]) -> List[Habit]:
  """
  Return a list of all currently tracked habits.

  Pure function wrapper (returns a copy to avoid accidental mutation).
  """
  return list(habits)

# ============================================================================
# 2) Returning a list of all habits with the same periodicity (daily/weekly)
# ============================================================================
def get_habits_by_periodicity(habits: List[Habit], periodicity: Periodicity) -> List[Habit]:
  """
  Filters habits by periodicity and return sorted by name.

  Args:
    habits: list of all Habit objects
    periodicity: "daily" or "weekly"

  Returns:
    Sorted list of habits matching the specified periodicity

  Example:
    daily_habits = get_habits_by_periodicity(all_habits, "daily")
    # returns only daily habits, sorted alphabetically
  """
  filtered = [habit for habit in habits if habit.periodicity.lower() == periodicity.lower()]
  return sorted(filtered, key=lambda habit: habit.name)

# --- helpers (pure functions) ---
def _normalize_events_to_period_starts(
  completion_events: List[datetime],
  periodicity: Periodicity
) -> List[datetime]:
  """
  Convert completion timestamps to unique period-start timestamps.

  - daily: day start (00:00)
  - weekly: week start (Monday 00:00)

  Returns:
    Sorted list (ascending) of unique period starts.
  """
  starts: set[datetime] = set()

  for event in completion_events:
    if periodicity == "daily":
      starts.add(event.replace(hour=0, minute=0, second=0, microsecond=0))
    else:
      week_start = (event - timedelta(days=event.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
      )
      starts.add(week_start)

  return sorted(starts)


def _split_into_consecutive_runs(period_starts: List[datetime], step_days: int) -> List[List[datetime]]:
  """
  Given sorted (ascending) period starts, split into consecutive runs.

  Returns:
    List of runs, each run is a list of period-start datetimes.
  """
  if not period_starts:
    return []

  step = timedelta(days=step_days)
  runs: List[List[datetime]] = []
  current_run: List[datetime] = [period_starts[0]]

  for i in range(1, len(period_starts)):
    if period_starts[i] - period_starts[i - 1] == step:
      current_run.append(period_starts[i])
    else:
      runs.append(current_run)
      current_run = [period_starts[i]]

  runs.append(current_run)
  return runs


# ============================================================================
# 4) Calculating the longest run streak for a given habit
# ============================================================================
def calculate_longest_streak_for_habit(
  completion_events: List[datetime],
  periodicity: Periodicity
) -> Tuple[int, List[List[datetime]]]:
  """
  Calculates the longest streak for a specific habit.
  Pure function that analyzes completion events to find the best streak.
  
  Args:
      completion_events: List of datetime objects when habit was completed
      periodicity: "daily" or "weekly"
  
  Returns:
    Tuple of (streak_length, list_of_all_tied_longest_streaks)
  
  Examples:
    Events: [Feb 1, Feb 2, Feb 3, Feb 5, Feb 6, Feb 7]
    → Returns: (3, [[Feb 1, Feb 2, Feb 3], [Feb 5, Feb 6, Feb 7]])
    → Display: "Longest streak: 3 days"
               "Feb 1-3"
               "Feb 5-7" 
  """
  if not completion_events:
    return (0, [])

  # Normalize to unique day/week starts so weekly streaks don't require same weekday.
  period_starts = _normalize_events_to_period_starts(completion_events, periodicity)
  step_days = 1 if periodicity == "daily" else 7

  runs = _split_into_consecutive_runs(period_starts, step_days=step_days)
  if not runs:
    return (0, [])

  max_len = max(len(run) for run in runs)
  longest_runs = [run for run in runs if len(run) == max_len]
  return (max_len, longest_runs)

# Calculate longest streak across All habits
def calculate_longest_streak_all(
  habits: List[Habit],
  completion_data: Dict[int, List[datetime]]
) -> Tuple[List[Habit], int, Dict[int, List[List[datetime]]]]:
  """
  Finds all habits with the longest streak across all the user's habits.

  Args: 
    habits: list of all Habit objects
    completion_data: dictionary mapping habit_id to list of completion datetimes

  Returns:
    Tuple of (List of habits with longest streak, streak length, dict mapping habit_id to tied streaks)
    Returns ([], 0, {}) if no habits or no completions exist

  Examples:
    habits = [morning_exercise, read_books, meditation]
    completion_data = {
      1: [Feb 1, Feb 2, Feb 3], # 3-day streak
      2: [Feb 1, Feb 3, Feb 5], # 1-day streaks
      3: [Feb 9, Feb 10, Feb 11] # 3-day streak
    }
    → Returns: (
      [morning_exercise, meditation], # List of tied habits
      3,                              # streak length
      {
        1: [[Feb 1, Feb 2, Feb 3]],   # morning_exercise's streaks
        3: [[Feb 9, Feb 10, Feb 11]]  # meditation's streaks
      } 
  """
  
  if not habits or not completion_data:
      return ([], 0, {})
  
  # Track all habits with best streak
  best_habits = []
  best_streak_length = 0
  best_streak_dates = {}
  
  # Check each habit
  for habit in habits:
    # get completion events for this habit
    time_logs = completion_data.get(habit.habit_id, [])

    if not time_logs:
      continue
    
    # Calculate longest streak for this habit
    streak_length, streak_dates_list = calculate_longest_streak_for_habit(time_logs, habit.periodicity)

    if streak_length > best_streak_length:
      # New champion. Clear previoous and add this
      best_habits = [habit]
      best_streak_length = streak_length
      best_streak_dates = {habit.habit_id: streak_dates_list}
    
    elif streak_length == best_streak_length:
      # Tied champion. Add this to the list too.
      best_habits.append(habit)
      best_streak_dates[habit.habit_id] = streak_dates_list
  
  return (best_habits, best_streak_length, best_streak_dates)