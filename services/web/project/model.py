import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pickle


class FrustrationBert(torch.nn.Module):
    def __init__(self, pretrained="DeepPavlov/rubert-base-cased-conversational", device='cpu'):
        super(FrustrationBert, self).__init__()
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained(pretrained)
        self.encoder = BertForSequenceClassification.from_pretrained(pretrained)
        self.encoder.to(self.device)

        self.softm = torch.nn.Softmax(dim=-1)

    def forward(self, texts):
        encodings = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)
        output = self.encoder(input_ids, attention_mask=attention_mask)
        return output['logits']

    def predict(self, texts, return_labels=False):
        logits = self.forward(texts).detach()
        preds = torch.argmax(logits, -1).tolist()
        if not return_labels:
            return preds
        else:
           return ['frustrated' if pred==1 else 'normal' for pred in preds ]

    def predict_probas(self, texts):
        logits = self.forward(texts).detach()
        return self.softm(logits)

    def load_saved(self, path):
        state_dict = torch.load(path, map_location=self.device)
        self.load_state_dict(state_dict)


class MyCustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "__main__":
            module = "project.model"
        return super().find_class(module, name)


with open("project/model_cpu.pickle", 'rb') as f:
    unpickler = MyCustomUnpickler(f)
    frustration_model = unpickler.load()