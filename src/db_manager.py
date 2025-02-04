import sqlite3
from datetime import datetime
from typing import List, Optional
from .habit import Habit

class HabitDatabase:
  def __init__(self, db_path: str = "habits.db"):
    """Initialize database connection and create tables if they don't exist."""
    self.db_path = db_path
    self.conn = sqlite3.connect(db_path)
    self.conn.row_factory = sqlite3.Row
    self._create_tables()

  def _create_tables(self) -> None:
    """Create the necessary database tables if they don't exist."""
    with self.conn:
      self.conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_name TEXT NOT NULL,
          periodicity TEXT NOT NULL,
          creation_date TEXT NOT NULL
        )
      """)
          
      self.conn.execute("""
        CREATE TABLE IF NOT EXISTS check_offs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          habit_id INTEGER NOT NULL,
          check_date TEXT NOT NULL,
          FOREIGN KEY (habit_id) REFERENCES habits (id),
          UNIQUE(habit_id, check_date)
        )
      """)

  def save_habit(self, habit: Habit) -> int:
    """Save a habit to the database and return its ID."""
    with self.conn:
      cursor = self.conn.execute("""
        INSERT INTO habits (task_name, periodicity, creation_date)
        VALUES (?, ?, ?)
      """, (habit.task_name, habit.periodicity, habit.creation_date.isoformat()))
      return cursor.lastrowid

  def load_habit(self, habit_id: int) -> Optional[Habit]:
    """Load a habit and its check-offs from the database."""
    cursor = self.conn.execute("""
      SELECT * FROM habits WHERE id = ?
    """, (habit_id,))
    habit_data = cursor.fetchone()
    
    if not habit_data:
      return None

    # Create habit instance
    habit = Habit(
      task_name=habit_data['task_name'],
      periodicity=habit_data['periodicity'],
      creation_date=datetime.fromisoformat(habit_data['creation_date'])
    )

    # Load check-offs
    cursor = self.conn.execute("""
      SELECT check_date FROM check_offs WHERE habit_id = ?
    """, (habit_id,))
      
    for row in cursor.fetchall():
      habit.check_off_dates.append(datetime.fromisoformat(row['check_date']))

    return habit

  def save_check_off(self, habit_id: int, check_date: datetime) -> None:
    """Save a check-off date for a habit."""
    with self.conn:
      self.conn.execute("""
        INSERT OR IGNORE INTO check_offs (habit_id, check_date)
        VALUES (?, ?)
      """, (habit_id, check_date.isoformat()))

  def get_all_habits(self) -> List[tuple[int, Habit]]:
    """Return all habits with their IDs."""
    cursor = self.conn.execute("SELECT id FROM habits")
    habits = []
    for row in cursor.fetchall():
      habit = self.load_habit(row['id'])
      if habit:
        habits.append((row['id'], habit))
    return habits

  def delete_habit(self, habit_id: int) -> None:
    """Delete a habit and its check-offs from the database."""
    with self.conn:
      self.conn.execute("DELETE FROM check_offs WHERE habit_id = ?", (habit_id,))
      self.conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

  def close(self) -> None:
    """Close the database connection."""
    self.conn.close()