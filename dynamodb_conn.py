# coding=utf8

import boto3
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

        self.dynamodb = boto3.resource('dynamodb', aws_access_key_id=self.access_key_id,
             aws_secret_access_key=self.secret_access_key , region_name='us-east-1')     
             
    def store_to_db(self, name, json_ary ):
        table = self.dynamodb.Table('ptt_data')
        
        for item in json_ary :
            SCORE = item['score']
            jsonStr = json.dumps(item, indent=4)
            response = table.put_item(
                Item={
                    'board': name,
                    'score': SCORE,
                    'info': jsonStr
                }
            )
            
    def __init__(self, file_name):
        print('init')
        self.open(file_name)   