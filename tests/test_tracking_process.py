import os
import platform
import random
from multiprocessing import Process, Queue


class DemoProcess(Process):
    def __init__(self):
        super().__init__()
        self.name = str(random.randint(10, 100))
        self._queue = Queue()

    def send_message(self):
        self._queue.put(1, block=False)

    def get_cpu_id(self):
        if platform.system() == 'Linux':
            # return os.popen('cat /proc/cpuinfo').read().strip()
            return os.getpid()
        raise NotImplementedError

    def handle_message(self, message):
        print(self.name, ': ', self.get_cpu_id())

    def run(self) -> None:
        while True:
            msg = self._queue.get()
            print(self.name, ': Received Message')
            self.handle_message(message=msg)


if __name__ == '__main__':
    source_map = dict()

    for k in range(10):
        i = random.randint(0, 10)

        if i not in source_map:
            p = DemoProcess()
            source_map[i] = p
            p.start()

    for _ in range(300):
        i = random.randint(0, 10)
        if i in source_map:
            source_map[i].send_message()

    for p in source_map.values():
        p.terminate()
        p.join(timeout=1)
