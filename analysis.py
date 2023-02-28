import os
import pandas as pd
import snscrape.modules.twitter as sntwitter
from textblob import TextBlob
from datetime import datetime, timedelta
import re

# Define hashtags to search for
hashtags = ["#bitcoin"]

# Define function to clean tweet text
def clean_tweet_text(tweet_text):
    cleaned_text = re.sub("#bitcoin", "bitcoin", tweet_text)
    cleaned_text = re.sub("#Bitcoin", "Bitcoin", tweet_text)
    # cleaned_text = re.sub("#btc", "btc", tweet_text)
    # cleaned_text = re.sub("#bitcoinprice", "bitcoinprice", tweet_text)
    cleaned_text = re.sub("#\S+", "", tweet_text)
    cleaned_text = re.sub("\n", "", tweet_text)
    cleaned_text = re.sub("https?://\S+", "", tweet_text)
    return cleaned_text

def get_sentiment_label(polarity):
    if polarity > 0:
        return 'Positive'
    elif polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Define file path to save data
csv_file_path = 'tweets_data.csv'

# Check if file exists, if not create one
# Check if file exists, if not create one
if not os.path.isfile(csv_file_path):
    print(f'{csv_file_path} does not exist. Creating new file and scraping data for today.')
    df = pd.DataFrame(columns=["Datetime", "Text", "Username", "likeCount", "retweetCount", "replyCount", "followersCount", "Subjectivity", "Polarity", "Text Sentiment"])
    for hashtag in hashtags:    
        print(f'Scraping data for {hashtag}...')
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{hashtag} since:{datetime.today().strftime("%Y-%m-%d")}').get_items()):
            tweet_datetime = tweet.date.strftime("%Y-%m-%d %H:%M:%S")
            tweet_text = clean_tweet_text(tweet.rawContent)
            tweet_username = tweet.user.username
            likeCount = tweet.likeCount
            retweetCount = tweet.retweetCount
            replyCount = tweet.replyCount
            tweet_user_followers = tweet.user.followersCount
            if likeCount >= 100 or retweetCount >= 100 or tweet_user_followers >= 100 or replyCount >= 100:
                continue
            # Perform sentiment analysis on the tweet text
            tweet_text_blob = TextBlob(tweet_text)
            tweet_subjectivity = tweet_text_blob.sentiment.subjectivity
            tweet_polarity = tweet_text_blob.sentiment.polarity
            if tweet_polarity > 0:
                tweet_sentiment = 'Positive'
            elif tweet_polarity < 0:
                tweet_sentiment = 'Negative'
            else:
                tweet_sentiment = 'Neutral'
            # Add row to dataframe
            row = [tweet_datetime, tweet_text, tweet_username, likeCount, retweetCount, replyCount, tweet_user_followers]
            row += [tweet_subjectivity, tweet_polarity, tweet_sentiment]
            df.loc[len(df)] = row
            print(f'{i+1} tweets collected for {hashtag}.')
    # Remove duplicate tweets and reset index
    # df.drop_duplicates(subset='Tweet ID', inplace=True)
    # df.reset_index(drop=True, inplace=True)
    # Save dataframe to csv file
    df.to_csv(csv_file_path, index=False, columns=["Datetime", "Text", "Username", "likeCount", "retweetCount", "replyCount", "followersCount", "Subjectivity", "Polarity", "Text Sentiment"])
    # Print number of tweets collected, number of unique users, and number of hashtags explored
    tweets_collected = len(df)
    unique_users = len(df['Username'].unique())
    print(f'Tweets collected: {tweets_collected}')
    print(f'Unique users: {unique_users}')
    print(f'Hashtags explored: {len(hashtags)}')
else:
    # Check when the file was last modified
    file_last_modified = datetime.fromtimestamp(os.path.getmtime(csv_file_path))
    now = datetime.now()
    # Check if the file is more than 1 day old
    if (now - file_last_modified) > timedelta(days=1):
        print(f"Data for {hashtags} in file {csv_file_path} is more than 1 day old. Scraping new data for tweets generated today...")
        df = pd.DataFrame(columns=["Datetime", "Text", "Username", "Subjectivity", "Polarity", "Text Sentiment", "likeCount", "retweetCount", "replyCount", "followersCount"])
        tweets_collected = 0
        for hashtag in hashtags:
            unique_users = set()
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{hashtag} since:{now.strftime("%Y-%m-%d")}').get_items()):
                tweet_datetime = tweet.date.strftime("%Y-%m-%d %H:%M:%S")
                tweet_text = clean_tweet_text(tweet.rawContent)
                tweet_username = tweet.user.username
                likeCount = tweet.likeCount
                retweetCount = tweet.retweetCount
                replyCount = tweet.replyCount
                tweet_user_followers = tweet.user.followersCount
                # Perform sentiment analysis on the tweet text
                tweet_text_blob = TextBlob(tweet_text)
                tweet_subjectivity = tweet_text_blob.sentiment.subjectivity
                tweet_polarity = tweet_text_blob.sentiment.polarity
                tweet_sentiment = get_sentiment_label(tweet_polarity)
                row = [tweet_datetime, tweet_text, tweet_username, tweet_subjectivity, tweet_polarity, tweet_sentiment, likeCount, retweetCount, replyCount, tweet_user_followers]
                df.loc[len(df)] = row
                tweets_collected += 1
                unique_users.add(tweet_username)
        print(f"Number of tweets collected: {tweets_collected}")
        print(f"Number of unique users who generated these tweets: {len(unique_users)}")
        
        # Save the data to CSV file
        df.to_csv(csv_file_path, index=False)
        print(f"Data saved to {csv_file_path}")
        
    else:
        print(f"Data for {hashtags} in file {csv_file_path} is less than 1 day old. No need to scrape new data.")
        
        # Load the data from CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Data loaded from {csv_file_path}")
        # Convert the "Datetime" column to a datetime object
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        
    # Check if the data is more than 1 hour old
    now = datetime.now()
    tweets_collected = 0
    unique_users = set()

    if (now - df.iloc[0]["Datetime"]) > timedelta(hours=1):
        print(f"Data for {hashtags} in file {csv_file_path} is more than 1 hour old. Scraping new data for tweets generated since {df.iloc[0]['Datetime']}")
        last_tweet_datetime =  pd.to_datetime(df.iloc[0]["Datetime"])
        for hashtag in hashtags:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{hashtag} since:{last_tweet_datetime.strftime("%Y-%m-%d %H:%M:%S")}').get_items()):
                tweet_datetime = tweet.date.strftime("%Y-%m-%d %H:%M:%S")
                tweet_text = clean_tweet_text(tweet.rawContent)
                tweet_username = tweet.user.username
                likeCount = tweet.likeCount
                retweetCount = tweet.retweetCount
                replyCount = tweet.replyCount
                tweet_user_followers = tweet.user.followersCount
                # Perform sentiment analysis on the tweet text
                tweet_text_blob = TextBlob(tweet_text)
                tweet_subjectivity = tweet_text_blob.sentiment.subjectivity
                tweet_polarity = tweet_text_blob.sentiment.polarity
                tweet_sentiment = get_sentiment_label(tweet_polarity)
                row = [tweet_datetime, tweet_text, tweet_username, tweet_subjectivity, tweet_polarity, tweet_sentiment, likeCount, retweetCount, replyCount, tweet_user_followers]
                df.loc[len(df)] = row
                tweets_collected += 1
                unique_users.add(tweet_username)
        
        # Save the collected tweets to the CSV file
        df.to_csv(csv_file_path, index=False)
        
        # Print number of tweets collected, number of unique users, and file path of the CSV file
        print(f"{tweets_collected} tweets collected for {hashtags} ({len(unique_users)} unique users). Saved to {csv_file_path}")
        
    else:
        print(f"Data for {hashtags} in file {csv_file_path} is less than 1 hour old. No need to scrape new data.")

