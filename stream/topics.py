from core.faust_app import faust_app as app

human_detect_full_queue = app.topic(
    'human_detect',
    value_serializer='json'
)

tracking_queue = app.topic(
    'tracking',
    value_serializer='json'
)

recognized_queue = app.topic(
    'recognized',
    value_serializer='json',
)
