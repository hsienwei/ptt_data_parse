# coding=utf8

import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb', aws_access_key_id=' ',
         aws_secret_access_key=' ' , region_name='us-east-1', endpoint_url="http://localhost:8000")

table = dynamodb.Table('ptt')

ID = "test1"
DATE = 2015

response = table.put_item(
   Item={
        'ID': ID,
        'DATE': DATE,
        'info': {
            'plot':"Nothing happens at all."

        }
    }
)

print("PutItem succeeded:")
print(json.dumps(response, indent=4, cls=DecimalEncoder))