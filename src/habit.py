from datetime import datetime, timedelta
from typing import List, Optional

class Habit:
  def __init__(self, task_name: str, periodicity: str, creation_date: Optional[datetime] = None):
    """
    Initialize a new habit.
    
    Args:
      task_name: The habit task description
      periodicity: Daily/Weekly/Monthly
      creation_date: When the habit was created (defaults to now)
    """
    self.task_name = task_name
    self.periodicity = periodicity.lower()
    self.creation_date = creation_date or datetime.now()
    self.check_off_dates: List[datetime] = []
    
    # Validate periodicity
    valid_periodicities = ['daily', 'weekly', 'monthly']
    if self.periodicity not in valid_periodicities:
      raise ValueError(f"Periodicity must be one of: {valid_periodicities}")

  def check_off(self, date: Optional[datetime] = None) -> None:
    """Mark the habit as completed for a given date."""
    check_date = date or datetime.now()
    if check_date not in self.check_off_dates:
      self.check_off_dates.append(check_date)
      self.check_off_dates.sort()

  def calculate_streak(self) -> int:
    """Calculate the current streak."""
    if not self.check_off_dates:
      return 0

    today = datetime.now()
    sorted_dates = sorted(self.check_off_dates, reverse=True)
    
    # Check if the most recent check-off is within the expected interval
    if self.periodicity == 'daily':
      if today - sorted_dates[0] > timedelta(days=1):
        return 0
    elif self.periodicity == 'weekly':
      if today - sorted_dates[0] > timedelta(days=7):
        return 0
    else:  # monthly
      if today - sorted_dates[0] > timedelta(days=30):
        return 0

    streak = 1
    expected_interval = {
      'daily': timedelta(days=1),
      'weekly': timedelta(days=7),
      'monthly': timedelta(days=30)
    }[self.periodicity]

    # Count consecutive check-offs
    for i in range(len(sorted_dates) - 1):
      if sorted_dates[i] - sorted_dates[i + 1] <= expected_interval:
        streak += 1
      else:
        break

    return streak

  def get_completion_rate(self) -> float:
    """Calculate the completion rate as a percentage."""
    if not self.check_off_dates:
      return 0.0

    total_days = (datetime.now() - self.creation_date).days
    if total_days == 0:
      return 100.0 if self.check_off_dates else 0.0

    expected_completions = 0
    if self.periodicity == 'daily':
      expected_completions = total_days
    elif self.periodicity == 'weekly':
      expected_completions = total_days // 7
    else:  # monthly
      expected_completions = total_days // 30

    if expected_completions == 0:
      return 100.0 if self.check_off_dates else 0.0

    actual_completions = len(self.check_off_dates)
    return (actual_completions / expected_completions) * 100 