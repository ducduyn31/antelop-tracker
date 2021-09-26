import heapq
from multiprocessing import Process, Queue

from norfair import Tracker

from core.pubsub import PubSub
from handlers import on_human_detect
from utils import euclidean_distance


class TrackingProcess(Process):
    def __init__(self, source, distance_threshold=50, redis_uri='localhost:6379'):
        super().__init__()
        self._queue = Queue()
        self._tracker = Tracker(
            distance_function=euclidean_distance,
            distance_threshold=distance_threshold,
        )
        self._heap = []
        self._source = source
        self._subscribed = False
        self._pubsub = PubSub(connection_uri=redis_uri)
        self._last_frame_order = -1

    def add_new_detection(self, detections):
        self._queue.put(detections, block=False)

    def handle_new_detection(self, new_detection):
        order = new_detection['order']
        if order < self._last_frame_order:
            return

        message = (order, new_detection)
        heapq.heappush(self._heap, message)
        self._pubsub.publish_time_event(new_detection['cid'], new_detection, 5)

    def start_listening(self):
        if not self._subscribed:
            self._pubsub.subscribe('expired', on_human_detect)

    def run(self) -> None:
        self.start_listening()
        while True:
            new_detection = self._queue.get(block=True)
            self.handle_new_detection(new_detection)
