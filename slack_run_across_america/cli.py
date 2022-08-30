import argparse
from pprint import pprint
from typing import Any, Dict

from slack_run_across_america import AlertBuilder, AlertInfo, SlackNotification


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a slack alert with leaderboard info from `Run Across America`."
    )
    parser.add_argument(
        "user_code",
        help="User invitation code emailed after sign-up.",
    )
    parser.add_argument(
        "team_name",
        help="Team name, not case sensitive.",
    )
    parser.add_argument(
        "slack_token",
        nargs="?",
        help="Slack bearer token for the Slack app.",
    )
    parser.add_argument(
        "slack_channel",
        nargs="?",
        help="Channel the Slack app should post the alert to.",
    )

    args = parser.parse_args()

    client: AlertBuilder = AlertBuilder(args.user_code, args.team_name)
    alert: AlertInfo = client.build()
    pprint(alert)

    if alert and args.slack_token and args.slack_channel:
        slack: SlackNotification = SlackNotification(
            args.slack_token, args.slack_channel
        )
        resp: Dict[str, Any] = slack.send_alert(alert)
        pprint(resp)


if __name__ == "__main__":
    main()
