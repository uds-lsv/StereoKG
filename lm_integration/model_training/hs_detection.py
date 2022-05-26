import sys
import pandas as pd
import torch
import gc
from simpletransformers.classification import (ClassificationModel, ClassificationArgs)
import sklearn
from scipy import stats
import random
import time

# Arguments
TRAIN_FILE= sys.argv[1]
VAL_FILE= sys.argv[2]
TEST_FILE= sys.argv[3]

MODEL_DIR = sys.argv[4]
OUTPUT_DIR = sys.argv[5]
MODEL = sys.argv[6]

CUDA_DEVICE=0
NUM_LOOPS=10 #Average out the scores over 10 tests
NUM_EPOCHS=7

test = pd.read_csv(TEST_FILE, sep=",", names=['labels', 'text'],header=0, index_col=False)
training = pd.read_csv(TRAIN_FILE, sep=",", names=['labels', 'text'], header=0, index_col=False)
eval = pd.read_csv(VAL_FILE, sep=",", names=['labels', 'text'], header=0, index_col=False)

training['labels'] = training['labels'].astype(int)
test['labels'] = test['labels'].astype(int)
eval['labels'] = eval['labels'].astype(int)

gc.collect()
torch.cuda.empty_cache()

running_acc=0
running_f1=0
acc_se = []
f1_se = []

main_start = time.time()

for i in range(NUM_LOOPS):
    print(f"Training (Iter {i+1})...")

    model_args=ClassificationArgs(num_train_epochs=NUM_EPOCHS,
                                overwrite_output_dir=True)
    model_args.manual_seed = random.randint(10,90)
    model_args.best_model_dir = MODEL_DIR+"_"+str(i)
    model_args.output_dir = OUTPUT_DIR
    model_args.cache_dir=OUTPUT_DIR+"/cache_dir"
    model_args.tensorboard_dir=OUTPUT_DIR+"/runs"
    model_args.normalization = True
    model_args.reprocess_input_data = True
    model_args.evaluate_during_training = True
    model_args.evaluate_during_training_verbose = True
    model_args.train_batch_size=8
    model_args.eval_batch_size=8
    model_args.learning_rate=1e-5
    model_args.max_seq_length=512
    model_args.early_stopping_metric="f1"
    model_args.early_stopping_metric_minimize=False
    model_args.use_early_stopping=True
    model_args.early_stopping_consider_epochs=True
    model_args.early_stopping_patience=3

    loop_start = time.time()

    model = ClassificationModel(model_type='roberta',
                                model_name=MODEL, 
                                args=model_args, 
                                num_labels=2,
                                cuda_device=CUDA_DEVICE)

    shuffled_training = training.sample(frac=1).reset_index(drop=True)
    model.train_model(train_df=shuffled_training, eval_df=eval, f1=sklearn.metrics.f1_score)

    result, model_outputs, wrong_predictions = model.eval_model(eval,
                acc=sklearn.metrics.accuracy_score,
                f1=sklearn.metrics.f1_score)

    print("Eval Result:")
    print(result)

    predictions, raw_outputs = model.predict(test["text"].to_list())
    acc=sklearn.metrics.accuracy_score(predictions, test['labels'])
    f1=sklearn.metrics.f1_score(predictions, test['labels'], zero_division=0)

    print(f"Test Accuracy: {acc}")
    print(f"Test F1: {f1}")

    running_acc+=acc
    acc_se.append(acc)
    running_f1+=f1
    f1_se.append(f1)
    loop_end = time.time()
    hours, rem = divmod(loop_end-loop_start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    print("-------------------------------------------------------")

avg_acc= round(running_acc/NUM_LOOPS, 4)
avg_f1= round(running_f1/NUM_LOOPS, 4)
print(f"Average Accuracy = {avg_acc}")
print(f"Standard error = {stats.sem(acc_se)}")
print(f"Average F1 = {avg_f1}")
print(f"Standard error = {stats.sem(f1_se)}")

main_end = time.time()
hours, rem = divmod(main_end-main_start, 3600)
minutes, seconds = divmod(rem, 60)
print("Overall time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))