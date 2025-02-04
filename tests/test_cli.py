from click.testing import CliRunner
from datetime import datetime
import pytest
from src.cli import cli
from src.db_manager import HabitDatabase

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def test_db():
    db = HabitDatabase(":memory:")
    yield db
    db.close()

def test_create_habit(runner):
    result = runner.invoke(cli, ['create', 'Exercise', '-p', 'daily'])
    assert result.exit_code == 0
    assert 'Created habit' in result.output

def test_create_habit_invalid_periodicity(runner):
    result = runner.invoke(cli, ['create', 'Exercise', '-p', 'invalid'])
    assert result.exit_code == 2
    assert 'Invalid value' in result.output

def test_check_habit(runner):
    # First create a habit
    result = runner.invoke(cli, ['create', 'Exercise', '-p', 'daily'])
    assert result.exit_code == 0
    
    # Extract habit ID from creation output
    habit_id = int(result.output.split('ID: ')[1])
    
    # Check off the habit
    result = runner.invoke(cli, ['check', str(habit_id)])
    assert result.exit_code == 0
    assert 'Checked off' in result.output

def test_list_habits(runner):
    # Create some habits
    runner.invoke(cli, ['create', 'Exercise', '-p', 'daily'])
    runner.invoke(cli, ['create', 'Read', '-p', 'weekly'])
    
    # List habits
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'Exercise' in result.output
    assert 'Read' in result.output

def test_delete_habit(runner):
    # First create a habit
    result = runner.invoke(cli, ['create', 'Exercise', '-p', 'daily'])
    habit_id = int(result.output.split('ID: ')[1])
    
    # Delete with force flag
    result = runner.invoke(cli, ['delete', str(habit_id), '-f'])
    assert result.exit_code == 0
    assert 'Deleted habit' in result.output 