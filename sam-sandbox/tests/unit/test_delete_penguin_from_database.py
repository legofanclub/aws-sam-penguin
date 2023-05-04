import pytest
from app.app import add_penguin_to_database
from app.app import delete_penguin_from_database
import boto3
import os
from dotenv import load_dotenv
load_dotenv()

def test_delete_penguin_from_database_function():
    #setup
    add_penguin_to_database("6969", "red", "john")

    #test
    delete_penguin_from_database("6969")

    #assert
    DB = boto3.resource('dynamodb').Table(os.environ.get("TABLE_NAME"))
    response = DB.get_item(Key={'PK':"6969"})
    try:
        item = response['Item']
        pytest.fail()
    except(KeyError):
        pass