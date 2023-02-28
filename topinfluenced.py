import pandas as pd
import snscrape.modules.twitter as sntwitter
import datetime
import os

# def get_top_influencers():
#     # Define the usernames to retrieve tweets from
#     usernames = ['aantonop','Bybit_Official', 'APompliano', 'ErikVoorhees', 'VitalikButerin', 'vanOnTech', 'MessariCrypto', 'TheCryptoDog', 'mdudas', 'PaikCapital', 'SushiSwap', 'girlgone_crypto', '100trillionUSD']

#     # Define the hashtags to search for in tweets
#     hashtags = ['#bitcoin', '#btc', '#bitcoinprice', '#crypto', '#cryptocurrency','#digitalcurrency', '#blockchain', '#ico','#thefuture','ethereum','#trading','xrp', '#ltc','eth','usd','ripple','#getcrypto','#exchange', '#currency' ]

#     # Define the time period to search for tweets
#     today = datetime.datetime.now()
#     last_24_hours = today - datetime.timedelta(days=1)

#     # Check if top_influenced.csv file exists, if so load data and return
#     if os.path.isfile('top_influenced.csv'):
#         df = pd.read_csv('top_influenced.csv')
#         return df.to_dict(orient='records')

#     # Create an empty list to store tweets
#     tweets_list = []

#     # Loop through each username and search for tweets with the given hashtags
#     for username in usernames:
#         for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username} since:{last_24_hours.date()}').get_items()):
#             # Check if the tweet contains any of the specified hashtags
#             if any(hashtag in tweet.content.lower() for hashtag in hashtags):
#                 tweets_list.append((username, tweet.content, tweet.likeCount, tweet.user.followersCount, tweet.date))
#             # Stop searching for tweets if we've reached the maximum limit of 100 tweets
#             if i > 100:
#                 break

#     # Convert the list of tweets to a pandas DataFrame
#     tweets_df = pd.DataFrame(tweets_list, columns=['Username', 'Content', 'Number of likes', 'Number of followers', 'Date'])

#     # Aggregate the tweet data by influencer
#     influencer_df = tweets_df.groupby(['Username', 'Number of followers'], as_index=False).agg({'Content': 'count', 'Number of likes': 'sum'})

#     # Calculate additional metrics
#     influencer_df['Like count'] = influencer_df['Number of likes'] / influencer_df['Content']
#     influencer_df = influencer_df.rename(columns={'Content': 'Number of tweets', 'Number of likes': 'Total number of likes'})

#     # Sort the influencers by total number of likes and select the top 5
#     influencer_df = influencer_df.sort_values(by='Total number of likes', ascending=False).head(5)
    
#     influencer_df = influencer_df.reset_index(drop=True)

#     # Save the top influencers' information in a CSV file
#     influencer_df.to_csv('top_influenced.csv', index=False)

#     # Return the top influencers' information as a list of dictionaries
#     return influencer_df.to_dict(orient='records')



def get_top_influencers(df):
    df['Date'] = pd.to_datetime(df['Datetime']).dt.date

    # Aggregate the tweet data by influencer
    influencer_df = df.groupby(['Username', 'followersCount'], as_index=False).agg({'Text': 'count', 'likeCount': 'sum'})

    # Calculate additional metrics
    influencer_df['Like count'] = influencer_df['likeCount'] / influencer_df['Text']
    influencer_df = influencer_df.rename(columns={'Text': 'Number of tweets', 'likeCount': 'Total number of likes'})

    # Sort the influencers by total number of likes and select the top 5
    influencer_df = influencer_df.sort_values(by='Total number of likes', ascending=False).head(5)

    influencer_df = influencer_df.reset_index(drop=True)

    # Return the top influencers' information as a list of dictionaries
    return influencer_df.to_dict(orient='records')


