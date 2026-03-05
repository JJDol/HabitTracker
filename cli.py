"""
  CLI layer - Command-Line Interface
  Provides a menu-based interface for users to interact with the habit tracker.
"""

from habit import Habit
from database import HabitDatabase
from datetime import datetime
import analytics

class HabitTrackerCLI:
  """
    CLI for the Habit Tracker application.
    Provides a menu for creating, viewing, and managing habits.
  """

  def __init__(self, db_path: str = "data/habits.db"):
    """
      Initialize CLI with database connection.

      Args:
        db_path: Path to the SQLite database file
    """
    self.db = HabitDatabase(db_path)

  def run(self):
    """Start the main CLI loop."""
    print("\n" + "=" * 60)
    print(" HABIT TRACKER - Build Better Habits")
    print("=" * 60)

    # Main loop
    while True:
      self._display_menu()
      choice = input("\nEnter your choice (1-6): ").strip()

      if choice == "1":
        self._create_habit()
      elif choice == "2":
        self._view_all_habits()
      elif choice == "3":
        self._check_off_habit()
      elif choice == "4":
        self._delete_habit()
      elif choice == "5":
        self._show_analytics()
      elif choice == "6":
        print("\nGoodbye~! Keep building those habits!")
        break
      else:
        print("\nInvalid choice. Please enter 1-6")
    
  def _display_menu(self):
    """Display the main menu"""
    print("\n" + "-"*60)
    print("MAIN MENU")
    print("-"*60)
    print("1. Create a new habit")
    print("2. View all habits")
    print("3. Check off a habit (mark as completed)")
    print("4. Delete a habit")
    print("5. Analytics")
    print("6. Exit")

  def _create_habit(self):
    """Guide user through creating a new habit"""
    print("\n" + "="*60)
    print("CREATE NEW HABIT")
    print("="*60)

    # Get habit name
    name = input("Enter habit name: ").strip()
    if not name:
      print("Error: Habit name cannot be empty.")
      return

    # Get description
    description = input("Enter habit description (optional): ").strip()

    # Get periodicity
    print("\nPeriodicity options:")
    print(" 1. Daily")
    print(" 2. Weekly")
    periodicity_choice = input("Choose periodicity (1 or 2): ").strip()

    if periodicity_choice == "1":
      periodicity = "daily"
    elif periodicity_choice == "2":
      periodicity = "weekly"
    else:
      print("Error: Invalid periodicity choice")
      return
    
    # Create and save habit
    try:
      habit = Habit(name=name, description=description, periodicity=periodicity)
      habit_id = self.db.create_habit(habit)

      print(f"\nSuccess! Habit created with ID: {habit_id}")
      print(f"  Name: {habit.name}")
      print(f"  Periodicity: {habit.periodicity}")
    except ValueError as e:
      print(f"Error creating habit: {e}")
  
  def _view_all_habits(self):
    """Display all tracked habits."""
    print("\n" + "="*60)
    print("ALL HABITS")
    print("="*60)

    # Get all habits from database
    habits = self.db.get_all_habits()

    # Check if any habits exist
    if not habits:
      print("\nNo habits found. Create a new habit to get started")
      return

    # Display each habit with completion status
    for i, habit in enumerate(habits, 1):
      print(f"\n{i}. {habit.name}")
      print(f"  Description: {habit.description or 'No description'}")
      print(f"  Periodicity: {habit.periodicity}")
      print(f"  Created at: {habit.created_at.strftime('%Y-%m-%d')}")
    
      # Show completion status based on periodicity
      if habit.periodicity == "daily":
        is_completed = self.db.is_habit_completed_today(habit.habit_id)
        status = "Completed today" if is_completed else "Not completed today"
      else: 
        is_completed = self.db.is_habit_completed_this_week(habit.habit_id)
        status = "Completed this week" if is_completed else "Not completed this week"

      print(f"  Status: {status}")

  def _check_off_habit(self):
    """Guide user through checking off a habit"""
    print("\n" + "="*60)
    print("CHECK OFF HABIT")
    print("="*60)

    #Step 1: Get all habits
    habits = self.db.get_all_habits()

    if not habits:
      print("\nNo habits found. Create a new habit first")
      return

    #Step 2: Display habits with numbers
    print("\nYour habits:")
    for i, habit in enumerate(habits, 1):
      print(f"  {i}. {habit.name} ({habit.periodicity})")

    #Step 3: Get user choice
    try:
      choice = int(input("\nEnter habit number to check off: ").strip())

      if 1 <= choice <= len(habits):
        habit = habits[choice -1]
    
        #Step 4: Record completion in database
        self.db.record_completion(habit.habit_id)

        print(f"\nChecked off: {habit.name}")
        print(f"  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
      else:
        print("\nError: Invalid habit number")
    except ValueError:
      print("\nError: Please enter a valid number")

  def _delete_habit(self):
    """Guide user through deleting a habit"""
    print("\n" + "="*60)
    print("DELETE HABIT")
    print("="*60)

    # Get all habits
    habits = self.db.get_all_habits()

    if not habits:
      print("\nNo habits found. Create a new habit first")
      return
    
    # Display habits
    print("\nYour habits:")
    for i, habit in enumerate(habits, 1):
      print(f"  {i}. {habit.name} ({habit.periodicity})")

    # Get user choice
    try:
      choice = int(input("\nEnter habit number to delete:").strip())

      if choice == 0:
        print("Cancelled")
        return 
      
      if 1 <= choice <= len(habits):
        habit = habits[choice -1]

        # COnfirm deletion
        confirm = input(f"\n  Delete {habit.name}? All data will be lost (yes/no): ").strip().lower()

        if confirm == "yes":
          self.db.delete_habit(habit.habit_id)
          print(f"\n  Deleted: {habit.name}")
        else:
          print("Cancelled")
      else:
        print("\nError: Invalid habit number")
    except ValueError:
      print("\nError: Please enter a valid number")

  def _show_analytics(self):
    """Display analytics for the user's habits"""
    while True: 
      print("\n" + "="*60)
      print("SHOW ANALYTICS")
      print("="*60)

      print("1. View habits by periodicity")
      print("2. Show my best habit overall")
      print("3. Analyze a specific habit")
      print("4. Back to main menu")
      
      choice = input("\nEnter your choice (1-4): ").strip()
      if choice == "1":
        self._view_habits_by_periodicity()
      elif choice == "2":
        self._show_best_habit_overall()
      elif choice == "3":
        self._analyze_specific_habit()
      elif choice == "4":
        break 
      else:
        print("\nInvalid choice. Please enter 1-4")

  def _view_habits_by_periodicity(self):
    """Display habits by periodicity"""
    print("\n" + "="*60)
    print("HABITS BY PERIODICITY")
    print("="*60)

    choice = input("\nEnter 1 for daily habits, 2 for weekly habits: ").strip()

    # Select periodicity
    if choice == "1":
      periodicity = "daily"
    elif choice == "2":
      periodicity = "weekly"
    else:
      print("\nInvalid choice. Please enter 1 or 2")
      return

    # Get habits filtered by periodicity
    habits = analytics.get_habits_by_periodicity(self.db.get_all_habits(), periodicity)
    
    if not habits:
      print(f"\nNo {periodicity} habits found")
      return

    print(f"YOUR {periodicity.upper()} HABITS:")
    for i, habit in enumerate(habits, 1):
      print(f"\n  NAME: {i}. {habit.name}")
      print(f"  DESCRIPTION: {habit.description or 'No description'}")
      print(f"  CREATED AT: {habit.created_at.strftime('%Y-%m-%d')}")

  def _show_best_habit_overall(self):
    """Display the best habit overall"""
    print("\n" + "="*60)
    print("BEST HABITS OVERALL")
    print("="*60)

    print("1. Best daily habit(s)")
    print("2. Best weekly habit(s)")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
      periodicity = "daily"
      unit = "day(s)"
    elif choice == "2":
      periodicity = "weekly"
      unit = "week(s)"
    else:
      print("\nInvalid choice. Please enter 1 or 2")
      return

    # Get all habits and filter by periodicity
    all_habits = self.db.get_all_habits()
    filtered_habits = analytics.get_habits_by_periodicity(all_habits, periodicity)

    if not filtered_habits:
      print(f"\nNo {periodicity} habits found")
      return
    
    # Get best habit among filtered habits and unpack the result
    best_habits, longest_streak, all_streaks_dates = analytics.calculate_longest_streak_all(filtered_habits, self.db.get_all_completion_data())
    
    # Check if no habits found
    if not best_habits:
      print(f"\nNo completions found for {periodicity} habits")
      return

    # Display results
    print(f"YOUR BEST {periodicity.upper()} HABITs: {longest_streak} {unit}\n")
    
    for i, habit in enumerate(best_habits, 1):
      print(f"{i}. NAME: {habit.name}")
      print(f"DESCRPTION: {habit.description or 'No description'}")

      # Get this habit's streak dates
      habit_streaks = all_streaks_dates[habit.habit_id]

      print(f"ACHIEVED TIMES: {len(habit_streaks)}")    
      for j, streak_dates in enumerate(habit_streaks, 1):
        print(f" {j}. {streak_dates[0].strftime('%b %d (%Y)')} - {streak_dates[-1].strftime('%b %d (%Y)')}")

  def _analyze_specific_habit(self):
    """Analyze a specific habit"""
    print("\n" + "="*60)
    print("ANALYZE SPECIFIC HABIT")
    print("="*60)

    print("1. Analyze a daily habit")
    print("2. Analyze a weekly habit")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
      periodicity = "daily"
      unit = "day(s)"
    elif choice == "2":
      periodicity = "weekly"
      unit = "week(s)"
    else:
      print("\nInvalid choice. Please enter 1 or 2")
      return

    habits = self.db.get_all_habits()
    filtered_habits = analytics.get_habits_by_periodicity(habits, periodicity)

    if not filtered_habits:
      print(f"\nNo {periodicity} habits found. Create a new {periodicity} habit to get started")
      return

    print(f"YOUR {periodicity.upper()} HABITS:")
    for i, habit in enumerate(filtered_habits, 1):
      print(f"\n  {i}. {habit.name} ({habit.description or 'No description'})")
    
    habit_choice = input("\nEnter habit number to analyze: ").strip()
    if not habit_choice.isdigit() or int(habit_choice) < 1 or int(habit_choice) > len(filtered_habits):
      print("\nInvalid habit number. Please enter a valid number")
      return

    habit = filtered_habits[int(habit_choice) -1]
    completion_events = self.db.get_completion_events(habit.habit_id)

    if not completion_events:
      print(f"\nNo completions found for {habit.name}")
      return

    # Calculate longest streak for this habit
    longest_streak, tied_streaks = analytics.calculate_longest_streak_for_habit(completion_events, periodicity)
    
    print(f"\nANALYSIS FOR THE HABIT: {habit.name.upper()} ")
    print(f"LONGEST STREAK: {longest_streak} {unit} (achieved {len(tied_streaks)} time(s))")
    print("STREAK PERIODS: ")
    for i, streak_dates in enumerate(tied_streaks, 1):
      print(f"  {i}. {streak_dates[0].strftime('%b %d (%Y)')} - {streak_dates[-1].strftime('%b %d (%Y)')}")


def main():
  cli = HabitTrackerCLI()
  cli.run()
if __name__ == "__main__":
  main()
