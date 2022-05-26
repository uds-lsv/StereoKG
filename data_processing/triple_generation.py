"""
Usage: python triple_generation.py filename subject
"""

import sys
# setting path
sys.path.append('../StereoKG')

import os
import en_core_web_sm
nlp = en_core_web_sm.load()

from openie import StanfordOpenIE
from tqdm import tqdm
from Credentials import *


personal_pronouns = [
    "i", "me", "my", "mine", "im", "ive",
    "you", "you're", "your", "yours", "youre","youve", "yall", "u",
    "he", "she", "him", "her", "his", "hers","hes", "shes",
    "we", "weve", "ours", " ur ", "our",
    "theyve"
    ]

# List obtained from https://en.wiktionary.org/wiki/Category:English_modal_adverbs
modal_adverbs = [
    " really ", " surely ", " always ", " much ", " sometimes ", " so ", " likely ",
    " more ", " often ", " rarely ", " maybe ", " perhaps ", " totally ", " indeed ",
    " hypothetically ", " probably ", " obviously ", " definitely ", " essentially ", 
    " certainly ", " clearly ", " afaik ", " possibly ", " truly ", " only ", " too ",
    " just ", " such", " especially"
    ]

slang_words = [
    "bc", "lmao", "lol", "lolol", "smh", "fckn", "mfing", "mf", "omg", "tbh", "af", "wth",
    "pls", "dear", "bro", "btw", "asf", "plz"
]


class TripleGenerator():
    """
    Class for generating triples from sentences using OpenIE
    """
    def __init__(self) -> None:
        pass

    def _process_triple(self, triple) -> bool:
        elim=False

        # extend incomplete subjects
        if triple['subject'] == 'people':
            for sub in subjects:
                if(
                    (sub in triple['subject']) or
                    (sub in triple['relation']) or
                    (sub in triple['object'])
                ):
                    subject = sub
                    triple['subject'] = subject + ' people'
                    print(f"Changing subject in {triple} to '{subject}+ people'")
                    break
        
        elif triple['subject'] == 'men':
            for sub in subjects:
                if(
                    (sub in triple['subject']) or
                    (sub in triple['relation']) or
                    (sub in triple['object'])
                ):
                    subject = sub
                    triple['subject'] = subject + ' men'
                    print(f"Changing subject in {triple} to '{subject}+ men'")
                    break
        
        elif triple['subject'] == 'women':
            for sub in subjects:
                if(
                    (sub in triple['subject']) or
                    (sub in triple['relation']) or
                    (sub in triple['object'])
                ):
                    subject = sub
                    triple['subject'] = subject + ' women'
                    print(f"Changing subject in {triple} to '{subject}+ women'")
                    break
            
        # eliminate triples with personal pronouns
        for key, value in triple.items():
            for pp in personal_pronouns:
                if pp in value.split(" "):
                    elim=True
                    print(f"Eliminating {triple} containing personal pronoun")
                    break

        if elim==False:
            if ("that" in triple["object"].split(" ")):
                print(f"Eliminating {triple} containing 'that'")
                elim=True

        # eliminate triples with vague subjects like "they", "it" etc.
        if elim==False:
            if(
                (triple['subject'] == "they") or
                (triple['subject'] == "said") or
                (triple['subject'] == "r") or
                (triple['subject'] == "them") or
                (triple['subject'] == "thats") or
                (triple['subject'] == "something") or
                (triple['subject'] == "it") or
                ("their" in triple['subject']) or
                (triple['subject'] == "___")
            ):
                elim=True
                print(f"Eliminating {triple} with generic subject")
        
        # eliminate triples with vague objects like "they", "it" etc.
        if elim==False:
            if(
                (triple['object'] == "it") or
                (triple['object'] == "this") or
                (triple['object'] == "___") or
                (triple['object'] == "]")
            ):
                elim=True
                print(f"Eliminating {triple} with generic object")

        # eliminate triples not containing subject term
        if elim==False:
            found=False
            for sub in subjects:
                if(
                    (sub in triple['subject']) or
                    (sub in triple['relation']) or
                    (sub in triple['object'])
                ):
                    found=True
                    break
            
            if found:
                elim=False
            else:
                elim=True
        
        return elim


    def _get_triples(self, cluster) -> set:
        triple_cluster = set()

        for stmt in cluster:
            is_dont = False
            is_arent = False
            is_cant = False
            # preprocess sentence
            if ("cant" in stmt.split(" ")):
                is_cant = True
                stmt = stmt.replace(" cant ", " can ")
            elif ("can't" in stmt.split(" ")):
                is_cant = True
                stmt = stmt.replace(" can't ", " can ")
            
            if "don't" in stmt:
                is_dont = True
                stmt = stmt.replace(" don't ", " do ")
            elif "dont" in stmt.split(" "):
                is_dont = True
                stmt = stmt.replace(" dont ", " do ")

            if "aren't" in stmt:
                is_arent = True
                stmt = stmt.replace(" aren't ", " are ")
            elif "are not" in stmt:
                is_arent = True
                stmt = stmt.replace(" are not ", " are ")
            elif "arent" in stmt.split(" "):
                is_arent = True
                stmt = stmt.replace(" arent ", " are ")    

            for ma in modal_adverbs:
                stmt = stmt.replace(ma, " ").lower()
            
            for sw in slang_words:
                if sw in stmt.split(" "):
                    stmt = stmt.replace(sw, " ").lower()
            
            if "gonna" in stmt:
                stmt = stmt.replace("gonna", "going to")

            stmt = stmt.replace("]", "")

            client = StanfordOpenIE()
            triples = client.annotate(stmt)
            
            for triple in triples:
                for key, val in triple.items():
                    if is_cant:
                        if "american" not in val:
                            triple[key] = val.replace("can ", "can't ")
                    if is_dont:
                        triple[key] = val.replace("do", "don't")
                    if is_arent:
                        triple[key] = val.replace("are", "are not")
                    if "at_time" in val:
                        triple[key] = val.replace("at_time", "")
                    if "'" in val.split(" "): # replace stray apostrophes
                        triple[key] = val.replace(" '", " ")

                elim = self._process_triple(triple)
                
                if elim==False:
                    triple_cluster.add(tuple(triple.items())) # revert to dict using dict(tuple)

        return triple_cluster

    
    def generate_triples(self, file, subject) -> None:
        count_proc = 0
        count_unproc = 0
        inter_triples = tripledir + "/" + subject + "_triples.txt"
        unproc = unprocdir + "/" + subject + "_sentences.txt"
        
        with open(file) as c_file:
            
            if os.path.exists(inter_triples):
                os.remove(inter_triples)
            if os.path.exists(unproc):
                os.remove(unproc)
            
            f = open(inter_triples, 'a')
            uf = open(unproc, 'a')
            for line in tqdm(c_file):
                #cluster = list(ast.literal_eval(line))
                cluster = line.rstrip().split(", ")
                triples = self._get_triples(cluster)
                if triples:
                    f.write(str(triples)+"\n")
                    count_proc += 1
                else:
                    uf.write(str(cluster)+"\n")
                    count_unproc += 1
            
            f.close()
            uf.close()
            print(subject)
            print(f"Sentences processed by OpenIE: {count_proc}")
            print(f"Sentences not processed by OpenIE: {count_unproc}")
            print("==============================================================================")


if __name__ == "__main__":

    filename = sys.argv[1]
    subject = sys.argv[2]

    tg = TripleGenerator()
    tg.generate_triples(filename, subject)