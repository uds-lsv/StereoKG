"""
Usage: python scrape_twitter.py file_path_to_questions subject
"""

import sys
# setting path
sys.path.append('../StereoKG')

import pandas as pd
from tqdm import tqdm
import time

from pathlib import Path
import requests

from Credentials import *
from data_processing import utils
from data_processing.StatementMaker import StatementMaker
statement_maker = StatementMaker(use_cache=False)

# Variables for analysis
total_twitter_sentences=0
total_twitter_posts=0


class TweetScraper():
    """
    Functionality for scraping tweets using API
    """

    def __init__(self):
        pass

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers


    def connect_to_endpoint(self, search_url, headers, params):
        response = requests.request("GET", search_url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()


    def full_twitter_search(self, subject, query, parent):
        local_twitter_sentences=0
        local_twitter_posts=0
        global total_twitter_sentences
        global total_twitter_posts

        tweets_list = []
        fname = subject + "_" + ''.join(query.strip(" "))
        query = '(' + query + ' -is:retweet)'
        #tqdm.write(query)

        # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
        # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
        query_params = {'query': query, 'tweet.fields': 'public_metrics,author_id,entities,geo',
                        'start_time': '2013-06-01T00:00:00z', 'end_time': '2021-06-30T00:00:00z', 'max_results': '500'}

        headers = self.create_headers(bearer_token)
        tweets = self.connect_to_endpoint(search_url, headers, query_params)
        if tweets.get('data', 0) != 0: 
            for tweet in tweets['data']:
                if tweet['public_metrics']['like_count'] < 5:
                    continue
                else:
                    t_params = [
                        tweet['text'],
                        tweet['author_id'],
                        tweet['id'],
                        tweet.get('entities', '-'),
                        tweet['public_metrics']['like_count'],
                        tweet['public_metrics']['retweet_count'],
                        tweet['public_metrics']['reply_count']
                    ]
                    tweets_list.append(t_params)
                    local_twitter_posts += 1
                    total_twitter_posts += 1
                    sents =  utils.process_tweet(tweet['text'])
                    for sent in sents:
                        if subject in sent:
                            utils.add_to_file(sent, subject, parent)
                            local_twitter_sentences += 1
                            total_twitter_sentences += 1

            next_token = (tweets['meta'].get('next_token', None))

            try:
                while next_token != None:
                    if len(tweets_list) > 1000:  # was 500 originally
                        break
                    print("...", end='')
                    query_params['next_token'] = next_token
                    tweets = self.connect_to_endpoint(search_url, headers, query_params)
                    for tweet in tweets['data']:
                        if tweet['public_metrics']['like_count'] < 5:
                            continue
                        else:
                            t_params = [
                                tweet['text'],
                                tweet['author_id'],
                                tweet['id'],
                                tweet.get('entities', '-'),
                                tweet['public_metrics']['like_count'],
                                tweet['public_metrics']['retweet_count'],
                                tweet['public_metrics']['reply_count']
                            ]
                            tweets_list.append(t_params)
                            local_twitter_posts += 1
                            total_twitter_posts += 1
                            sents = utils.process_tweet(tweet['text'])
                            for sent in sents:
                                if subject in sent:
                                    utils.add_to_file(sent, subject, parent)
                                    local_twitter_sentences += 1
                                    total_twitter_sentences += 1
                    next_token = (tweets['meta'].get('next_token', None))
            except:
                print("\nLimit exceeded. Saving data...")

        tweets_df = pd.DataFrame(tweets_list, columns=['Tweet Text', 'Author id', 'Tweet id',
                                                    'Entities', 'Likes', 'Retweets', 'Replies'])
        utils.file_scraped_data_twitter(tweets_df, parent, fname)
        print(f"\nSubject: {subject}")
        print(f"Query: {query}")
        print(f"Total submissions scraped: {local_twitter_posts}")
        print(f"Total sentences retrieved: {local_twitter_sentences}")


if __name__ == "__main__":

    filename = sys.argv[1]
    sub = sys.argv[2]
    
    with open(filename) as f:
        for line in tqdm(f):
            subject = line.split(",")[0]
            query = line.split(",")[1].strip("\n")
            ts = TweetScraper()
            ts.full_twitter_search(subject, query, sub)
            time.sleep(3)

    print(f"Source: Twitter")
    print(f"Total posts scraped: {total_twitter_posts}")
    print(f"Total sentences retrieved: {total_twitter_sentences}")