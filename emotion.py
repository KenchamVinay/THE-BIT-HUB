import pandas as pd
import text2emotion as te
import matplotlib.pyplot as plt

def generate_emotion_chart():
    # load your data into a pandas dataframe
    df = pd.read_csv('tweets_data.csv')

    # get the top 50 users by follower count
    top_users = df.groupby('Username')['followersCount'].max().nlargest(50).index.tolist()

    # filter the dataframe to include only the top 50 users
    df_top_users = df[df['Username'].isin(top_users)]

    # define a function to analyze the emotions of each text and return a dictionary of scores
    def analyze_emotions(text):
        if isinstance(text, float):
            return {'Angry': 0, 'Fear': 0, 'Happy': 0, 'Sad': 0, 'Surprise': 0}
        else:
            emotions = te.get_emotion(text.lower())
            return emotions

    # apply the function to your text column and create a new column for the emotion scores
    df_top_users.loc[:, 'emotion_scores'] = df_top_users['Text'].apply(analyze_emotions)
    # create a new dataframe to store the emotion scores for each text
    emotions_df = pd.DataFrame(df_top_users['emotion_scores'].to_list())

    # normalize the emotion scores by dividing them by the total number of texts analyzed
    normalized_emotion_scores = emotions_df.sum() / len(emotions_df)

    # plot the normalized emotion scores for each emotion
    emotions = ['Angry', 'Fear', 'Happy', 'Sad', 'Surprise']
    plt.figure(figsize=(9, 4.16))
    plt.bar(emotions, normalized_emotion_scores, color=['red', 'orange', 'yellow', 'blue', 'green'])
    plt.title('Emotion Scores for Top 50 Users by Follower Count')
    plt.xlabel('Emotions')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    plt.savefig("static/images/emotion_bar_chart.png")
    plt.clf()
    return "static/images/emotion_bar_chart.png"
