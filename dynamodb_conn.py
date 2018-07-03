# coding=utf8

import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import decimal
import csv
import time
import datetime

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
                
            ],
            KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }, 
        )    
    
    def store_to_db(self, name, json_ary ):
        table_name = 'ptt_data'
        meta_table_name = 'ptt_meta_data'

        cur_time = time.time()
        time_str = datetime.datetime.fromtimestamp(cur_time).strftime('%Y%m%d%H%M%S')
        print(time_str)
        # check data table exist, if not exist, create it.
        is_exist = self.check_table_exist(table_name)
        if not is_exist:
            self.create_table(table_name)

        # check meta data table exist, if not exist, create it.
        is_exist = self.check_table_exist(meta_table_name)
        if not is_exist:
            self.create_table(meta_table_name)
        
        # write data
        data_table = self.dynamodb.Table(table_name)
        jsonStr = json.dumps(json_ary, indent=4)

        response = data_table.put_item(
            Item={
                'id': name + '_' + time_str,
                'info': jsonStr
            }
        )

        # write meta data
        meta_data_table = self.dynamodb.Table(meta_table_name)
        response = meta_data_table.put_item(
            Item={
                'id': name,
                'info': time_str
            }
        )


        '''for item in json_ary :
            id = item['cid']
            SCORE = item['score']
            jsonStr = json.dumps(item, indent=4)
            response = table.put_item(
                Item={
                    'id': id,
                    'score': SCORE,
                    'info': jsonStr
                }
            )'''

    def get_data(self, name, top_cnt = 50):
        table = self.dynamodb.Table('ptt_data')
        meta_table = self.dynamodb.Table('ptt_meta_data')
        
        '''
        response = table.query(
            KeyConditionExpression=Key('id'),
            Limit=top_cnt,
            ScanIndexForward=False,
        )
        '''

        response = meta_table.query(
            KeyConditionExpression=Key('id').eq(name),
            Limit=top_cnt,
            ScanIndexForward=False,
        )

        print(response['Items'])

        if len(response['Items']) != 0:
            response = table.query(
                KeyConditionExpression=Key('id').eq(name + '_' + response['Items'][0]['info']),
                Limit=top_cnt,
                ScanIndexForward=False,
            )

        print(response['Items'][0]['info'])

        json_obj = json.loads(response['Items'][0]['info'])  
        sorted_obj = sorted(json_obj, key=lambda x : x['score'], reverse=True)

        for item in sorted_obj:
            print(item['title'] + str(item['score']))

        return sorted_obj[:10]
            
    def __init__(self, file_name):
        print('init')
        self.open(file_name)   