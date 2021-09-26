import os

from core.faust_app import faust_app as app
from core.pubsub import PubSub
from core.tracking_process import TrackingProcess
from stream.topics import human_detect_minimal_queue

handlers = dict()


@app.agent(human_detect_minimal_queue, concurrency=int(os.getenv('FAUST_CONCURRENCY')))
async def on_human_detected(stream):
    async for events in stream.take(20, within=10):
        for event in events:
            source, order, timestamp = event['source'], event['order'], event['timestamp']
            detections = event['detections']

            if source not in handlers or not handlers[source].is_alive():
                proc = TrackingProcess(source=source)
                handlers[source] = proc
                proc.start()

            if len(detections) > 0:
                handlers[source].add_new_detection(event)
