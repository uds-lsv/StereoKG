"""
Refer:
https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/clustering/fast_clustering.py

Requires sentence-transformers
-> pip install -U sentence-transformers

Usage: python fast_clustering.py in_file out_file create_singleton_mode cluster_file 

This is a more complex example on performing clustering on large scale dataset.
This example finds in a large set of sentences local communities, i.e., groups of sentences that are highly
similar. You can freely configure the threshold what is considered as similar. A high threshold will
only find extremely similar sentences, a lower threshold will find more sentence that are less similar.
A second parameter is 'min_community_size': Only communities with at least a certain number of sentences will be 
returned.
The method for finding the communities is extremely fast, for clustering 50k sentences it requires only 5 
seconds (plus embedding computation).
In this example, we download a large set of questions from Quora and then find similar questions in this set.
"""

from sentence_transformers import SentenceTransformer, util
import time
import sys

in_file = sys.argv[1] #file containing sentences for an entity
out_file = sys.argv[2] #file for outputting clusters
create_singleton_mode = sys.argv[3] #Optional: whether to log singleton and non-singleton clusters
cluster_file = sys.argv[4] #Optional: for creating singleton/non-singleton clusters
 
if not create_singleton_mode:
    create_singleton_mode=False

if not cluster_file:
    cluster_file = "clusterfile.text"

# Model for computing sentence embeddings. We use one trained for similar questions detection
model = SentenceTransformer('all-MiniLM-L6-v2')

with open(in_file,"r") as f:
    corpus_sentences = list(set(f.readlines()))

print(f"Encoding {len(corpus_sentences)} sentences. This might take a while...")
corpus_embeddings = model.encode(corpus_sentences, batch_size=64, show_progress_bar=True, convert_to_tensor=True)

print("Start clustering")
start_time = time.time()

#Two parameters to tune:
#min_cluster_size: Only consider cluster that have at least n elements
#threshold: Consider sentence pairs with a cosine-similarity larger than threshold as similar
clusters = util.community_detection(corpus_embeddings, min_community_size=1, threshold=0.82)
print("Clustering done after {:.2f} sec".format(time.time() - start_time))

# Statistics
cluster_count = 0
singleton_count = 0
non_singleton_count = 0

with open(out_file, "w") as f:
    for i, cluster in enumerate(clusters):
        print("Cluster {}, #{} Elements".format(i+1, len(cluster)))
        cluster_count += len(cluster)
        
        f.write("[")
        for sentence_id in cluster[:-1]:
            f.write(f"'{corpus_sentences[sentence_id].rstrip()}', ")
        f.write(f"'{corpus_sentences[cluster[-1]].rstrip()}'")
        f.write("]\n")

        if create_singleton_mode:
            if len(cluster) == 1:
                singleton_count += 1
                f_s = open(cluster_file, "a")
                f_s.write("[")
                for sentence_id in cluster:
                    f_s.write(f"'{corpus_sentences[sentence_id].rstrip()}', ")
                f_s.write("]\n")
            else:
                non_singleton_count +=1
                f_ns = open(cluster_file, "a")
                f_ns.write("[")
                for sentence_id in cluster[:-1]:
                    f_ns.write(f"'{corpus_sentences[sentence_id].rstrip()}', ")
                f_ns.write(f"'{corpus_sentences[cluster[-1]].rstrip()}'")
                f_ns.write("]\n")

print(f"Total clusters: {len(clusters)}, total elements in all clusters: {cluster_count}")
print(f"No. of singleton clusters = {singleton_count} and non-singleton clusters = {non_singleton_count}")