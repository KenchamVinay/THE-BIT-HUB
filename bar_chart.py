import matplotlib.pyplot as plt
import pandas as pd

def generate_bar_chart(df):
    # Grouping the tweets by sentiment and counting the number of tweets for each sentiment
    sentiment_counts = df['Text Sentiment'].value_counts()

    # Plotting the bar chart
    plt.style.use('ggplot')  # Change the style to 'ggplot'
    fig, ax = plt.subplots(figsize=(9, 4.16))
    ax.bar(sentiment_counts.index, sentiment_counts.values, color='purple')
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Count')
    ax.set_title('Sentiment Counts')
    ax.tick_params(axis='x', rotation=0)
    plt.savefig("static/images/bar_chart.png")
    plt.clf()
