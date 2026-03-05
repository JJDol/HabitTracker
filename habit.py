from datetime import datetime
from typing import Literal, Optional

class Habit:
  """
  Represents a single habit that a user want to track.

  A habit is a task that must be completed periodically (daily or weekly).
  This class stores the habit definition only, not completion history.

  Attributes:
    habit_id (int): Unique identifier
    name (str): Name of the habit
    description (str): Description of the habit
    periodicity (str): "daily" or "weekly"
    created_at (datetime): When the habit was created
  """
  def __init__(
    self, 
    name: str, 
    description: Optional[str],
    periodicity: Literal["daily", "weekly"],
    habit_id: int = None, 
    created_at: datetime = None        
    ):

    #Validate name is not empty
    if not name or not name.strip():
        raise ValueError("Habit name cannot be empty")
    
    #Validate periodicity is valid
    if periodicity not in ["daily", "weekly"]:
        raise ValueError("Periodicity must be 'daily' or 'weekly'")

    self.name = name.strip()
    self.description = description.strip() if description else ""
    self.periodicity = periodicity 
    self.habit_id = habit_id
    self.created_at = created_at if created_at else datetime.now()
    
  def __str__(self) -> str:
    """User-friendly string representation"""
    return f"{self.name} ({self.periodicity})"

  def __repr__(self) -> str:
    """Detailed string for debugging"""
    return(
        f"Habit(id={self.habit_id}, name='{self.name}', "
        f"periodicity='{self.periodicity}', created_at='{self.created_at}')"
    )

  def to_dict(self) -> dict:
    """Convert habit to dictionary for serialization"""
    return {
        "habit_id": self.habit_id,
        "name": self.name,
        "description": self.description,
        "periodicity": self.periodicity,
        "created_at": self.created_at.isoformat() if self.created_at else None
    }

  @classmethod
  def from_dict(cls, data: dict) -> "Habit":
    """Create Habit from dictionary (for loading from database)"""
    created_at = data.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    return cls(
        habit_id=data.get("habit_id"),
        name=data["name"],
        description=data.get("description", ""),
        periodicity=data["periodicity"],
        created_at=created_at
    )


