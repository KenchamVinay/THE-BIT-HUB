# import snscrape.modules.twitter as sntwitter
# import pandas as pd
# import re
# from textblob import TextBlob
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import seaborn as sns
# import pie_chart
# import bar_chart
# import toptweets

# # Creating list to append tweet data to
# tweets_list = []

# # Check if the tweets_df.csv file exists or not
# try:
#     # If the file exists, read the data from the file
#     tweets_df = pd.read_csv("tweets.csv")
#     print("Data loaded from CSV file")
# except:
#     # If the file does not exist, scrape the data and create the file
#     # Using TwitterSearchScraper to scrape data and append tweets to list
#     for i, tweet in enumerate(sntwitter.TwitterSearchScraper('#bitcoin OR #btc OR #bitcoinprice').get_items()):
#         if i > 10: # to limit the number of tweets fetched
#             break
#         tweets_list.append([tweet.date, tweet.id, tweet.rawContent, tweet.user.username, tweet.user.followersCount, tweet.coordinates])

#     # Creating a dataframe from the tweets list above
#     tweets_df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet ID', 'Text', 'Username', 'User influence', 'Geo or location'])

#     # Save the dataframe to a CSV file
#     tweets_df.to_csv("tweets_df.csv", index=False)
#     print("Data scraped and saved to CSV file")

# # Removing URLs, RTs, and twitter handles
#     def clean_tweet(tweet):
#         # remove # from bitcoin, # from Bitcoin
#         tweet = re.sub("#bitcoin", "bitcoin", tweet)
#         tweet = re.sub("#Bitcoin", "Bitcoin", tweet)
#         tweet = re.sub("#btc", "btc", tweet)
#         tweet = re.sub("#bitcoinprice", "bitcoinprice", tweet)
#         # remove any strings with a #
#         tweet = re.sub("#\S+", "", tweet)

#         # remove the \n string
#         tweet = re.sub("\n", "", tweet)

#         # remove any hyperlinks
#         tweet = re.sub("https?://\S+", "", tweet)

#         return tweet

#     tweets_df['Text'] = tweets_df['Text'].apply(lambda x: clean_tweet(x))

# # Adding Subjectivity and Polarity columns
# subjectivity = []
# polarity = []
# for tweet in tweets_df['Text']:
#     analysis = TextBlob(tweet)
#     polarity.append(analysis.sentiment.polarity)
#     subjectivity.append(analysis.sentiment.subjectivity)

# tweets_df['Subjectivity'] = subjectivity
# tweets_df['Polarity'] = polarity


# def get_text_sentiment(text):
#     sentiment = TextBlob(text).sentiment.polarity
#     if sentiment < 0:
#         return "Negative"
#     elif sentiment == 0:
#         return "Neutral"
#     else:
#         return "Positive"

# tweets_df['Text Sentiment'] = tweets_df['Text'].apply(lambda x: get_text_sentiment(x))

# print(tweets_df.head()) 

# # Saving the cleaned dataframe to a CSV file
# tweets_df.to_csv("tweets_df.csv", index=False)
# print("Cleaned data saved to CSV file")
from google.cloud import language_v1
from langdetect import detect
import pandas as pd
import matplotlib.pyplot as plt

client = language_v1.LanguageServiceClient()

df = pd.read_csv('tweets_data.csv')

def analyze_tone(text):
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT, language='en')
    response = client.analyze_sentiment(request={'document': document})
    return response.document_sentiment.score

def is_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except:
        return False

df = df[df['Text'].apply(is_english)]
df['sentiment'] = df['Text'].apply(lambda x: analyze_tone(x))

emotions = ['anger', 'joy', 'fear', 'sadness', 'disgust']
scores = [df[df['Text'].str.contains(e)]['sentiment'].mean() for e in emotions]
plt.bar(emotions, scores)
plt.xlabel('Emotion')
plt.ylabel('Sentiment Score')
plt.savefig('sentiment_scores.png')
plt.show()






