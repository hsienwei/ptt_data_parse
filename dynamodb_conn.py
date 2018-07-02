# coding=utf8

import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import decimal
import csv

class AwsDB:
    
        
    def open(self, file_name):

        with open(file_name, 'r') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',')
            print(spamreader)
            for row in spamreader:
                self.access_key_id = row['Access key ID']
                self.secret_access_key = row['Secret access key']
                break
        self.client = boto3.client('dynamodb', aws_access_key_id=self.access_key_id,
             aws_secret_access_key=self.secret_access_key , region_name='us-east-1')
        self.dynamodb = boto3.resource('dynamodb', aws_access_key_id=self.access_key_id,
             aws_secret_access_key=self.secret_access_key , region_name='us-east-1')     
    
    def get_data(self, name, top_cnt = 50):
        table = self.dynamodb.Table('ptt_data_' + name)
        
        '''
        response = table.query(
            KeyConditionExpression=Key('id'),
            Limit=top_cnt,
            ScanIndexForward=False,
        )
        '''
        
        response = table.scan(
            #KeyConditionExpression=Key('id').eq(100),
            FilterExpression=Attr('score').gt(20),
            #Limit=top_cnt,
        )
        

        for i in response['Items']:
            item_obj = json.loads(i['info']) 
            print(item_obj['title'] + str(i['score']))

    def check_table_exist(self, table_name):
        return table_name in self.client.list_tables()['TableNames']        

    def create_table(self, table_name):
        self.client.create_table(
            TableName = table_name, 
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'score',
                    'AttributeType': 'N'
                },
            ],
            KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'score',
                'KeyType': 'RANGE'
            }],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }, 
        )    
    
    def store_to_db(self, name, json_ary ):
        target_table_name = 'ptt_data_' + name
        is_exist = self.check_table_exist(target_table_name)
        
        if not is_exist:
            self.create_table(target_table_name)

        is_exist = self.check_table_exist(target_table_name)  
        print(is_exist)

        table = self.dynamodb.Table(target_table_name)
        print(table)
        print(json_ary)
        for item in json_ary :
            id = item['cid']
            SCORE = item['score']
            jsonStr = json.dumps(item, indent=4)
            response = table.put_item(
                Item={
                    'id': id,
                    'score': SCORE,
                    'info': jsonStr
                }
            )
            
    def __init__(self, file_name):
        print('init')
        self.open(file_name)   