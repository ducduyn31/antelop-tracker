import os

import faust
from dotenv import load_dotenv

load_dotenv()
faust_app = faust.App(
    'antelope-tracker',
    broker=os.getenv('KAFKA_URI'),
    value_serializer='json',
    producer_max_request_size='5000000',
)
