import pytest
from datetime import datetime, timedelta
from src.habit import Habit

def test_habit_creation():
  habit = Habit("Exercise", "daily")
  assert habit.task_name == "Exercise"
  assert habit.periodicity == "daily"
  assert isinstance(habit.creation_date, datetime)

def test_invalid_periodicity():
  with pytest.raises(ValueError):
    Habit("Exercise", "invalid")

def test_check_off():
  habit = Habit("Exercise", "daily")
  habit.check_off()
  assert len(habit.check_off_dates) == 1

def test_streak_calculation():
  habit = Habit("Exercise", "daily")
  today = datetime.now()
  
  # Add three consecutive days
  for i in range(3):
    habit.check_off(today - timedelta(days=i))
  
  assert habit.calculate_streak() == 3

def test_completion_rate():
  habit = Habit("Exercise", "daily", datetime.now() - timedelta(days=10))
  
  # Check off 5 out of 10 days
  today = datetime.now()
  for i in range(5):
    habit.check_off(today - timedelta(days=i))
  
  assert habit.get_completion_rate() == 50.0 