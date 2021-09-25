from core.faust_app import faust_app as app

human_detect_minimal_queue = app.topic(
    'human_detect_minimal',
    value_serializer='json',
)
