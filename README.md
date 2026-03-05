# Habit Tracker
A habit tracking application built with Python, demonstrating object-oriented and functional programming paradigms.

## Features
- Create and manage daily/weekly habits
- Track habit completions with timestamps
- View completion status
- Analytics: calculate longest streaks across habits
- SQLite database for persistent data storage
- Command-Line Interface (CLI)

## Installation
1. **Clone or download this project**
2. **Install pytest** (for running tests):
   pip install pytest
3. No other dependencies required - uses Python standard library

## How to Run
Start the application:
```bash
python cli.py
```

## How to Test
```bash
python -m pytest -v
```

## Project Structure
```
Habit Tracker/
├── habit.py           # Domain model (OOP)
├── database.py        # Persistence layer (Repository pattern)
├── analytics.py       # Analytics module (Functional programming)
├── cli.py             # Command-line interface
├── seed_data.py       # Script to generate 4 weeks of test data
├── data/
│   └── habits.db      # SQLite database
└── tests/
    ├── test_smoke.py      # Basic CRUD tests
    └── test_analytics.py  # Analytics function tests
```

## Technologies/Requirements
- **Python 3.x** (standard library)
- **SQLite** (built-in with Python)
- **pytest** (for testing: `pip install pytest`)
