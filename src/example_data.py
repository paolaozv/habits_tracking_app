from datetime import datetime, timedelta
from typing import List, Tuple
from .db_manager import HabitDatabase
from .habit import Habit

def create_example_data(db: HabitDatabase) -> List[Tuple[int, Habit]]:
  """
  Create example habits with 4 weeks of check-off history.
  Returns list of (habit_id, habit) tuples.
  """
  # Define example habits
  habits_data = [
    ("Morning Exercise", "daily", 0.8),  # 80% completion rate
    ("Read 30 mins", "daily", 0.6),      # 60% completion rate
    ("Weekly Planning", "weekly", 1.0),   # 100% completion rate
    ("Meditate", "daily", 0.9),          # 90% completion rate
    ("Weekend Meal Prep", "weekly", 0.75) # 75% completion rate
  ]

  # Calculate date range for check-offs
  today = datetime.now()
  four_weeks_ago = today - timedelta(weeks=4)
  habits = []

  for task_name, periodicity, completion_rate in habits_data:
    # Create and save habit
    habit = Habit(task_name, periodicity, four_weeks_ago)
    habit_id = db.save_habit(habit)
    
    if periodicity == "daily":
      # Calculate total days in the period
      total_days = (today - four_weeks_ago).days
      # Calculate number of check-offs based on completion rate
      num_check_offs = int(total_days * completion_rate)
      
      # Generate random check-off dates
      possible_dates = [
        four_weeks_ago + timedelta(days=i)
        for i in range(total_days)
      ]
      # Select dates based on completion rate
      check_dates = sorted(possible_dates[:num_check_offs])
      
      # Save check-offs
      for check_date in check_dates:
        if check_date <= today:
          db.save_check_off(habit_id, check_date)
          habit.check_off(check_date)
    else:  # weekly habits
      # For 4 weeks with given completion rate
      num_weeks = 4
      num_check_offs = int(num_weeks * completion_rate)
      
      # Generate weekly check-offs
      for week in range(num_check_offs):
        check_date = four_weeks_ago + timedelta(weeks=week)
        if check_date <= today:
          db.save_check_off(habit_id, check_date)
          habit.check_off(check_date)
    
    habits.append((habit_id, habit))

  return habits

def main():
  """Create a new database with example data."""
  db = HabitDatabase("example_habits.db")
  try:
    habits = create_example_data(db)
    print("\nCreated example habits:")
    print("-" * 50)
    for habit_id, habit in habits:
      print(f"ID {habit_id}: {habit.task_name} ({habit.periodicity})")
      print(f"  Current streak: {habit.calculate_streak()}")
      print(f"  Completion rate: {habit.get_completion_rate():.1f}%")
      print()
  finally:
    db.close()

if __name__ == "__main__":
    main() 