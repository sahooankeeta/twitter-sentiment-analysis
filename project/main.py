from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import matplotlib.pyplot as plt
import requests
import numpy as np
import tweepy
import pyttsx3
from tweepy.auth import OAuthHandler
from textblob import TextBlob
import csv
import os
import re
import matplotlib

matplotlib.use('agg')

from . import db
main = Blueprint('main', __name__)
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/analyze')
@login_required
def analyze():
    return render_template('analyze.html', name=current_user.name)

class SentimentAnalysis:
 
    def __init__(self):
        self.tweets = []
        self.tweetText = []

    def DownloadData(self, keyword, tweets):
        # authenticating
       consumerKey = os.getenv("API_KEY")
       
       consumerSecret = os.getenv("API_KEY_SECRET")
       accessToken = os.getenv("ACCESS_TOKEN")
       accessTokenSecret = os.getenv("ACCESS_TOKEN_SECRET")
       auth = OAuthHandler(consumerKey, consumerSecret)
       auth.set_access_token(accessToken, accessTokenSecret)
       api = tweepy.API(auth)
       
       tweets = int(tweets)
       self.tweets = api.search_tweets(q=keyword, lang="en",count=tweets)
       # Open/create a file to append data to
       csvFile = open('result.csv', 'a')
 
        # Use csv writer
       csvWriter = csv.writer(csvFile)
       
       fear=0
       love=0
       sadness=0
       joy=0
       anger=0
       surprise=0
       for tweet in self.tweets:
           
            # Append to temp so that we can store in csv later. I use encode UTF-8
            self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
            #print(tweet.text)
            r=requests.post('http://127.0.0.1:8000/predict',json={'tweet':tweet.text})
            if r.text=='fear':
              fear+=1
            elif r.text=='love':
              love+=1
            elif r.text=='sadness':
              sadness+=1
            elif r.text=='joy':
              joy+=1
            elif r.text=='anger':
              anger+=1
            elif r.text=='surprise':
              surprise+=1
       csvWriter.writerow(self.tweetText)
       csvFile.close()
 
        # finding average of how people are reacting
       fear = self.percentage(fear, tweets)
       love = self.percentage(love, tweets)
       sadness = self.percentage(sadness, tweets)
       joy = self.percentage(joy, tweets)
       anger = self.percentage(anger, tweets)
       surprise = self.percentage(surprise, tweets)
        # printing out data
       
       self.plotPieChart(fear,love,sadness,joy,anger,surprise, keyword, tweets)
      
       
       
 

    def cleanTweet(self, tweet):
        # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())
 
    # function to calculate percentage
    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')
   
    def plotPieChart(self,fear,love,sadness,joy,anger,surprise, keyword, tweets):
        fig = plt.figure()
        labels = ['Fear [' + str(fear) + '%]', 'Love [' + str(love) + '%]',
                  'Sadness [' + str(sadness) +
                  '%]', 'Joy [' + str(joy) + '%]',
                  'Anger [' + str(anger) +
                  '%]', 'Surprise [' + str(surprise) + '%]']
        sizes = [fear,love,sadness,joy,anger,surprise]
        colors = ['yellowgreen', 'lightgreen', 'darkgreen',
                  'gold', 'red','darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        strFile = r"C:\Users\ANKEETA\Desktop\projects\twitter-sentiment-analysis\project\static\images\plot1.png"
        
        os.remove(strFile)  # Opt.: os.system("rm "+strFile)
        plt.savefig(strFile)
        plt.show()


@main.route('/analyze',methods=['POST'])
def sentiment_logic():
    keyword = request.form.get('keyword')
    tweets = request.form.get('tweets')
    sa = SentimentAnalysis()
    sa.DownloadData(keyword,tweets)
    # set variables which can be used in the jinja supported html page
    #polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1=sa.DownloadData(
     #   keyword, tweets)
    # engine=pyttsx3.init()
    # engine.say("The Average Sentiment is "+htmlpolarity)
    # engine.runAndWait()
  
    # Playing the converted file
    
    #print(polarity,htmlpolarity,positive,wpositive)
    return render_template('analyze.html',showResults=True,keyword=keyword,tweets=tweets)
    #return flask.render_template('sentiment_analyzer.html')
    #return render_template('analyze.html', polarity=polarity, htmlpolarity=htmlpolarity, positive=positive, wpositive=wpositive, spositive=spositive,
                           #negative=negative, wnegative=wnegative, snegative=snegative, neutral=neutral, keyword=keyword1, tweets=tweet1)
 