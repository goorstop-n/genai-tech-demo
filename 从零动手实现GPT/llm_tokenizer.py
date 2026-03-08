import tiktoken
import torch


def load_tokenizer():
    # 加载gpt-2词表；
    tokenizer = tiktoken.get_encoding("gpt2")

    print(f"OpenAI GPT-2中词表有{tokenizer.n_vocab:,}个Token。")

    # print(f"<<< Sample最后10个Token是：")
    # for token_id in range(tokenizer.n_vocab - 10, tokenizer.n_vocab):
    #     print(tokenizer.decode([token_id]), end="\t")
    # print("\n")

    return tokenizer

def text_to_token_tensor(tokenizer, text):
    encoded = tokenizer.encode(text, allowed_special={'<|endoftext|>'})
    encoded_tensor = torch.tensor(encoded).unsqueeze(0)
    return encoded_tensor

def token_tensor_to_text(tokenizer, token_ids):
    flat = token_ids.squeeze(0)
    return tokenizer.decode(flat.tolist())
