import asyncio
import heapq
import threading
from multiprocessing import Process, Queue

from norfair import Tracker

from core.pubsub import PubSub
from handlers import on_human_detect
from utils import euclidean_distance


class TrackingProcess(Process):
    def __init__(self, source, distance_threshold=50, redis_uri='localhost:6379'):
        super().__init__()
        self._queue = Queue()
        self._tracker = None
        self._redis_uri = redis_uri
        self._heap = []
        self._source = source
        self._distance_threshold = distance_threshold
        self._pubsub = None
        self._loop = None
        self._last_frame_order = -1

    def add_new_detection(self, detections):
        self._queue.put(detections, block=False)

    def handle_new_detection(self, new_detection):
        order = new_detection['order']
        if order < self._last_frame_order:
            return

        message = (order, new_detection)
        heapq.heappush(self._heap, message)
        self._pubsub.publish_time_event(new_detection['frame_id'], new_detection, 5)
        self._last_frame_order = order

    def setup_pubsub(self):
        if self._pubsub is None:
            self._tracker = Tracker(
                distance_function=euclidean_distance,
                distance_threshold=self._distance_threshold,
            )
            self._pubsub = PubSub(connection_uri=self._redis_uri)
            self._loop = asyncio.get_event_loop()
            self._pubsub.subscribe('expired', on_human_detect(self._loop, heap=self._heap, tracker=self._tracker))


    def run(self) -> None:
        self.setup_pubsub()
        while True:
            new_detection = self._queue.get(block=True)
            self.handle_new_detection(new_detection)
