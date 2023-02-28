import snscrape.modules.twitter as sntwitter
import pandas as pd
from textblob import TextBlob
import datetime
from datetime import timedelta

# def get_top_tweets():
#     # Creating list to append tweet data to
#     tweets_list = []

#     # Get the current time and calculate the time for last 24 hours
#     now = datetime.datetime.now()
#     last_24_hours = now - timedelta(hours=24)
#     last_24_hours = last_24_hours.strftime("%Y-%m-%d")

#     # Using TwitterSearchScraper to scrape data and append tweets to list
#     for i, tweet in enumerate(sntwitter.TwitterSearchScraper('#btc #bitcoinprice #bitcoin since:' + last_24_hours).get_items()):
#         tweets_list.append([tweet.date, tweet.id, tweet.rawContent[:50], tweet.user.username, tweet.user.followersCount])

#     # Creating a dataframe from the tweets list above
#     tweets_df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet ID', 'Text', 'Username', 'User influence'])

#     # Filter the tweets to only include tweets from blue verified users

#     # Calculate the subjectivity and polarity of the tweets
#     tweets_df['Subjectivity'] = tweets_df['Text'].apply(lambda x: TextBlob(x).sentiment.subjectivity)
#     tweets_df['Polarity'] = tweets_df['Text'].apply(lambda x: TextBlob(x).sentiment.polarity)

#     # Get the top 5 positive tweets
#     positive_tweets = tweets_df.nlargest(5, 'Polarity')

#     # Get the top 5 negative tweets
#     negative_tweets = tweets_df.nsmallest(5, 'Polarity')

#     # Concatenate the positive and negative tweets
#     top_tweets = pd.concat([positive_tweets, negative_tweets])

#     # Reset the index of the top_tweets dataframe
#     top_tweets = top_tweets.reset_index(drop=True)

#     # Return the positive and negative tweets
#     return positive_tweets, negative_tweets
def get_top_tweets(df):
    # Get the top 5 positive tweets
    positive_tweets = df.nlargest(5, 'Polarity')
    positive_tweets['Short Text'] = positive_tweets['Text'].apply(lambda x: x[:50])

    # Get the top 5 negative tweets
    negative_tweets = df.nsmallest(5, 'Polarity')
    negative_tweets['Short Text'] = negative_tweets['Text'].apply(lambda x: x[:50])

    # Concatenate the positive and negative tweets
    top_tweets = pd.concat([positive_tweets, negative_tweets])

    # Reset the index of the top_tweets dataframe
    top_tweets = top_tweets.reset_index(drop=True)

    # Return the positive and negative tweets
    return positive_tweets, negative_tweets
    
