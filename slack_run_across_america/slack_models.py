from dataclasses import dataclass
from typing import List, Optional

from .models import SerializableModel


class SlackBlock(SerializableModel):
    pass


@dataclass
class PlainText(SlackBlock):
    text: str
    type: str = "plain_text"
    emoji: bool = True


@dataclass
class Text(SlackBlock):
    text: str
    type: str = "mrkdwn"

    @classmethod
    def empty(cls) -> "Text":
        return Text(text=" ")


@dataclass
class Header(SlackBlock):
    text: PlainText
    type: str = "header"


@dataclass
class Accessory(SlackBlock):
    image_url: str
    alt_text: str
    type: str = "image"


@dataclass
class Section(SlackBlock):
    accessory: Accessory
    fields: List[Text]
    text: Optional[PlainText] = None
    type: str = "section"
