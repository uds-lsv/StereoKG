"""
Usage: python webnlg_generate_dataset.py path_to_webnlg

Refer:
https://towardsdatascience.com/data-to-text-generation-with-t5-building-a-simple-yet-advanced-nlg-model-b5cce5a6df45

Download the WebNLG 2020 dataset from:
https://gitlab.com/shimorina/webnlg-dataset/-/tree/master/release_v3.0
"""

import glob
import re
import xml.etree.ElementTree as ET
import pandas as pd

path_to_webnlg = sys.argv[1]

#files = glob.glob("path_to_datasets/WebNLG/webnlg-dataset-master/webnlg_challenge_2017/train/**/*.xml", recursive=True)
files = glob.glob(path_to_webnlg, recursive=True)

triple_re=re.compile('(\d)triples')
data_dct={}
for file in files:
    tree = ET.parse(file)
    root = tree.getroot()
    triples_num=int(triple_re.findall(file)[0])
    for sub_root in root:
        for ss_root in sub_root:
            strutured_master=[]
            unstructured=[]
            for entry in ss_root:
                unstructured.append(entry.text)
                strutured=[triple.text for triple in entry]
                strutured_master.extend(strutured)
            unstructured=[i for i in unstructured if i.replace('\n','').strip()!='' ]
            strutured_master=strutured_master[-triples_num:]
            strutured_master_str=(' && ').join(strutured_master)
            data_dct[strutured_master_str]=unstructured
mdata_dct={"prefix":[], "input_text":[], "target_text":[]}
print(len(data_dct.items()))
for st,unst in data_dct.items():
    for i in unst:
        mdata_dct['prefix'].append('webNLG')
        mdata_dct['input_text'].append(st)
        mdata_dct['target_text'].append(i)


df=pd.DataFrame(mdata_dct)
df.to_csv('/data/users/adeshpande/stereo_kg_v2/datasets/WebNLG/webNLG2020_train.csv')