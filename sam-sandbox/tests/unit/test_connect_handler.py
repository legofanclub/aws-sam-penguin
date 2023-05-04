import json

import pytest

from app import app
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture()
def connect_event():
    """Generates a websocket connect Event"""
    return {
        "headers": {
            "Host": "fut2pn5a74.execute-api.us-west-2.amazonaws.com",
            "Origin": "https://fut2pn5a74.execute-api.us-west-2.amazonaws.com",
            "Sec-WebSocket-Key": "BUndHmSUbY2anMncLCXRVA==",
            "Sec-WebSocket-Version": "13",
            "X-Amzn-Trace-Id": "Root=1-6443669d-6ee81db61abce5396cd2dfa6",
            "X-Forwarded-For": "206.87.236.185",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
        },
        "multiValueHeaders": {
            "Host": ["fut2pn5a74.execute-api.us-west-2.amazonaws.com"],
            "Origin": ["https://fut2pn5a74.execute-api.us-west-2.amazonaws.com"],
            "Sec-WebSocket-Key": ["BUndHmSUbY2anMncLCXRVA=="],
            "Sec-WebSocket-Version": ["13"],
            "X-Amzn-Trace-Id": ["Root=1-6443669d-6ee81db61abce5396cd2dfa6"],
            "X-Forwarded-For": ["206.87.236.185"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
        },
        "requestContext": {
            "routeKey": "$connect",
            "eventType": "CONNECT",
            "extendedRequestId": "Dwz4lGRyvHcF0KQ=",
            "requestTime": "22/Apr/2023:04:46:21 +0000",
            "messageDirection": "IN",
            "stage": "Prod",
            "connectedAt": 1682138781027,
            "requestTimeEpoch": 1682138781029,
            "identity": {"sourceIp": "206.87.236.185"},
            "requestId": "Dwz4lGRyvHcF0KQ=",
            "domainName": "fut2pn5a74.execute-api.us-west-2.amazonaws.com",
            "connectionId": "Dwz4leekPHcCG6Q=",
            "apiId": "fut2pn5a74",
        },
        "isBase64Encoded": False,
    }


def test_connect_event(connect_event):
    ret = app.handler(connect_event, "context object mock")
