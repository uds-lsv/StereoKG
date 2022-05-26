import sys
import logging
#sys.path.append('/nethome/druiter/code/simpletransformers/')
from simpletransformers.language_modeling import LanguageModelingModel, LanguageModelingArgs
from transformers import AutoTokenizer 
# replace by required model
"""
cardiffnlp/twitter-roberta-base OR roberta-base
"""
tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base')
MODEL_PATH = "cardiffnlp/twitter-roberta-base"
MODEL_TYPE = 'roberta'

# Set loggers
logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger('transformers')
transformers_logger.setLevel(logging.WARNING)

# Input
TRAIN_FILE = sys.argv[1]
VAL_FILE = sys.argv[2]
TEST_FILE = sys.argv[3]

OUTPUT_DIR = sys.argv[4]
BEST_MODEL_DIR = sys.argv[5]

model_args = LanguageModelingArgs()
model_args.reprocess_input_data = True
model_args.num_train_epochs = 7
model_args.dataset_type = 'simple'
model_args.evaluate_during_training=True
model_args.output_dir = '{}/output'.format(OUTPUT_DIR)
model_args.cache_dir = '{}/cache/'.format(OUTPUT_DIR)
model_args.tensorboard_dir = '{}/runs/'.format(OUTPUT_DIR)
model_args.best_model_dir = BEST_MODEL_DIR
model_args.overwrite_output_dir=True
model_args.fp16=False
model_args.use_early_stopping=False
model_args.early_stopping_delta = 2e-5
model_args.early_stopping_patience=3
model_args.evaluate_during_training_steps=1000
model_args.save_eval_checkpoints=False
model_args.tokenizer=tokenizer

model = LanguageModelingModel(
    MODEL_TYPE,
    MODEL_PATH,
    args=model_args,
    cuda_device=1
)

# Train the model
model.train_model(TRAIN_FILE, eval_file=VAL_FILE)

# Validate model
result = model.eval_model(TEST_FILE)
print(result)
print("Model created and saved.")