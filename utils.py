def euclidean_distance():
    # TODO: Implement this for multi direction travel
    pass


class Singleton(type):
    _instance = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instance:
            self._instance[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instance[self]
