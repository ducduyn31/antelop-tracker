import os

from core.faust_app import faust_app as app
from core.pubsub import PubSub
from core.tracking_process import TrackingProcess
from stream.topics import human_detect_full_queue, recognized_queue

handlers = dict()


@app.agent(human_detect_full_queue, concurrency=int(os.getenv('FAUST_CONCURRENCY')))
async def on_human_detected(stream):
    async for event in stream:
        source, order, timestamp = event.source, event.frame_order, event.timestamp
        detections = event.detections

        if source not in handlers or not handlers[source].is_alive():
            proc = TrackingProcess(source=source, redis_uri=os.getenv('REDIS_URI'))
            handlers[source] = proc
            proc.start()

        if len(detections) > 0:
            handlers[source].add_new_detection(event)


@app.agent(recognized_queue, concurrency=int(os.getenv('FAUST_CONCURRENCY')))
async def on_subject_recognize(stream):
    async for event in stream:
        oid, subject_id = event['oid'], event['subject_id']
        # TODO: implement this by update object id with subject id in redis
