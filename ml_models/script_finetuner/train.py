from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def train_model(feedback_data):
    inputs = tokenizer(feedback_data, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss
    loss.backward()
    model.save_pretrained("ml_models/script_finetuner/model")
