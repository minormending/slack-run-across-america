from datetime import timedelta
import logging
from typing import Dict, List

from run_across_america import RunAcrossAmerica, Team, MemberStats, Goal, Activity

from .models import AlertInfo


class AlertBuilder:
    def __init__(self, user_code: str, team_name: str) -> None:
        self.client: RunAcrossAmerica = RunAcrossAmerica(user_code)
        self.team_name = team_name

    def build(self) -> AlertInfo:
        teams: List[Team] = list(self.client.teams())

        team: List[Team] = list(
            filter(lambda t: t.name.lower() == self.team_name.lower(), teams)
        )
        if not team:
            logging.warning(f"Unable to find team `{self.team_name}` for user.")
            return None
        team: Team = team[0]

        goal: Goal = self.client.goals(team.id, include_progress=True)
        leaderboard: List[MemberStats] = list(self.client.leaderboard(team.id))

        activities: List[Activity] = list(self.client.feed(team.id))
        activities = list(
            filter(lambda a: a.time_completed > goal.start_date, activities)
        )

        max_users: int = min(len(leaderboard), 3)  # at most 3 users from team

        exclude_leaders: List[str] = [i.id for i in leaderboard[:max_users]]
        honorable_mentions: Dict[str, Activity] = self._get_activity_leaders(
            activities, exclude_leaders
        )

        return AlertInfo(
            team_name=team.name,
            goal=goal.distance,
            progress=goal.progress,
            leaders_overall=leaderboard[:3],
            leaders_by_activity=honorable_mentions,
        )

    def _normalize_activity_type(self, activity: Activity) -> str:
        if "run" in activity.type:
            return "Running"
        elif "bike" in activity.type:
            return "Biking"
        elif "walk" in activity.type or "hike" in activity.type:
            return "Walking"
        else:
            print(activity.type)
            return "Walking"

    def _get_activity_leaders(
        self, activities: List[Activity], exclude: List[str]
    ) -> Dict[str, Activity]:
        # type => { user_id => [Activity] }
        combined: Dict[str, Dict[str, Activity]] = {}
        for activity in activities:
            if activity.user_id in exclude:
                continue

            activity_type: str = self._normalize_activity_type(activity)

            if activity_type not in combined:
                combined[activity_type] = {}

            if activity.user_id not in combined[activity_type]:
                combined[activity_type][activity.user_id] = Activity(
                    name=activity_type,
                    type=activity_type,
                    distance=0,
                    units="Kilometers",
                    duration=timedelta(seconds=0),
                    time_completed=None,
                    user_id=activity.user_id,
                    user_first_name=activity.user_first_name,
                    user_last_name=activity.user_last_name,
                    user_icon=activity.user_icon,
                )

            distance: float = activity.distance
            if activity.units == "Miles":
                distance = activity.distance * 1.60934

            combined[activity_type][activity.user_id].distance += distance
            combined[activity_type][activity.user_id].duration += activity.duration

        leaders: Dict[str, Activity] = {}
        for activity_type, users in combined.items():
            ordered: List[Activity] = sorted(
                users.values(), key=lambda u: u.distance, reverse=True
            )
            leaders[activity_type] = ordered[0]
        return leaders
