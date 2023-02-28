import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List

def influencer_bar(influencer_data: List[dict]):
    # Create a pandas DataFrame from the influencer data
    df = pd.DataFrame(influencer_data)

    # Sort the data by total number of likes
    df = df.sort_values('Total number of likes', ascending=False)

    # Get the top 5 influencers by total number of likes
    top_influencers = df.head(5)

    # Get the usernames and total number of likes for the top influencers
    usernames = top_influencers['Username'].tolist()
    likes = top_influencers['Total number of likes'].tolist()

    # Create a bar chart
    x_pos = np.arange(len(usernames))
    plt.bar(x_pos, likes, align='center', color='purple')
    plt.xticks(x_pos, usernames)
    plt.ylabel('Total number of likes')
    plt.title('Top 5 Influencers by Total Number of Likes')
    plt.savefig('static/images/influencer_bar.png')
    # Show the chart
    plt.show()
    plt.clf()
