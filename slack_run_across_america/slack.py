from typing import Any, Dict, Iterator, List, Tuple
from requests import Session, Response

from run_across_america import MemberStats, Activity

from .slack_models import Accessory, Header, Section, Text, PlainText, SlackBlock
from .models import AlertInfo
from .utils import pretty_timedelta


DEFAULT_ICON = "https://st4.depositphotos.com/4329009/19956/v/450/depositphotos_199564354-stock-illustration-creative-vector-illustration-default-avatar.jpg"


class SlackNotification:
    def __init__(self, token: str, channel: str) -> None:
        self.token = token
        self.channel = channel

        self.session = Session()
        self.session.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        self.session.proxies = {"http": "127.0.0.1:8888", "https": "127.0.0.1:8888"}
        self.session.verify = False

    def _build_leaderboard(self, leaders: List[MemberStats]) -> Iterator[SlackBlock]:
        rank_emoji: Dict[int, str] = {1: ":one:", 2: ":two:", 3: ":three:"}

        yield Header(text=PlainText("Top Overall Distance:"))
        for leader in leaders:
            name: str = f"{leader.first_name} {leader.last_name}"
            fields: List[Text] = [
                Text(rank_emoji[leader.rank]),
                Text(f"*{name}*"),
                Text.empty(),
                Text(f"{int(leader.distance)}km"),
            ]
            yield Section(
                accessory=Accessory(
                    image_url=leader.icon or DEFAULT_ICON, alt_text=name
                ),
                fields=fields,
            )

    def _build_activities(
        self, activities: Dict[str, Activity]
    ) -> Iterator[SlackBlock]:
        activity_emoji: Dict[str, str] = {
            "Biking": ":bicyclist:",
            "Walking": ":walking:",
            "Running": ":running:",
        }

        yield Header(text=PlainText("Last Week Recap:"))

        ordered: List[Tuple[str, Activity]] = sorted(
            activities.items(), key=lambda kv: kv[1].distance, reverse=True
        )
        for activity_type, activity in ordered:
            name: str = f"{activity.user_first_name} {activity.user_last_name}"
            emoji: str = activity_emoji[activity_type]
            fields: List[Text] = [
                Text(f"{emoji} {activity_type}"),
                Text(f"*{name}*"),
                Text.empty(),
                Text(f"{int(activity.distance)}km"),
                Text.empty(),
                Text(pretty_timedelta(activity.duration)),
            ]
            yield Section(
                accessory=Accessory(
                    image_url=activity.user_icon or DEFAULT_ICON, alt_text=name
                ),
                fields=fields,
            )

    def send_alert(self, info: AlertInfo) -> Dict[str, Any]:
        pct: int = int(100.0 * (info.progress / info.goal))
        msg: str = f"{info.team_name} is at {pct}% of it's goal to {info.goal}km!"

        slack_blocks: List[SlackBlock] = [
            Header(PlainText(msg)),
        ]
        slack_blocks.extend(self._build_leaderboard(info.leaders_overall))
        slack_blocks.extend(self._build_activities(info.leaders_by_activity))

        blocks: Dict[str, Any] = [b.json() for b in slack_blocks]
        message = {"channel": self.channel, "blocks": blocks}
        print(message)

        url: str = "https://slack.com/api/chat.postMessage"
        resp: Response = self.session.post(url, json=message)
        return resp.json
