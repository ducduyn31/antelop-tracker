import numpy as np


def euclidean_distance(detection, tracked_object):
    return np.linalg.norm(detection.points - tracked_object.estimate)


def normalize_bbox(detection):
    return np.array(
        [
            [int(detection['xyxy'][0] * 0.01), int(detection['xyxy'][1] * 0.01)],
            [int(detection['xyxy'][2] * 0.01), int(detection['xyxy'][3] * 0.01)]
        ]
    )


class Singleton(type):
    _instance = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instance:
            self._instance[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instance[self]
