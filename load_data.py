from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb', 
    region_name='us-east-1',
    aws_access_key_id = 'AKIAJTNL33WBCK5CFHQA',
    aws_secret_access_key = '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')

table = dynamodb.Table('Movies')

with open("moviedata.json") as json_file:
    movies = json.load(json_file, parse_float = decimal.Decimal)
    for movie in movies:
        year = int(movie['year'])
        title = movie['title']
        info = movie['info']

        print("Adding movie:", year, title)

        table.put_item(
           Item={
               'year': year,
               'title': title,
               'info': info,
            }
        )