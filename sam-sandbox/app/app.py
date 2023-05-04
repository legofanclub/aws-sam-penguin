import boto3
import os
import simplejson as json

_DB = None


def handler(event, context):
    event_type = event["requestContext"][
        "eventType"
    ]  # "CONNECT" or "DISCONNECT" or "MESSAGE"
    if event_type == "CONNECT":
        onConnect(event)
    elif event_type == "DISCONNECT":
        onDisconnect(event)
    elif event_type == "MESSAGE":
        onMessage(event)

    return {"statusCode": 200, "body": ""}


def get_app_db():
    global _DB
    if _DB is None:
        _DB = boto3.resource("dynamodb").Table(os.environ.get("TABLE_NAME"))
    return _DB


def broadcast_to_all_clients(message):
    response = get_app_db().scan(TableName=os.environ.get("TABLE_NAME"))
    all_connection_ids = [item.get("PK") for item in response["Items"]]

    for connection_id in all_connection_ids:
        send_message_to_client(message, connection_id)


def send_message_to_client(message, connection_id):
    client = boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{os.environ.get('WEBSOCKET')}.execute-api.{os.environ.get('REGION')}.amazonaws.com/Prod",
    )
    print("sending message: %s to %s" % (message, connection_id))

    try:
        client.post_to_connection(Data=message, ConnectionId=connection_id)
    except Exception as e:
        print(e)
        print(f"sending to client with connection_id: {connection_id} failed")
        delete_penguin_from_database(connection_id)
        broadcast_leaving_message(connection_id)


def onConnect(event):
    name = ""
    color = ""
    add_penguin_to_database(event["requestContext"]["connectionId"], color, name)


def onDisconnect(event):
    delete_penguin_from_database(event["requestContext"]["connectionId"])
    broadcast_leaving_message(event["requestContext"]["connectionId"])


def broadcast_leaving_message(id):
    message = json.dumps({"type": "leaving", "data": id})
    broadcast_to_all_clients(message)


def onMessage(event):
    id = event["requestContext"]["connectionId"]
    try:
        body = json.loads(event["body"])
    except Exception as e:
        send_message_to_client("invalid command: not parsable as json", id)
        return ()

    if "type" not in body:
        send_message_to_client("invalid command: no type property", id)
        send_message_to_client(str(body), id)
        return ()
    # example: {"type": "move", "data": {"position_x": 20, "position_y": 30}}
    elif body["type"] == "move":
        position_x = body["data"]["position_x"]
        position_y = body["data"]["position_y"]
        move_penguin(id, position_x, position_y)
        send_message_to_client("succesfully moved", id)
    # example: {"type": "snowball", "data": {"position_x": 20, "position_y": 30}}
    elif body["type"] == "snowball":
        position_x = body["data"]["position_x"]
        position_y = body["data"]["position_y"]
        throw_snowball(id, position_x, position_y)
        send_message_to_client("succesfully threw snowball", id)
    # example: {"type": "chat", "data": "this is an example chat message"}
    elif body["type"] == "chat":
        text = body["data"]
        chat_from(id, text)
        send_message_to_client("succesfully chatted", id)
    # example: {"type": "get_table_data"}
    elif body["type"] == "get_table_data":
        get_table_data(id)
        send_message_to_client("succesfully got data", id)
    # example: {"type": "join_server", "data": {"name": "example name", "color": "example color"}}
    elif body["type"] == "join_server":
        name = body["data"]["name"]
        color = body["data"]["color"]
        choose_name_and_color(id, name, color)
        set_initial_position(id, 50, 50)
        introduce_new_penguin(id, name, color, 50, 50)
        send_message_to_client("succesfully joined", id)
    elif body["type"] == "get_id":
        # this is lazy, imo client has some other way of telling connection id
        send_message_to_client(json.dumps({"type": "id", "data": id}), id)
    else:
        send_message_to_client("invalid command", id)


def set_initial_position(id, x, y):
    DB = get_app_db()
    DB.update_item(
        Key={"PK": str(id)},
        UpdateExpression="SET position_x = :x, position_y = :y",
        ExpressionAttributeValues={
            ":x": x,
            ":y": y,
        },
    )


def choose_name_and_color(id, n, c):
    DB = get_app_db()
    DB.update_item(
        Key={"PK": str(id)},
        UpdateExpression="SET #n = :n, color = :c",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={
            ":n": n,
            ":c": c,
        },
    )


def introduce_new_penguin(id, n, c, x, y):
    penguin = json.dumps(
        {
            "type": "new_penguin",
            "data": [
                {
                    "PK": id,
                    "name": n,
                    "color": c,
                    "position_x": x,
                    "position_y": y,
                }
            ],
        },
        use_decimal=True,
    )
    broadcast_to_all_clients(penguin)


def get_table_data(id):
    response = get_app_db().scan()
    items = response["Items"]
    send_message_to_client(
        json.dumps({"type": "set_db", "data": items}, use_decimal=True), id
    )


def chat_from(id, text):
    broadcast_to_all_clients(
        json.dumps({"type": "chat", "data": {"id": id, "text": text}}, use_decimal=True)
    )


def throw_snowball(thrower, target_x, target_y):
    broadcast_to_all_clients(
        json.dumps(
            {"type": "snowball", "data": {"id": thrower, "x": target_x, "y": target_y}},
            use_decimal=True,
        )
    )


def add_penguin_to_database(PK, color, name):
    DB = DB = get_app_db()
    DB.put_item(
        Item={
            "PK": PK,
            "color": color,
            "name": name,
            "position_x": 50,
            "position_y": 50,
        }
    )


def delete_penguin_from_database(PK):
    DB = get_app_db()
    DB.delete_item(Key={"PK": str(PK)})


def move_penguin(id, x, y):
    broadcast_to_all_clients(
        json.dumps(
            {"type": "move", "data": {"id": id, "x": x, "y": y}}, use_decimal=True
        )
    )

    DB = get_app_db()
    DB.update_item(
        Key={"PK": str(id)},
        UpdateExpression="SET position_x = :x, position_y = :y",
        ExpressionAttributeValues={
            ":x": x,
            ":y": y,
        },
    )
