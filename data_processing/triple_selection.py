"""
Usage: python 
"""

import sys
# setting path
sys.path.append('../StereoKG')

import warnings
warnings.filterwarnings("ignore")

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("textattack/distilbert-base-uncased-CoLA")
model = AutoModelForSequenceClassification.from_pretrained("textattack/distilbert-base-uncased-CoLA")

import os
import ast
import csv

from Credentials import finaldir, tripledir

device = 'cuda'

class TripleSelector():

    def __init__(self) -> None:
        self.triple_file = finaldir + "/stereoKG.tsv" 


    def _get_best_triple(self, triples) -> str:
        sentences = []
        for triple in triples:
            triple = dict(triple)
            sentence = triple["subject"] + " " + triple["relation"] + " " + triple["object"]
            sentences.append(sentence)
        
        inputs = tokenizer(sentences, return_tensors="pt", padding=True, truncation=True)
        outputs = model(**inputs)
        pt_predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        max_score = 0
        best_triple = ""

        try:
            for index, scores in enumerate(pt_predictions):
                score = scores.detach().numpy()[1]
                print(f"Triple: {triples[index]}")
                print(f"Score: {score}\n")
                if score > max_score:
                    max_score = score
                    best_triple = dict(triples[index])
        except:
            print("Error in determining best triple")
            print(f"Index: {index}")
            print(f"Score: {scores}")
            
        print(f"Best triple: {best_triple}")
        print(f"Score: {max_score}")
        print("-------------------------------------------------------")
        return best_triple

    
    def get_final_triples(self):
        totaltriples = 0
        wfile = open(self.triple_file, 'w')
        writer = csv.writer(wfile, delimiter='\t')

        for subdir, _, files in os.walk(tripledir):
            for file in files:
                fname = os.path.join(subdir, file)
                print(fname)
                with open(fname, encoding="utf-8") as json_file:
                    for line in json_file:
                        try:
                            cluster = list(ast.literal_eval(line))
                            chosen_triple = self._get_best_triple(cluster)
                            if chosen_triple:
                                writer.writerow(chosen_triple.values())
                                totaltriples += 1
                        except:
                            print(f"Exception in getting final triple for line {line}")
                            continue
            print("==================================================================")
                
        wfile.close()
        print(f"{totaltriples} generated in all.")


if __name__ == "__main__":
    ts = TripleSelector()
    ts.get_final_triples()