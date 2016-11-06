import json
import tweepy
from vaderSentiment.vaderSentiment import sentiment

def tweet(event, context):
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
