import click
from datetime import datetime, timedelta
from typing import Optional
from .db_manager import HabitDatabase
from .habit import Habit
from .analytics import HabitAnalytics

db = HabitDatabase()

@click.group()
def cli():
  """Habit Tracker - Track and manage your daily, weekly, and monthly habits."""
pass

@cli.command()
@click.argument('task_name')
@click.option('--periodicity', '-p', type=click.Choice(['daily', 'weekly', 'monthly'], case_sensitive=False), required=True)
def create(task_name: str, periodicity: str):
  """Create a new habit to track."""
  try:
    habit = Habit(task_name, periodicity)
    habit_id = db.save_habit(habit)
    click.echo(f"Created habit '{task_name}' with ID: {habit_id}")
  except ValueError as e:
    click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('habit_id', type=int)
@click.option('--date', '-d', type=click.DateTime(), default=None,
              help='Date of completion (default: now)')
def check(habit_id: int, date: Optional[datetime]):
  """Mark a habit as completed for today or a specific date."""
  habit = db.load_habit(habit_id)
  if not habit:
    click.echo(f"Error: Habit with ID {habit_id} not found", err=True)
    return

  try:
    check_date = date or datetime.now()
    habit.check_off(check_date)
    db.save_check_off(habit_id, check_date)
    click.echo(f"Checked off '{habit.task_name}' for {check_date.date()}")
  except Exception as e:
    click.echo(f"Error: {e}", err=True)

@cli.command()
def list():
  """List all habits and their current streaks."""
  habits = db.get_all_habits()
  if not habits:
    click.echo("No habits found")
    return

  click.echo("\nYour Habits:")
  click.echo("-" * 60)
  click.echo(f"{'ID':4} {'Task':20} {'Periodicity':12} {'Streak':8} {'Completion Rate':15}")
  click.echo("-" * 60)

  for habit_id, habit in habits:
    streak = habit.calculate_streak()
    completion_rate = habit.get_completion_rate()
    click.echo(
      f"{habit_id:<4} {habit.task_name[:20]:<20} {habit.periodicity:<12} "
      f"{streak:<8} {completion_rate:>6.1f}%"
    )

@cli.command()
@click.argument('habit_id', type=int)
def stats(habit_id: int):
  """Show detailed statistics for a specific habit."""
  habit = db.load_habit(habit_id)
  if not habit:
    click.echo(f"Error: Habit with ID {habit_id} not found", err=True)
    return

  click.echo(f"\nStatistics for: {habit.task_name}")
  click.echo("-" * 40)
  click.echo(f"Periodicity: {habit.periodicity}")
  click.echo(f"Created: {habit.creation_date.date()}")
  click.echo(f"Current streak: {habit.calculate_streak()}")
  click.echo(f"Completion rate: {habit.get_completion_rate():.1f}%")
    
  # Show recent check-offs
  if habit.check_off_dates:
    click.echo("\nRecent completions:")
    for date in sorted(habit.check_off_dates, reverse=True)[:5]:
      click.echo(f"  ✓ {date.date()}")

@cli.command()
@click.argument('habit_id', type=int)
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
def delete(habit_id: int, force: bool):
  """Delete a habit and its history."""
  habit = db.load_habit(habit_id)
  if not habit:
    click.echo(f"Error: Habit with ID {habit_id} not found", err=True)
    return

  if not force:
    if not click.confirm(f"Are you sure you want to delete '{habit.task_name}'?"):
      click.echo("Operation cancelled")
      return

  db.delete_habit(habit_id)
  click.echo(f"Deleted habit: {habit.task_name}")

@cli.group()
def analytics():
  """Analytics and statistics commands."""
  pass

@analytics.command()
@click.option('--periodicity', '-p', type=click.Choice(['daily', 'weekly', 'monthly'], case_sensitive=False))
def habits(periodicity: Optional[str]):
  """List habits filtered by periodicity."""
  analytics = HabitAnalytics(db)
  habits = analytics.get_habits_by_periodicity(periodicity)
  
  if not habits:
    click.echo("No habits found")
    return
      
  click.echo(f"\nHabits{f' ({periodicity})' if periodicity else ''}:")
  click.echo("-" * 40)
  for habit_id, habit in habits:
    click.echo(f"{habit_id}: {habit.task_name}")

@analytics.command()
def streaks():
  """Show all habits sorted by current streak."""
  analytics = HabitAnalytics(db)
  streaks = analytics.get_current_streaks()
  
  if not streaks:
    click.echo("No habits found")
    return
      
  click.echo("\nCurrent Streaks:")
  click.echo("-" * 50)
  for habit_id, habit, streak in streaks:
    click.echo(f"{habit_id}: {habit.task_name:20} {streak:3} days")

@analytics.command()
def summary():
  """Show completion rate summary by periodicity."""
  analytics = HabitAnalytics(db)
  summary = analytics.get_completion_summary()
  
  click.echo("\nCompletion Rates:")
  click.echo("-" * 40)
  for periodicity, rate in summary.items():
    click.echo(f"{periodicity.capitalize():8}: {rate:5.1f}%")

@analytics.command()
def longest_streak():
  """Show the habit with the longest streak ever."""
  analytics = HabitAnalytics(db)
  habit_id, habit, streak = analytics.get_longest_streak_habit()
  
  if not habit:
    click.echo("No habits found")
    return
      
  click.echo("\nLongest Streak Ever:")
  click.echo("-" * 40)
  click.echo(f"Habit: {habit.task_name}")
  click.echo(f"Streak: {streak} days")

@cli.command()
@click.option('--force', '-f', is_flag=True, help='Skip confirmation if database exists')
def load_examples(force: bool):
  """Load example habits with 4 weeks of history."""
  if not force and db.get_all_habits():
    if not click.confirm("This will clear existing habits. Continue?"):
      click.echo("Operation cancelled")
      return
  
  try:
    # Clear existing data
    habits = db.get_all_habits()
    for habit_id, _ in habits:
      db.delete_habit(habit_id)
        
    # Create example data
    from .example_data import create_example_data
    habits = create_example_data(db)
    
    click.echo("\nCreated example habits:")
    click.echo("-" * 50)
    for habit_id, habit in habits:
      click.echo(f"ID {habit_id}: {habit.task_name} ({habit.periodicity})")
      click.echo(f"  Current streak: {habit.calculate_streak()}")
      click.echo(f"  Completion rate: {habit.get_completion_rate():.1f}%")
      click.echo()
          
  except Exception as e:
    click.echo(f"Error creating example data: {e}", err=True)

def main():
  try:
    cli()
  finally:
    db.close()

if __name__ == '__main__':
  main() 