import heapq
import uuid
from typing import List, Sequence

import faust
import numpy as np
import redis
from norfair import Detection, Tracker


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


def euclidean_distance(detection, tracked_object):
    return np.linalg.norm(detection.points - tracked_object.estimate)


def tracking_object(objects: Sequence["TrackedObject"]):
    for obj in objects:
        if not obj.live_points.any():
            continue
        print(str(obj.id))


def event_handler(msg):
    try:
        key = msg["data"].decode("utf-8")
        if "orderKey" in key:
            yolo_detection = heapq.heappop(heap_detection)[0]
            source = yolo_detection[1][1]['source']
            detections = yolo_detection[1][1]['detections']
            time_stamp = yolo_detection[1][1]['timestamp']
            for detection in detections:
                yolo_detection = [detection['xyxy'][0], detection['xyxy'][1],
                                  detection['xyxy'][2], detection['xyxy'][3], detection['score']]
                norfair_detection = yolo_detections_to_norfair_detections(yolo_detection=yolo_detection)
                tracking_object(trackers[source].update(norfair_detection))
    except Exception as exp:
        print(exp)


app = faust.App(
    'human_detect_minimal',
    broker='kafka://localhost:19092',
    value_serializer='json',
    key_serializer='raw',
)

max_distance_between_points = 50

topic = app.topic('human_detect_minimal', value_serializer='json')
trackers = {}

heap_detection = []

cache = redis.Redis()
pubsub = cache.pubsub()
pubsub.psubscribe(**{"__keyevent@0__:expired": event_handler})
pubsub.run_in_thread(sleep_time=0.01)


@app.agent(topic)
async def on_tracking(detection_messages: faust.Stream):
    async for detection in detection_messages:
        if detection['source'] not in list(trackers.keys()):
            trackers[detection['source']] = Tracker(
                distance_function=euclidean_distance,
                distance_threshold=max_distance_between_points,
            )
        record = {"order": [detection["order"], detection]}
        di2 = list(record.items())
        heapq.heappush(heap_detection, di2)
        heapq.heapify(heap_detection)
        yolo_id = str(uuid.uuid4())
        cache.set('orderKey_%s' % yolo_id, '', ex=5)
