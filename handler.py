import json
import tweepy
from vaderSentiment.vaderSentiment import sentiment
from firebase import firebase
import random
import numpy as np
import requests
from json import JSONEncoder
from requests_oauthlib import OAuth1


config = json.load(open('.config.json'))
firebase = firebase.FirebaseApplication(config['databaseURL'], None)
auth = tweepy.OAuthHandler(config['consumerKey'], config['consumerSecret'])

default_positweeters = 3
default_tweets = 3

def get_auth():
    global auth
    if auth is None:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    return auth

def apiForPositweeter(positweeter):
    global auth
    auth.set_access_token(positweeter['token'], positweeter['token_secret'])
    api = tweepy.API(auth)
    return api


def saveTweetsToCollection(listOfTweets_IDS):
    auth_collection = OAuth1(config['consumerKey'], config['consumerSecret'],
                             config['masterKey'], config['masterSecret'])
    post_data = []
    for tweet in listOfTweets_IDS:
        post_data.append({"op":"add", "tweet_id":tweet})
    json_data = {"id":config['collectionId'], "changes":post_data}
    r = requests.post('https://api.twitter.com/1.1/collections/entries/curate.json', json=json_data, auth=auth_collection)
    return r

def topNTweets(tweets, n = 100, posThresh = 0.7):
    posScores = np.zeros(len(tweets)+1)
    negScores = np.zeros(len(tweets)+1)
    tweetID = [0]*(len(tweets)+1)
    i = 0
    for t in tweets:
        #if not t.in_reply_to_status_id:
            #continue
        sent = sentiment(t.text.encode("utf-8"))
        if sent['neu'] == 1.0:
            continue
        posScores[i] = sent['pos']/(sent['pos']+sent['neg'])
        tweetID[i] = t.id
        i += 1

    posScores = posScores[posScores>posThresh]
    topNIndices = np.argsort(posScores)[::-1][:n]
    topN = np.array(tweetID)[topNIndices]
    return topN

def generateLists(api):
    keywords = ['#lgbt :)', 'lgbt :)', '#pride :)', 'pride :)', '#trans :)', 'trans :)', '#gay :)', 'gay :)', '#transgender :)', 'transgender :)',
               '#lesbian :)', 'lesbian :)', '#lgbtrights :)', 'lgbtrights :)', '#equalrights :)', 'equal rights :)', '#gaymarriage :)',
                'gay marriage :)', '#comingOut :)', 'coming out :)', '#comingOutDay :)', '#nationalComingOutDay :)', '#lgbtq :)',
                'lgbtq :)']

    IDS = []

    for k in keywords:
        t = api.search(q = k + ' -porn -#porn -nsfw -#nsfw -#nsfl -nsfl -#dick', result_type='recent', lang='en', count=100)
        IDS.extend(topNTweets(t))
        print len(IDS)

    return IDS

def random_positweeters(size=default_positweeters):
    positweeters = firebase.get('/positweeters', None)
    lucky_ones   = random.sample(positweeters,
                                 size if len(positweeters) >= size else len(positweeters))
    return {k: positweeters[k] for k in lucky_ones}

def retweet(positweeter=None, tweet_id=None):
    print "retweeting", tweet_id, " with ", json.dumps(positweeter)
    return apiForPositweeter(positweeter).retweet(tweet_id)

def tweet(event, context):
    lucky_positweeters = random_positweeters()
    print 'random positweeters', lucky_positweeters
    tweet_ids = generateLists(apiForPositweeter(
        lucky_positweeters[lucky_positweeters.keys()[0]]
    ))
    lucky_tweets = random.sample(
        tweet_ids,
        default_tweets if len(tweet_ids) >= default_tweets else len(tweet_ids)
    )
    retweeted = [retweet(lucky_positweeters[p], t) for p, t in zip(lucky_positweeters.keys(), lucky_tweets)]
    saveTweetsToCollection(lucky_tweets)

    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "retweeted": retweeted
    }
