import heapq
from core.faust_app import faust_app as app
from core.pubsub import PubSub
from utils import euclidean_distance
from stream.topics import human_detect_minimal_queue as topic
import uuid
from typing import List, Sequence

import faust
import numpy as np
import redis
from norfair import Detection, Tracker


def yolo_detections_to_norfair_detections(yolo_detections: list) -> List[Detection]:
    norfair_detections: List[Detection] = []
    for yolo_detection in yolo_detections:
        bbox = np.array(
            [
                [yolo_detection[0], yolo_detection[1]],
                [yolo_detection[2], yolo_detection[3]]
            ]
        )
        scores = np.array([yolo_detection[4], yolo_detection[4]])
        norfair_detections.append(Detection(points=bbox, scores=scores))
    return norfair_detections


def tracking_object(sid, objects: Sequence["TrackedObject"]):
    r = redis.Redis(db=3)
    for obj in objects:
        if not obj.live_points.any():
            continue
        # r.set(str(obj.id), "ok", ex=os.getenv("TRACKING_DELAY_TIME"))
        r.set(str(obj.id), "ok", 300)
        try:
            temp = s_uuids[str(obj)]
            if sid not in temp:
                temp.append(sid)
                if len(temp) > 200:
                    temp = temp[50:]
                s_uuids[str(obj)] = temp
        except:
            s_uuids[str(obj)] = [sid]
        print(str(obj))


def event_handler(msg):
    try:
        key = msg["data"].decode("utf-8")
        if "orderKey" in key:
            yolo_detections = heapq.heappop(heap_detection)[1]
            print(yolo_detections)
            source = yolo_detections['source']
            detections = yolo_detections['detections']
            sid = yolo_detections['id']
            norfair_detection = yolo_detections_to_norfair_detections(yolo_detections=detections)
            tracking_object(sid, trackers[source].update(norfair_detection))
    except Exception as exp:
        print(exp)


# max_distance_between_points = os.getenv("MAX_DISTANCE_BETWEEN_POINTS")
max_distance_between_points = 50

trackers = {}
s_uuids = {}

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
                distance_threshold=float(max_distance_between_points),
            )
        record = [detection["order"], detection]
        heapq.heappush(heap_detection, record)
        heapq.heapify(heap_detection)
        yolo_id = str(uuid.uuid4())
        cache.set('orderKey_%s' % yolo_id, '', ex=5)
