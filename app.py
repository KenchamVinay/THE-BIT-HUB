from flask import Flask, render_template, url_for, redirect
import warnings
warnings.simplefilter("ignore", category=UserWarning)
warnings.simplefilter("ignore", category=DeprecationWarning)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
from textblob import TextBlob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pie_chart
import bar_chart
import toptweets
import os
import pytz

# Define function to clean tweet text
import re
import string
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
nltk.download('stopwords', quiet=True)
nltk.download('stopwords')

app = Flask(__name__, template_folder='template', static_url_path='/static')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#creating a table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False) 

#------------------------------commands to be runned ro create table and verify if tabels are created--------------
#python
# from filename import db
# create_all()
# exit()
# in cmd goto frontend folder and run sqlite3 database.db
# then run .tables
# if the output is users then table is created sucessfully    
#-------------------------------------------------------------------------------------------------------------------


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit_signup = SubmitField('Sign Up', render_kw={'id': 'signupbutton'})

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')



class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit_login = SubmitField('Log In', render_kw={'id': 'loginbutton'} )
    
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('about'))
    return render_template('index.html', form = form)

@app.route('/About')
@login_required
def about():
    return render_template('About.html')

@app.route('/livetweets')
@login_required
def livetweets():
    return render_template('livetweets.html')

# Define function to clean tweet text
def clean_tweet_text(tweet_text):
    cleaned_text = re.sub("#bitcoin", "bitcoin", tweet_text)
    cleaned_text = re.sub("#\S+", "", cleaned_text)
    cleaned_text = re.sub("\n", "", cleaned_text)
    cleaned_text = re.sub("https?://\S+", "", cleaned_text)
    cleaned_text = re.sub("(@[A-Za-z0-9_]+)","", cleaned_text)
    cleaned_text = re.sub('\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()

    return cleaned_text

def get_sentiment_label(polarity):
    if polarity > 0:
        return 'Positive'
    elif polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Define hashtags to search for
    hashtags = ["#bitcoin"]
    # Define file path to save data
    csv_file_path = 'tweets_data.csv'
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
                if likeCount < 100 and retweetCount < 100 and tweet_user_followers < 100 and replyCount < 100:
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
        # Read the data from the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Get the datetime of the first row
        first_row_datetime = pd.to_datetime(df.iloc[0]["Datetime"])
        
        # Get today's date
        today = pd.Timestamp.now().tz_localize('Asia/Kolkata').date()
        
        # Check if the first row's datetime is not from today
        if first_row_datetime.date() != today:
            print(f"Data for {hashtags} in file {csv_file_path} is from a previous day. Scraping new data for tweets generated today...")
            df = pd.DataFrame(columns=["Datetime", "Text", "Username", "likeCount", "retweetCount", "replyCount", "followersCount", "Subjectivity", "Polarity", "Text Sentiment"])
            # tweets_collected = 0
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
                    if likeCount < 100 and retweetCount < 100 and tweet_user_followers < 100 and replyCount < 100:
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
            print(f"Data for {hashtags} in file {csv_file_path} is from today. No need to scrape new data.")
            
            # Load the data from CSV file
            df = pd.read_csv(csv_file_path)
            print(f"Data loaded from {csv_file_path}")
            # Convert the "Datetime" column to a datetime object
            df["Datetime"] = pd.to_datetime(df["Datetime"])
            
        # Check if the data is more than 1 hour old
        now = datetime.now()
        tweets_collected = 0
        unique_users = set()

        csv_file_path = "tweets_data.csv"
        hashtags = ["#bitcoin"]

        df = pd.read_csv(csv_file_path)

        ust_tz = pytz.timezone("UTC")
        ist_tz = pytz.timezone("Asia/Kolkata")

        # Convert the datetime in the CSV file from UST to IST
        first_tweet_datetime_ust = datetime.strptime(df.iloc[0]["Datetime"], '%Y-%m-%d %H:%M:%S').replace(tzinfo=ust_tz)
        first_tweet_datetime_ist = first_tweet_datetime_ust.astimezone(ist_tz)

        # Compare the current time in IST with the datetime in the CSV file in IST
        if (datetime.now(ist_tz) - first_tweet_datetime_ist) > timedelta(hours=5):
            print(f"Data for {hashtags} in file {csv_file_path} is more than 5 hour old. Scraping new data for tweets generated since {df.iloc[0]['Datetime']}")
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
                    if likeCount < 100 and retweetCount < 100 and tweet_user_followers < 100 and replyCount < 100:
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
            print(f"Data for {hashtags} in file {csv_file_path} is less than 5 hour old. No need to scrape new data.")



    from scatter_plot import generate_scatter_plot
    generate_scatter_plot(df)

    # Pie chart to display tweet sentiments
    from pie_chart import generate_pie_chart
    generate_pie_chart(df)

    # Plotting the bar chart
    from bar_chart import generate_bar_chart
    generate_bar_chart(df)

    #top positive and negitive tweets
    from toptweets import get_top_tweets
    positive_tweets, negative_tweets = get_top_tweets(df)

    #get top influenced tweets
    from topinfluenced import get_top_influencers
    influencer_df = get_top_influencers(df)

    from likes_bar import influencer_bar
    influencer_bar(influencer_df)


    from emotion import generate_emotion_chart
    # generate the emotion chart
    chart_path = generate_emotion_chart()


    return render_template('dashboard.html', positive_tweets=positive_tweets, negative_tweets=negative_tweets, influencer_df=influencer_df, chart_path=chart_path)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))


    return render_template('register.html', form = form)
#------------------------------------------------------------
#goto project folder in cmd
#type sqlite3 database.db
#then type select * from user; to see all the users in DB
#------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)