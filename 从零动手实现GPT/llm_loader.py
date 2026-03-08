from torch.utils.data import DataLoader

from 从零动手实现GPT.llm_ds import LlmDs


def load_llm_ds(file_path, tokenizer, train_ratio, context_length, stride, batch_size):
    """
    加载大语言模型训练数据集，这里同时支持生成训练集和验证集；
    当传递train=True，代表获取训练集，如果train=False，代表获取验证集；

    :param file_path: 训练数据文件路径；
    :param tokenizer: 分词器；
    :param train_ratio: 训练集占比；
    :param context_length: 最大上下文长度；
    :param stride: 构造数据集时的窗口偏移大小，一般等于context_length；
    :param batch_size: 批次大小；
    :return: Pytorch DataLoader；
    """

    # 加载训练数据；
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    # 基于train_ratio将数据划分为训练集和验证集；
    split_idx = int(train_ratio * len(raw_text))
    train_text = raw_text[:split_idx]
    validate_text = raw_text[split_idx:]

    train_dataset = LlmDs(train_text, tokenizer, context_length=context_length, stride=stride)
    validate_dataset = LlmDs(validate_text, tokenizer, context_length=context_length, stride=stride)

    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=0)
    validate_loader = DataLoader(
        dataset=validate_dataset,
        batch_size=batch_size,
        shuffle=False,
        drop_last=False,
        num_workers=0)

    return train_loader, validate_loader