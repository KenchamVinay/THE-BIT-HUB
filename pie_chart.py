import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_pie_chart(df):
    sentiment_count = df['Text Sentiment'].value_counts()
    colors = ['red' if sentiment_count.index[i] == 'Negative' else 'yellow' if sentiment_count.index[i] == 'Neutral' else 'green' for i in range(len(sentiment_count))]
    plt.figure(figsize=(4.16, 4.16))
    plt.pie(sentiment_count, labels=sentiment_count.index, colors=colors, startangle=90, autopct='%1.1f%%')
    plt.title("Sentiment Analysis of Tweets about Bitcoin")
    plt.savefig("static/images/pie_chart.png")
    plt.clf()


