import logging
import os

from core.faust_app import faust_app as app
from core.tracking_process import TrackingProcess
from stream.topics import human_detect_full_queue, recognized_queue

handlers = dict()


@app.agent(human_detect_full_queue, concurrency=int(os.getenv('FAUST_CONCURRENCY')))
async def on_human_detected(stream):
    try:
        async for event in stream:
            if event is None:
                continue
            source, order, timestamp = event['source'], event['frame_order'], event['timestamp']
            detections = event['detections']

            if source not in handlers or not handlers[source].is_alive():
                proc = TrackingProcess(source=source, redis_uri=os.getenv('REDIS_URI'))
                handlers[source] = proc
                proc.start()

            if len(detections) > 0:
                logging.info(f'received {order} from {source}')
                handlers[source].add_new_detection(event)
    except Exception as e:
        logging.error(e)


@app.agent(recognized_queue, concurrency=int(os.getenv('FAUST_CONCURRENCY')))
async def on_subject_recognize(stream):
    async for event in stream:
        tracking_id, subject_id = event['tracking_id'], event['subject_id']
        source, timestamp = event['source'], event['timestamp']
        # TODO: implement this by update object id with subject id in redis
