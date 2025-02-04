import pytest
from datetime import datetime, timedelta
from src.analytics import HabitAnalytics
from src.db_manager import HabitDatabase
from src.habit import Habit

@pytest.fixture
def db():
  """Create a temporary database for testing."""
  db = HabitDatabase(":memory:")
  yield db
  db.close()

@pytest.fixture
def analytics(db):
  return HabitAnalytics(db)

def test_get_habits_by_periodicity(analytics, db):
  # Create habits with different periodicities
  habits = [
    ("Exercise", "daily"),
    ("Read", "weekly"),
    ("Meditate", "daily"),
  ]
    
  for task, periodicity in habits:
    habit = Habit(task, periodicity)
    db.save_habit(habit)
  
  daily_habits = analytics.get_habits_by_periodicity("daily")
  assert len(daily_habits) == 2
  
  weekly_habits = analytics.get_habits_by_periodicity("weekly")
  assert len(weekly_habits) == 1

def test_longest_streak_calculation(analytics, db):
  # Create a habit with a known streak pattern
  habit = Habit("Exercise", "daily")
  habit_id = db.save_habit(habit)
  
  # Create a streak of 5 days
  today = datetime.now()
  for i in range(5):
    check_date = today - timedelta(days=i)
    db.save_check_off(habit_id, check_date)
  
  # Add another set of 3 days after a gap
  for i in range(3):
    check_date = today - timedelta(days=i+10)
    db.save_check_off(habit_id, check_date)
  
  longest_streak = analytics.get_habit_longest_streak(habit_id)
  assert longest_streak == 5

def test_get_completion_summary(analytics, db):
  # Create habits and add some check-offs
  habit1 = Habit("Exercise", "daily")
  habit2 = Habit("Read", "weekly")
  
  habit1_id = db.save_habit(habit1)
  habit2_id = db.save_habit(habit2)
  
  # Add check-offs for the daily habit (5 out of 10 days)
  today = datetime.now()
  for i in range(5):
    db.save_check_off(habit1_id, today - timedelta(days=i))
  
  # Add check-offs for the weekly habit (2 out of 4 weeks)
  for i in range(2):
    db.save_check_off(habit2_id, today - timedelta(weeks=i))
  
  summary = analytics.get_completion_summary()
  assert 45 <= summary['daily'] <= 55  # Around 50%
  assert 45 <= summary['weekly'] <= 55  # Around 50%
  assert summary['monthly'] == 0.0  # No monthly habits

def test_get_current_streaks(analytics, db):
  # Create two habits with different streaks
  habit1 = Habit("Exercise", "daily")
  habit2 = Habit("Read", "daily")
  
  habit1_id = db.save_habit(habit1)
  habit2_id = db.save_habit(habit2)
  
  # Create a 3-day streak for habit1
  today = datetime.now()
  for i in range(3):
    db.save_check_off(habit1_id, today - timedelta(days=i))
  
  # Create a 2-day streak for habit2
  for i in range(2):
    db.save_check_off(habit2_id, today - timedelta(days=i))
  
  streaks = analytics.get_current_streaks()
  assert len(streaks) == 2
  assert streaks[0][2] == 3  # First habit has longer streak
  assert streaks[1][2] == 2  # Second habit has shorter streak 