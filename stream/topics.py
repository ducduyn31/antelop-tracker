from typing import Optional

from core.faust_app import faust_app as app
from faust import Record


class HumanDetectionMessage(Record, serializer='pickle'):
    frame_id: str
    frame: bytes
    detections: any
    source: str
    timestamp: int
    frame_order: int
    object_id: Optional[int]


human_detect_full_queue = app.topic(
    'human_detect',
    value_serializer='pickle',
    value_type=HumanDetectionMessage
)

tracking_queue = app.topic(
    'tracking',
    value_serializer='json'
)

recognized_queue = app.topic(
    'recognized',
    value_serializer='json',
)
