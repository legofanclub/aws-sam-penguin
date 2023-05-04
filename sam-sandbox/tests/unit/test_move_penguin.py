from app.app import add_penguin_to_database
from app.app import move_penguin
from app.app import delete_penguin_from_database
import boto3
import os
from dotenv import load_dotenv
load_dotenv()

def test_move_penguin_function():
    #setup
    add_penguin_to_database("6969", "red", "john")

    #run test
    move_penguin("6969", 30, 50)

    #assert
    DB = boto3.resource('dynamodb').Table(os.environ.get("TABLE_NAME"))
    response = DB.get_item(Key={'PK':"6969"})
    item = response['Item']

    expected = {"PK":"6969",
     "color": "red",
     "name": "john",
     "position_x":30,
     "position_y":50}
    
    assert item == expected

    #cleanup
    delete_penguin_from_database("6969")