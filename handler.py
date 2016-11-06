import json
import tweepy
from vaderSentiment.vaderSentiment import sentiment
from firebase import firebase
import random
import numpy as np

config = json.load(open('.config.json'))
firebase = firebase.FirebaseApplication(config['databaseURL'], None)

def random_positweeters(size=3):
    positweeters = firebase.get('/positweeters', None)
    lucky_ones   = random.sample(positweeters,
                                 size if len(positweeters) >= size else len(positweeters))
    return {k: positweeters[k] for k in lucky_ones}


def tweet(event, context):
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": random_positweeters()
    }
