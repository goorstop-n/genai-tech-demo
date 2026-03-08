import hydra
from omegaconf import DictConfig
from transformers import GPT2LMHeadModel

from 从零动手实现GPT.gpt import GPT
from 从零动手实现GPT.llm_generator import generate_text, get_device
from 从零动手实现GPT.llm_tokenizer import load_tokenizer, text_to_token_tensor, token_tensor_to_text


@hydra.main(config_path='configs', config_name='config', version_base=None)
def main(cfg: DictConfig):
    # 加载Tokenizer；
    tokenizer = load_tokenizer()

    gpt = GPT(
        vocab_size=tokenizer.n_vocab, # 50,257
        context_length=cfg.context_length,
        emb_dim=cfg.emb_dim,
        dropout=cfg.dropout,
        n_heads=cfg.n_heads,
        n_layers=cfg.n_layers,).to(get_device())

    # 加载huggingface的gpt-2预训练权重；
    hf_gpt2 = GPT2LMHeadModel.from_pretrained("gpt2")
    gpt.load_state_dict(hf_gpt2.state_dict())

    # 看下模型进行文字接龙的输出；
    prompt = "Hello, I'm a language model,"
    input = text_to_token_tensor(tokenizer, prompt)
    output = generate_text(
        model=gpt,
        idx=input,
        max_tokens=50,
        context_length=cfg.context_length,
        temperature=1.5,
        top_k=10
    )
    print(f"Input Prompt: {prompt}\nOutput: {token_tensor_to_text(tokenizer, output)})")


if __name__ == "__main__":
    main()