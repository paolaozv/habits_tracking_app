from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .habit import Habit
from .db_manager import HabitDatabase

class HabitAnalytics:
  def __init__(self, db: HabitDatabase):
    self.db = db

  def get_habits_by_periodicity(self, periodicity: Optional[str] = None) -> List[Tuple[int, Habit]]:
    """
    Get all habits filtered by periodicity.
    
    Args:
      periodicity: Optional filter ('daily', 'weekly', 'monthly')
    Returns:
      List of (habit_id, habit) tuples
    """
    habits = self.db.get_all_habits()
    if periodicity:
      return [(id, habit) for id, habit in habits if habit.periodicity == periodicity.lower()]
    return habits

  def get_longest_streak_habit(self) -> Tuple[Optional[int], Optional[Habit], int]:
    """
    Find the habit with the longest streak ever.
    
    Returns:
      Tuple of (habit_id, habit, streak_length)
    """
    habits = self.db.get_all_habits()
    if not habits:
      return None, None, 0

    max_streak = 0
    max_streak_habit_id = None
    max_streak_habit = None

    for habit_id, habit in habits:
      streak = self._calculate_longest_streak(habit)
      if streak > max_streak:
        max_streak = streak
        max_streak_habit_id = habit_id
        max_streak_habit = habit

    return max_streak_habit_id, max_streak_habit, max_streak

  def get_habit_longest_streak(self, habit_id: int) -> int:
    """Calculate the longest streak ever for a specific habit."""
    habit = self.db.load_habit(habit_id)
    if not habit:
      return 0
    return self._calculate_longest_streak(habit)

  def _calculate_longest_streak(self, habit: Habit) -> int:
    """Calculate the longest streak ever for a habit."""
    if not habit.check_off_dates:
      return 0

    check_dates = sorted(habit.check_off_dates)
    longest_streak = 1
    current_streak = 1

    # Define the expected interval based on periodicity
    if habit.periodicity == 'daily':
      expected_interval = timedelta(days=1)
    elif habit.periodicity == 'weekly':
      expected_interval = timedelta(days=7)
    else:  # monthly
      expected_interval = timedelta(days=30)

    for i in range(1, len(check_dates)):
      date_diff = check_dates[i] - check_dates[i-1]
      if date_diff <= expected_interval:
        current_streak += 1
        longest_streak = max(longest_streak, current_streak)
      else:
        current_streak = 1

    return longest_streak

  def get_completion_summary(self) -> Dict[str, float]:
    """
    Calculate completion rates by periodicity.
    
    Returns:
      Dictionary with completion rates for each periodicity
    """
    habits = self.db.get_all_habits()
    summary = {'daily': [], 'weekly': [], 'monthly': []}
    
    for _, habit in habits:
      summary[habit.periodicity].append(habit.get_completion_rate())
    
    # Calculate averages
    return {
      periodicity: sum(rates) / len(rates) if rates else 0.0
      for periodicity, rates in summary.items()
    }

  def get_current_streaks(self) -> List[Tuple[int, Habit, int]]:
    """
    Get all habits with their current streaks, sorted by streak length.
    
    Returns:
        List of (habit_id, habit, current_streak) tuples
    """
    habits = self.db.get_all_habits()
    streak_data = [
      (id, habit, habit.calculate_streak())
      for id, habit in habits
    ]
    return sorted(streak_data, key=lambda x: x[2], reverse=True) 