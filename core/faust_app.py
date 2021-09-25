import os

import faust
from dotenv import load_dotenv

load_dotenv()
faust_app = faust.App(
    'antelope',
    broker=os.getenv('KAFKA_URI'),
    value_serializer='json',
)
