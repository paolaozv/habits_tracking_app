# Habits Tracking App

A command-line habit tracking application that helps users build and maintain habits by tracking daily and weekly tasks.

## Features

- Create and manage habits with different periodicities (daily/weekly/monthly)
- Track habit completions with check-offs
- View current streaks and completion rates
- Analyze habit performance with detailed statistics
- SQLite-based persistent storage
- Example data for testing and demonstration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/paolaozv/habits_tracking_app.git
cd habits-tracking-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Load example data to try out the application:
```bash
python -m src.cli load-examples
```

2. List all habits:
```bash
python -m src.cli list
```

3. Check off a habit:
```bash
python -m src.cli check 1  # Replace 1 with habit ID
```

## Usage Guide

### Managing Habits

Create a new habit:
```bash
python -m src.cli create "Morning Exercise" --periodicity daily
```

View habit details:
```bash
python -m src.cli stats 1  # Replace 1 with habit ID
```

Delete a habit:
```bash
python -m src.cli delete 1  # Replace 1 with habit ID
```

### Analytics

View habits by periodicity:
```bash
python -m src.cli analytics habits --periodicity daily
```

Check current streaks:
```bash
python -m src.cli analytics streaks
```

View completion rates:
```bash
python -m src.cli analytics summary
```

Find longest streak:
```bash
python -m src.cli analytics longest-streak
```

## Testing

Run the test suite:
```bash
pytest
```

## Development

### Key Components

1. **Habit Class** (`src/habit.py`)
   - Core habit tracking functionality
   - Streak calculation
   - Completion rate tracking

2. **Database Manager** (`src/db_manager.py`)
   - SQLite database operations
   - Data persistence
   - CRUD operations for habits

3. **Analytics** (`src/analytics.py`)
   - Statistical analysis
   - Performance metrics
   - Habit filtering

4. **CLI Interface** (`src/cli.py`)
   - Command-line interface
   - User interaction
   - Data visualization

### Example Data

The project includes example data with:
- 3 daily habits (Exercise, Reading, Meditation)
- 2 weekly habits (Planning, Meal Prep)
- 4 weeks of realistic check-off history
- Various completion rates (60% - 100%)
