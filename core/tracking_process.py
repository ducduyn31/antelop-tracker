import heapq
from multiprocessing import Process, Queue

from norfair import Tracker

from utils import euclidean_distance


class TrackingProcess(Process):
    def __init__(self, source, distance_threshold=50):
        super().__init__()
        self._queue = Queue()
        self._tracker = Tracker(
            distance_function=euclidean_distance,
            distance_threshold=distance_threshold,
        )
        self._heap = []
        self._source = source

    def add_new_detection(self, detections):
        pass

    def handle_new_detection(self, new_detection):
        heapq.heappush(self._heap, )

    def run(self) -> None:
        while True:
            new_detection = self._queue.get(block=True)
