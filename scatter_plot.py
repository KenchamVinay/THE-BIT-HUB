import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

def generate_scatter_plot(df):
    subjectivity = []
    polarity = []
    for i in range(len(df)):
        tweet_text = df.iloc[i]['Text']
        if isinstance(tweet_text, str):
            sentiment = TextBlob(tweet_text).sentiment
            subjectivity.append(sentiment.subjectivity)
            polarity.append(sentiment.polarity)

    sns.set(style='darkgrid')
    plt.figure(figsize=(4.16, 4.16))
    plt.scatter(subjectivity, polarity, color='purple')
    plt.xlabel('Subjectivity')
    plt.ylabel('Polarity')
    plt.title('Subjectivity vs Polarity')
    plt.savefig("static/images/subjectivity_polarity_plot.png")
    plt.clf()

