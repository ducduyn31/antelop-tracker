import heapq
from typing import List

import numpy as np
from norfair import Tracker, Detection


def yolo_detections_to_norfair_detections(yolo_detection: list) -> List[Detection]:
    norfair_detections: List[Detection] = []
    bbox = np.array(
        [
            [yolo_detection[0], yolo_detection[1]],
            [yolo_detection[2], yolo_detection[3]]
        ]
    )
    scores = np.array([yolo_detection[4], yolo_detection[4]])
    norfair_detections.append(Detection(points=bbox, scores=scores))
    return norfair_detections


def on_human_detect(heap, tracker: Tracker):
    def handle_event(_):
        _, event = heapq.heappop(heap)
        source, order, timestamp = event['source'], event['order'], event['timestamp']
        detections = event['detections']
        # TODO: implement this
        tracker.update()

        # TODO: dispatch an event to kafka to sync object id
        #  with subject id by requiring recognize service to sync

    return handle_event
