import torch
from torch.utils.data import Dataset

class LlmDs(Dataset):
    """
    自定义LLM dataset，使用滑动窗口对数据进行采样.
    一般定义stride = context_length.
    """
    def __init__(self, text, tokenizer, context_length, stride):
        self.input_ids = []   # input tensor；
        self.target_ids = []   # target tensor;

        token_ids = tokenizer.encode(text)

        for i in range(0, len(token_ids) - context_length, stride):
            # 输入Token序列；
            self.input_ids.append(torch.tensor(token_ids[i : i + context_length]))
            # 目标Token序列，输入Token序列右移一个位置；
            self.target_ids.append(torch.tensor(token_ids[i + 1 : i + context_length + 1]))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.target_ids[idx]