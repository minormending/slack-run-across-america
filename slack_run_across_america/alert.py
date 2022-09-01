from datetime import datetime, timedelta
import logging
from typing import Dict, List

from run_across_america import RunAcrossAmerica, Team, MemberStats, Goal, Activity

from .models import AlertInfo


class AlertBuilder:
    def __init__(self) -> None:
        self.client: RunAcrossAmerica = RunAcrossAmerica()

    def build(self, team_id: str) -> AlertInfo:
        leaderboard: List[MemberStats] = list(self.client.leaderboard(team_id))
        if not leaderboard:
            logging.error(f"Team {team_id} has no memebers, exiting!")
            return

        # Could not find a team route, this is similar to how the app does it.
        random_user_id: str = leaderboard[0].id
        teams: List[Team] = list(self.client.teams(random_user_id))
        team: Team = next(filter(lambda t: t.id == team_id, teams))

        goal: Goal = self.client.goals(team_id, include_progress=True)

        # get all the activities in the last week
        activities: List[Activity] = list(self.client.feed(team_id))
        last_week: datetime = datetime.today() - timedelta(days=7)
        activities = list(
            filter(lambda a: a.time_completed > last_week, activities)
        )

        # only report on the top 3 members of the team.
        max_users: int = min(len(leaderboard), 3)  # at most 3 users from team
        leaders: List[MemberStats] = leaderboard[:max_users]

        # highlights from the last week, excluding leaders.
        exclude_leaders: List[str] = [i.id for i in leaders]
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
