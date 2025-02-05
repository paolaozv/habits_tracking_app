import pytest
from datetime import datetime, timedelta
from src.habit import Habit
from src.analytics import HabitAnalytics
from src.db_manager import HabitDatabase

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

def test_completion_summary():
  db = HabitDatabase()
  habit1 = Habit("Exercise", "daily")
  habit2 = Habit("Reading", "weekly")
  
  habit1_id = db.save_habit(habit1)
  habit2_id = db.save_habit(habit2)
  
  # Add check-offs for the daily habit (5 out of 10 days)
  today = datetime.now()
  for i in range(5):
    db.save_check_off(habit1_id, today - timedelta(days=i))
  
  # Add check-offs for the weekly habit (2 out of 4 weeks)
  for i in range(2):
    db.save_check_off(habit2_id, today - timedelta(weeks=i))
  
  analytics = HabitAnalytics(db)  # Initialize analytics *after* saving habits
  summary = analytics.get_completion_summary()