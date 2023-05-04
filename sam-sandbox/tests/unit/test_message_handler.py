import json

import pytest

from app import app
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture()
def message_event():
    """Generates a websocket message Event"""
    return {'requestContext': {'routeKey': '$default', 'messageId': 'Dw2gadIGvHcCEiQ=', 'eventType': 'MESSAGE', 'extendedRequestId': 'Dw2gbHkWPHcF0kQ=', 'requestTime': '22/Apr/2023:05:04:15 +0000', 'messageDirection': 'IN', 'stage': 'Prod', 'connectedAt': 1682139831163, 'requestTimeEpoch': 1682139855211, 'identity': {'sourceIp': '206.87.236.185'}, 'requestId': 'Dw2gbHkWPHcF0kQ=', 'domainName': 'fut2pn5a74.execute-api.us-west-2.amazonaws.com', 'connectionId': 'Dw2cqdCivHcCEiQ=', 'apiId': 'fut2pn5a74'}, 'body': '{"position_x": 20, "position_y": 30}', 'isBase64Encoded': False}



def test_message_event(message_event):
    ret = app.handler(message_event, "context object mock")
