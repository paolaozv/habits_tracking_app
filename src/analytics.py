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
    # Initialize summary with 0.0 for all periodicities
    summary = {'daily': 0.0, 'weekly': 0.0, 'monthly': 0.0}
    habits = self.db.get_all_habits()
    today = datetime.now()
    
    for habit_id, habit in habits:
        check_offs = self.db.get_check_offs(habit_id)
        
        if habit.periodicity == "daily":
            # Calculate percentage for daily habits (last 10 days)
            total_days = 10
            recent_check_offs = [co for co in check_offs if (today - co) <= timedelta(days=total_days)]
            completion_percentage = round((len(recent_check_offs) / total_days) * 100)
            summary['daily'] = completion_percentage
        elif habit.periodicity == "weekly":
            # Calculate percentage for weekly habits (last 4 weeks)
            total_weeks = 4
            recent_check_offs = [co for co in check_offs if (today - co) <= timedelta(weeks=total_weeks)]
            completion_percentage = (len(recent_check_offs) / total_weeks) * 100
            summary['weekly'] = completion_percentage
        elif habit.periodicity == "monthly":
            # Calculate percentage for monthly habits (last 3 months)
            total_months = 3
            recent_check_offs = [co for co in check_offs if (today - co) <= timedelta(days=total_months * 30)]
            completion_percentage = (len(recent_check_offs) / total_months) * 100
            summary['monthly'] = completion_percentage
    
    return summary

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