import json
import tweepy
from vaderSentiment.vaderSentiment import sentiment
from firebase import firebase
import json
import random

config = json.load(open('.config.json'))
firebase = firebase.FirebaseApplication(config['databaseURL'], None)

def tweet(event, context):
    positweeters = firebase.get('/positweeters', None)
    lucky_ones   = random.sample(positweeters, 3 if len(positweeters) >=3 else len(positweeters))
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": { k: positweeters[k] for k in lucky_ones }
    }
