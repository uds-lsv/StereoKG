"""
Usage: python create_interlm_data filepath datapath
"""

import sys
import os
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
from random import shuffle


# From sentence clusters for Unstructured Data
def from_sentence_clusters(cluster_dir=None, data_dir=None) -> None:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    tokenizer = AutoTokenizer.from_pretrained("textattack/distilbert-base-uncased-CoLA")
    model = AutoModelForSequenceClassification.from_pretrained("textattack/distilbert-base-uncased-CoLA")
    device = 'cuda'

    def get_best_sentence_from_cluster(cluster):
        if len(cluster)==1:
            return cluster[0]
        else:
            inputs = tokenizer(cluster, return_tensors="pt", padding=True, truncation=True)
            outputs = model(**inputs)
            pt_predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            max_score = 0
            best_sentence = ""
            try:
                for index, scores in enumerate(pt_predictions):
                    score = scores.detach().numpy()[1]
                    if score > max_score:
                        max_score = score
                        best_sentence = cluster[index]
            except:
                best_sentence = cluster[0]
                
            return best_sentence

    
    sentences = []
    for filename in os.listdir(cluster_dir):
        filename = os.path.join(cluster_dir, filename)
        with open(filename,"r",encoding="utf-8") as f:
            for line in tqdm(f):
                line=re.sub(r"[\[\]']", "", line)
                cluster = line.rstrip().split(", ")
                best_sentence = get_best_sentence_from_cluster(cluster)
                sentences.append(best_sentence.rstrip(","))
    
    df = pd.DataFrame(sentences, columns=['Sentence'])
    # shuffle data
    df = df.sample(frac=1,random_state=42).reset_index(drop=True)
    train, validate, test = np.split(df, [int(.7*len(df)), int(.8*len(df))])

    f_train = data_dir + "train.txt"
    f_dev = data_dir + "dev.txt"
    f_test = data_dir + "test.txt"
    np.savetxt(f_train, train.values,fmt='%s', encoding='utf-8')
    np.savetxt(f_dev, validate.values,fmt='%s', encoding='utf-8')
    np.savetxt(f_test, test.values,fmt='%s', encoding='utf-8')


# From linearised triples for Structured Data
def from_triples(triple_file=None, data_dir=None):

    sentences=[]
    with open(file,"r",encoding="utf-8") as f:
        for line in tqdm(f):
            line=line.lstrip().rstrip()
            sentences.append(line)
    
    shuffle(sentences)
    train, validate, test = np.split(sentences, [int(.7*len(sentences)), int(.8*len(sentences))])

    f_train = data_dir + "train.txt"
    f_dev = data_dir + "dev.txt"
    f_test = data_dir + "test.txt"
    np.savetxt(f_train, train, fmt='%s', encoding='utf-8')
    np.savetxt(f_dev, validate, fmt='%s', encoding='utf-8')
    np.savetxt(f_test, test, fmt='%s', encoding='utf-8')


if __name__ == "__main__":
    file = sys.argv[1]
    data_dir = sys.argv[2]

    # Comment out the required call during execution
    from_sentence_clusters(file, data_dir)
    from_triples(file, data_dir)