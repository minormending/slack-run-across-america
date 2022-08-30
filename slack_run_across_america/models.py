from dataclasses import dataclass
from typing import Any, Dict, List

from run_across_america import MemberStats


class SerializableModel:
    """Model utilities functions for derived classes."""

    def json(self) -> Dict[str, Any]:
        """Minimal JSON representation of the class attributes.
        Returns:
            A dictionary of all the class attributes with non-null or empty values
                and datetimes serialized.
        """

        serialized: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is None:
                continue
            if isinstance(value, SerializableModel):
                serialized[key] = value.json()
            elif isinstance(value, list):
                values: List[Any] = []
                for sub_value in value:
                    if isinstance(sub_value, SerializableModel):
                        values.append(sub_value.json())
                    else:
                        values.append(sub_value)
                serialized[key] = values
            else:
                serialized[key] = value

        return serialized


@dataclass
class AlertInfo:
    team_name: str
    goal: int
    progress: float

    leaders_overall: List[MemberStats]
    leaders_by_activity: Dict[str, MemberStats]
