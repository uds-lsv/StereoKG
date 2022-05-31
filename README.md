# StereoKG
Repository for WOAH paper **"StereoKG: Data-Driven Knowledge Graph Construction for Cultural Knowledge and Stereotypes"** ([paper](https://arxiv.org/abs/2205.14036))

---

## Requirements
Software:


    PRAW
    NLTK
    PyTorch
    SimpleTransformers
    HuggingFace Transformers


---

## Account Credentials
1. PRAW -  Set up a [Reddit](https://www.reddit.com/) Account
2. Twitter - Access [Twitter Developer API](https://developer.twitter.com/en) Credentials

## Pipeline

### Credentials

In ``Credentials.py``, include all metadata like the subreddits to query, Twitter developer credentials, absolute paths to respective directories, and a list of all subject entities in the KG.

### Question Templates
The question templates are stored for each entity in the ``questions`` folder. For using additional entities, simply create a questions file for that entity and enter the questions in the format

``subject, <question pattern>``

### (1) Data Extraction
1. Scraping Reddit - scrape_reddit.py
2. Scraping Twitter - scrape_twitter.py

The extracted questions are inherently converted to sentences and stored in the filepath specified in ``Credentials.py``.


    germans are obsessed with the wednesday frog meme
    indians are inherently happy
    christians are supporting donald trump
    Muslim women wear burkha


### (2) Fast clustering
``fast_clustering.py`` can be run to perform clustering on the sentences. If the ``create_singleton_mode`` is true, separate files are created for singleton and non-singleton clusters. 

    ['Christians believe everyone else should live and abide by their rules', 'Christians love to assume that everyone is supposed to live by the rules of their religion']
    ['indians are so loud', 'indians are always so loud in public places', 'indians are such noisy eaters']
    ['French people speak so fast', 'Serious question why do french people talk so quick', 'French people speak so quickly I am just a child']

### (3) Triple Generation
``triple_generation.py`` can be used to extract triples from sentences in clusters using a Python based ``OpenIE`` wrapper.


### (4) Triple Selection
This process uses the DistilBERT-CoLA model for choosing the most grammatically appropriate triple from the cluster of triple samples.

    <indians, don't sacrifice, freedom>
    <christians, don't remember, sabbath day>
    <atheists, are at, peace with death>

---

## KG 
The resultant KG of triples is saved in ``kg/stereoKG.tsv``. 

Using the ``triple_to_text`` model trained on WebNLG data, this same KG is converted to a verbalized form and saved in ``kg/stereoKG_linearised.txt``.

---

## Experiments

The code for language modeling integration experiments with intermediate pretraining can be found in ``lm_integration``. 

## Models
The best models in our research paper are [Twitter-RoBERTa](https://huggingface.co/cardiffnlp/twitter-roberta-base) models with intermediate pretraining on the structured and unstructured KG triples. They can be found at the following links:

1. [StereoKG-DT-SK](https://huggingface.co/eetnawa/StereoKG-DT-SK) -  Domain (Twitter) pre-trained RoBERTa with intermediate pretraining on verbalised triples.
2. [StereoKG-DT-UK](https://huggingface.co/eetnawa/StereoKG-DT-UK) - Domain (Twitter) pre-trained RoBERTa with intermediate pretraining on scraped sentences. 

***

