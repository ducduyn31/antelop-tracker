import asyncio
import heapq
from typing import List, Sequence

import numpy as np
from norfair import Tracker, Detection
from stream.topics import tracking_queue
from utils import normalize_bbox


def yolo_detections_to_norfair_detections(yolo_detections: list) -> List[Detection]:
    norfair_detections: List[Detection] = []
    for yolo_detection in yolo_detections:
        bbox = normalize_bbox(yolo_detection)
        scores = np.array([yolo_detection['score'], yolo_detection['score']])
        norfair_detections.append(Detection(points=bbox, scores=scores))
    return norfair_detections


def tracking_object(loop, detections, source, objects: Sequence["TrackedObject"]):
    asyncio.set_event_loop(loop)
    for obj in objects:
        if not obj.live_points.any():
            continue
        obj_id = obj.id
        obj_bbox = np.array(
            [
                [int(obj.last_detection.points[0][0]), int(obj.last_detection.points[0][1])],
                [int(obj.last_detection.points[1][0]), int(obj.last_detection.points[1][1])]
            ]
        )
        for detection in detections:
            yolo_bbox = normalize_bbox(detection)
            if (yolo_bbox == obj_bbox).all():
                match_id = {
                    "object_id": obj_id,
                    "uuid": detection['id'],
                    "sources": source
                }
                print(match_id)
                loop.run_until_complete(asyncio.wait([tracking_queue.send(value=match_id)]))
                print('done')
                break


def on_human_detect(loop, heap, tracker: Tracker):
    def handle_event(_):
        _, event = heapq.heappop(heap)
        source, order, timestamp = event['source'], event['order'], event['timestamp']
        detections = event['detections']
        norfair_detection = yolo_detections_to_norfair_detections(yolo_detections=detections)
        objects = tracker.update(norfair_detection)
        tracking_object(loop, detections, source, objects)
    return handle_event
