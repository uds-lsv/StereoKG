"""
Usage: python scrape_reddit.py file_path_to_questions subject
"""

import sys
# setting path
sys.path.append('../StereoKG')

import json
from tqdm import tqdm

from Credentials import *
from data_processing import utils


# Variables for analysis
total_reddit_sentences=0
total_reddit_posts=0


class rSubmission():
    """
    Object for a Reddit Post
    """
    def __init__(self):
        self.title = ""  # title of post
        self.score = None  # score of post = number of upvotes
        self.upvote_ratio = None  # percentage of upvotes
        self.id = None  # unique id of post
        self.link_flair_text = None  # flair of submission
        self.num_comments = 0  # number of comments on post
        self.created = None  # timestamp of post

        self.comments_dict = {
            "comment_id": [],  # unique comment id
            "comment_parent_id": [],  # comment parent id
            "comment_body": [],  # text in comment
            "comment_link_id": []  # link to comment
        }

    def set_details(self, **details):
        self.title = details["title"]
        self.score = details["score"]
        self.upvote_ratio = details["upvote_ratio"]
        self.id = details["sid"]
        self.link_flair_text = details["link_flair_text"]
        self.num_comments = details["num_comments"]
        self.created = details["created"]

    def set_comments(self, **kwargs):
        self.comments_dict["comment_id"].append(kwargs["comment_id"])
        self.comments_dict["comment_parent_id"].append(kwargs["comment_parent_id"])
        self.comments_dict["comment_body"].append(kwargs["comment_body"])
        self.comments_dict["comment_link_id"].append(kwargs["comment_link_id"])

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def scrape_reddit(subject, query, subreddit, maindir):
    """
    Scrape Reddit for a given query
    """
    local_reddit_sentences=0
    local_reddit_posts=0
    global total_reddit_sentences
    global total_reddit_posts

    #tqdm.write(query)
    s = query.split(" ")

    submissions = subreddit.search(query, sort="relevance", limit=800) #PRAW search functionality
    i = 1
    for sub in submissions:
        # Keep the submission only if it contains the query keywords
        if (subject in sub.title.lower() and (sub.upvote_ratio > 0.5)
            ):
            mysub = rSubmission() # Class for a Reddit Submission
            mysub.set_details(title=sub.title,
                              score=sub.score,
                              upvote_ratio=sub.upvote_ratio,
                              sid=sub.id,
                              link_flair_text=sub.link_flair_text,
                              num_comments=sub.num_comments, created=sub.created)

            sub.comments.replace_more(limit=10)
            for com in sub.comments.list():
                mysub.set_comments(comment_id=com.id,
                                   comment_parent_id=com.parent_id,
                                   comment_body=com.body,
                                   comment_link_id=com.link_id)
 
            utils.file_scraped_data_reddit(mysub, maindir, query, str(i))
            local_reddit_posts += 1
            total_reddit_posts += 1
            i += 1
            sentences = utils.preprocess_reddit(sub.title)
            for sent in sentences:
                if subject in sent.lower():
                    utils.add_to_file(sent, subject, maindir)
                    total_reddit_sentences +=1
                    local_reddit_sentences +=1

    print(f"Subject: {subject}")
    print(f"Query: {query}")
    print(f"Total submissions scraped: {local_reddit_posts}")
    print(f"Total sentences retrieved: {local_reddit_sentences}")


if __name__ == "__main__":
    filename = sys.argv[1]
    subject = sys.argv[2]
    
    # For each subject
    with open(filename) as f:
        for line in tqdm(f):
            subject = line.split(",")[0]
            query = line.split(",")[1].strip("\n")
            scrape_reddit(subject, query, subreddit_hindu, subject)

    print(f"Source: Reddit")
    print(f"Total posts scraped: {total_reddit_posts}")
    print(f"Total sentences retrieved: {total_reddit_sentences}")