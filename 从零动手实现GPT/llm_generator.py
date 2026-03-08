import torch


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    return torch.device('cpu')

def generate_text(model, idx,
        max_tokens, context_length, temperature=0.0, top_k=None,
        eos_id=None
):
    """
    大语言模型的自回归文本生成实现；
    根据输入的Token序列，一次预测一个新的Token，并不对追到到输入生成新的Token；

    :param model: 大语言模型；
    :param idx: 输入Token序列；
    :param max_tokens: 最多生成多少个Token；
    :param context_length: 模型最大上下文；
    :param temperature: 采样温度；
    :param top_k: top-k sampling；
    :param eos_id: 结束Token；
    :return: 生成内容；
    """
    idx = idx.to(get_device())

    # 最大支持max_tokens个Token输出；
    for _ in range(max_tokens):
        # 截取上下文窗口；
        idx_cond = idx[:, -context_length:]
        with torch.no_grad():
            # shape：[B, T, C]
            logits = model(idx_cond)

        # 只取最后一个Token的预测结果；
        logits = logits[:, -1, :]

        # Top-K采样；
        if top_k is not None:
            top_logits, _ = torch.topk(logits, top_k)
            min_val = top_logits[:, -1]
            # 只保留Top-K的Token，将小于min_val的设置为-inf，这样在计算Softmax的时候置为0；
            logits = torch.where(
                logits < min_val,
                torch.tensor(float("-inf"), device=logits.device),
                logits)

        # Temperature采样；
        if temperature > 0.0:
            logits = logits / temperature
            probs = torch.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
        else:
            idx_next = torch.argmax(logits, dim=-1, keepdim=True)

        if idx_next == eos_id:
            break

        idx = torch.cat((idx, idx_next), dim=1)
    return idx