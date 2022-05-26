"""
Usage: python triple_to_text.py knowledge_graph_file output_file train_csv batch_size epochs_num path_to_model
"""

import sys
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration,Adafactor


KB_FILE = sys.argv[1]
OUT_FILE = sys.argv[2]
path_to_train = sys.argv[3]
batch_size = sys.argv[4]
epochs = sys.argv[5]
model_dir = sys.argv[6]


class EarlyStopping():
    # 
    # Early stopping to stop the training when the loss does not improve after
    # certain epochs.
    # 
    def __init__(self, patience=3, min_delta=0.01):
        #
        # :param patience: how many epochs to wait before stopping when loss is
        #        not improving
        # :param min_delta: minimum difference between new loss and old loss for
        #        new loss to be considered as an improvement
        # 
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, value):
        if self.best_loss == None:
            self.best_loss = value
        
        if self.best_loss - value > self.min_delta:
            self.best_loss = value
        elif self.best_loss - value < self.min_delta:
            self.counter += 1
            print(f"INFO: Early stopping counter {self.counter} of {self.patience}")
            if self.counter >= self.patience:
                print('INFO: Early stopping')
                self.early_stop = True


def train():
    train_df=pd.read_csv(path_to_train, index_col=[0])
    train_df=train_df.iloc[  :35000,:]
    train_df=train_df.sample(frac=1)
    batch_size = batch_size
    num_of_batches = int(len(train_df)/batch_size)
    num_of_epochs = epochs

    if torch.cuda.is_available():
        dev = torch.device("cuda:3")
    else:
        dev = torch.device("cpu")

    tokenizer = T5Tokenizer.from_pretrained("t5-base")
    model = T5ForConditionalGeneration.from_pretrained("t5-base",
                                                return_dict=True)
    #moving the model to GPU
    model.to(dev)

    optimizer = Adafactor(model.parameters(),lr=1e-4,
                        eps=(1e-30, 1e-3),
                        clip_threshold=1.0,
                        decay_rate=-0.8,
                        beta1=None,
                        weight_decay=0.0,
                        relative_step=False,
                        scale_parameter=False,
                        warmup_init=False)

    # Training
    model.train()
    early_stopping = EarlyStopping()
    loss_per_500_steps=[]

    for epoch in tqdm(range(1,num_of_epochs+1)):
        print('Running epoch: {}'.format(epoch))
        running_loss=0

        for i in range(num_of_batches):
            inputbatch=[]
            labelbatch=[]
            new_df=train_df[i*batch_size:i*batch_size+batch_size]
            for indx,row in new_df.iterrows():
                input = 'WebNLG: '+ row['input_text']
                labels = row['target_text']
                inputbatch.append(input)
                labelbatch.append(labels)
        
            inputbatch=tokenizer.batch_encode_plus(inputbatch,padding=True,max_length=400,return_tensors='pt')["input_ids"]
            labelbatch=tokenizer.batch_encode_plus(labelbatch,padding=True,max_length=400,return_tensors="pt") ["input_ids"]
            inputbatch=inputbatch.to(dev)
            labelbatch=labelbatch.to(dev)

            # clear out the gradients of all Variables 
            optimizer.zero_grad()

            # Forward propogation
            outputs = model(input_ids=inputbatch, labels=labelbatch)
            loss = outputs.loss
            loss_num=loss.item()
            logits = outputs.logits
            running_loss+=loss_num
            if i%500 ==0:      
                loss_per_500_steps.append(loss_num)

            # calculating the gradients
            loss.backward()

            #updating the params
            optimizer.step()
   
        running_loss=running_loss/int(num_of_batches)
        print('Epoch: {} , Running loss: {}'.format(epoch,running_loss))
        early_stopping(running_loss)
        if early_stopping.early_stop:
            print(f"Early stopping induced at epoch {epoch+1}")
            break
        else:
            torch.save(model.state_dict(), model_dir + '/pytorch_model.bin')

    steps = [i*100 for i in range(len(loss_per_500_steps))]
    plt.plot(steps, loss_per_500_steps)
    plt.title('Loss')
    plt.xlabel('Steps')
    plt.ylabel('Loss')
    plt.show()
    plt.savefig("./t5_train_loss.jpg")


def generate(text,model,tokenizer):
   model.eval()
   input_ids = tokenizer.encode("WebNLG:{}".format(text), 
                               return_tensors="pt")  
   outputs = model.generate(input_ids)
   gen_text=tokenizer.decode(outputs[0]).replace('<pad>','').replace('</s>','')
   return gen_text


def test():
    tokenizer = T5Tokenizer.from_pretrained('t5-base')
    model =T5ForConditionalGeneration.from_pretrained(model_dir, return_dict=True)

    out_file=open(OUT_FILE,"w")
    stereo_triples = pd.read_csv(KB_FILE, sep="\t", names=['subject', 'predicate', 'object'],
                        header=None, index_col=False)
    stereo_triples=stereo_triples.reset_index()

    for index, row in tqdm(stereo_triples.iterrows()):
        text = row['subject']+" | "+row['predicate']+" | "+row['object']
        ret_text = generate(text, model, tokenizer)
        ret_text=ret_text.lstrip().rstrip()
        out_file.write(ret_text+"\n")
    
    out_file.close()