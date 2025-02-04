import pytest
from datetime import datetime, timedelta
from src.db_manager import HabitDatabase
from src.habit import Habit

@pytest.fixture
def db():
	"""Create a temporary database for testing."""
	db = HabitDatabase(":memory:")
	yield db
	db.close()

def test_save_and_load_habit(db):
	# Create and save a habit
	habit = Habit("Exercise", "daily")
	habit_id = db.save_habit(habit)
	
	# Load the habit
	loaded_habit = db.load_habit(habit_id)
	assert loaded_habit is not None
	assert loaded_habit.task_name == "Exercise"
	assert loaded_habit.periodicity == "daily"

def test_save_check_offs(db):
	# Create and save a habit
	habit = Habit("Exercise", "daily")
	habit_id = db.save_habit(habit)
    
	# Add some check-offs
	today = datetime.now()
	for i in range(3):
		check_date = today - timedelta(days=i)
		db.save_check_off(habit_id, check_date)
	
	# Load the habit and verify check-offs
	loaded_habit = db.load_habit(habit_id)
	assert len(loaded_habit.check_off_dates) == 3

def test_get_all_habits(db):
	# Create multiple habits
	habits = [
		Habit("Exercise", "daily"),
		Habit("Read", "weekly"),
		Habit("Meditate", "daily")
	]
	
	for habit in habits:
		db.save_habit(habit)
	
	# Get all habits
	loaded_habits = db.get_all_habits()
	assert len(loaded_habits) == 3

def test_delete_habit(db):
	# Create and save a habit
	habit = Habit("Exercise", "daily")
	habit_id = db.save_habit(habit)
	
	# Add some check-offs
	db.save_check_off(habit_id, datetime.now())
	
	# Delete the habit
	db.delete_habit(habit_id)
	
	# Try to load the deleted habit
	loaded_habit = db.load_habit(habit_id)
	assert loaded_habit is None 