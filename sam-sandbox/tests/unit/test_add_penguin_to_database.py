import pytest
from app.app import add_penguin_to_database
import boto3
import os

from dotenv import load_dotenv
load_dotenv()

def test_add_penguin_to_database():
    response = add_penguin_to_database("6969", "red", "john")

    #check that penguin has been added
    DB = boto3.resource('dynamodb').Table(os.environ.get("TABLE_NAME"))
    response = DB.get_item(Key={'PK':"6969"})
    item = response['Item']

    expected = {"PK":"6969",
     "color": "red",
     "name": "john",
     "position_x":0,
     "position_y":0}
    
    assert item == expected

    #delete penguin
    DB.delete_item(Key={'PK':"6969"})

    #check that penguin has been deleted
    response = DB.get_item(Key={'PK':"6969"})
    try:
        item = response['Item']
        pytest.fail()
    except(KeyError):
        pass