"""
This file contains account access credentials and other filepaths used for storing and accessing data
in different stages of the pipeline.
It also makes the respective imports
"""

# Subreddits for data scraping
import praw
reddit = praw.Reddit(client_id='2DykHGe-a6KtaQ', client_secret='o5Tc-zAUmeFYCJ4hkaSvYQ5_gGDE1g', user_agent='RedditScraperNLP')
subreddit_indian = reddit.subreddit("India+india+indiadiscussion+IndianFood+indianpeoplefacebook+explainlikeimfive+retailhell+AskReddit+TooAfraidToAsk+NoStupidQuestions+ABCDesis")
subreddit_american = reddit.subreddit("explainlikeimfive+OutOfTheLoop+AskAnAmerican+linguistics+offmychest+AskReddit+TooAfraidToAsk+NoStupidQuestions")
subreddit_french = reddit.subreddit("French+france+AskAFrench+explainlikeimfive+AskEurope+AskReddit+NoStupidQuestions")
subreddit_german = reddit.subreddit("explainlikeimfive+AskReddit+TooAfraidToAsk+NoStupidQuestions+germany+German+europe+AskGermany+offmychest+AskAGerman")
subreddit_chinese = reddit.subreddit("explainlikeimfive+AskReddit+TooAfraidToAsk+NoStupidQuestions+shanghai+China+asianamerican+HongKong+Sino")
subreddit_hindu = reddit.subreddit("explainlikeimfive+AskReddit+TooAfraidToAsk+NoStupidQuestions+India+hindusim+librandu+IndiaSpeaks+awakened+IAmA+atheismindia+india+AskHistorians")
subreddit_jew = reddit.subreddit("explainlikeimfive+AskReddit+TooAfraidToAsk+NoStupidQuestions+Judaism+AskHistorians+religion+DebateReligion+AskSocialScience+Discussion")
subreddit_atheist = reddit.subreddit("explainlikeimfive+AskReddit+TooAfraidToAsk+NoStupidQuestions+TrueAtheism+religion+DebateReligion+atheism")
subreddit_muslim = reddit.subreddit("religion+DebateReligion+TraditionalMuslims+progressive_islam+atheism+islam+exmuslim+Hijabis+indianmuslims+AskSocialScience+AskReddit+NoStupidQuestions+explainlikeimfive+ask")
subreddit_christian = reddit.subreddit("religion+DebateReligion+TrueChristian+DebateAChristian+AskAChristian+atheism+Christianity+Christian+AskReddit+NoStupidQuestions+explainlikeimfive+Christianmarriage+Bible")


# Twitter
# Replace by your own developer API
consumer_key = ""
consumer_secret = ""
access_token =  ""
access_token_secret = ""
bearer_token = ""
search_url = "https://api.twitter.com/2/tweets/search/all"

# General 
scrapedir = "./scraped_data"
"""
Unprocessed files containing data scraped from Reddit and Twitter
""" 

questionsdir = "./questions"
"""
Questions are stored in files 'christian', 'muslim', 'indian', 'french' etc. for both, reddit and twitter
(following certain templates)
"""

sentencedir = "./sentences"
"""
Sentences are stored in files 'christian', 'muslim', 'indian', 'french' etc. for both, reddit and twitter
"""

clusterdir = "./clusters"
"""
Clusters of sentences are stored in files christian_cluster, muslim_cluster etc.
"""

tripledir = "./triples"
"""
files are of the form subject_number
All triples formed for sentences are in one cluster
"""

unprocdir = "./unproc"
"""
All unprocessed sentences for analysis
"""

finaldir = "./kg"
"""
Contains final tsv file
"""

subjects = ['indian', 'indian men', 'indian women', 'indian people',
'french', 'french men', 'french women', 'french people',
'american', 'american men', 'american women', 'american people',
'german', 'german men', 'german women', 'german people',
'chinese', 'chinese men', 'chinese women', 'chinese people',
'christian', 'christian men', 'christian women', 'christian people', 'christianity',
'muslim', 'muslim men', 'muslim women', 'muslim people', 'islam',
'jewish', 'jewish men', 'jewish women', 'jewish people', 'judaism',
'hindu', 'hindu men', 'hindu women', 'hindu people', 'hinduism',
'atheist', 'atheist people', 'atheism'
]