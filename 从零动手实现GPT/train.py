import os

import hydra
import torch
from omegaconf import DictConfig
from torch import nn
from tqdm import tqdm
from matplotlib import pyplot as plt

from 从零动手实现GPT import gpt
from 从零动手实现GPT.gpt import GPT
from 从零动手实现GPT.llm_generator import generate_text, get_device
from 从零动手实现GPT.llm_loader import load_llm_ds
from 从零动手实现GPT.llm_tokenizer import load_tokenizer, text_to_token_tensor, token_tensor_to_text

# One epoch training for dataloader...
def train(dataloader, model, loss_fn, optimizer, device):
    model.train()

    running_loss = 0.0
    for inputs, targets in tqdm(dataloader, desc="Training", leave=False):
        inputs, targets = inputs.to(device), targets.to(device)
        outputs = model(inputs)

        # 只针对llm，初始inputs、targets、outputs维度为：
        # torch.Size([2, 256]) torch.Size([2, 256]) torch.Size([2, 256, 50257])
        outputs = outputs.flatten(0, 1)
        targets = targets.flatten(0, 1)

        loss = loss_fn(outputs, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
    epoch_loss = running_loss / len(dataloader.dataset)

    return epoch_loss

# Validating for dataloader...
def validate(dataloader, model, loss_fn, device):
    model.eval()

    validate_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for inputs, targets in tqdm(dataloader, desc="Validate", leave=False):
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)

            # 只针对llm，初始inputs、targets、outputs维度为：
            # torch.Size([2, 256]) torch.Size([2, 256]) torch.Size([2, 256, 50257])
            outputs = outputs.flatten(0, 1)
            targets = targets.flatten(0, 1)

            loss = loss_fn(outputs, targets)

            validate_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    validate_loss = validate_loss / len(dataloader.dataset)
    validate_accuracy = correct / total

    return validate_loss, validate_accuracy

def draw_model_train_curves(root, train_losses, val_losses, val_accuracies):
    plt.figure(figsize=(12, 5))

    # Loss subplot
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.title("Loss Curves")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    # Accuracy subplot
    plt.subplot(1, 2, 2)
    plt.plot(val_accuracies, label="Validation Accuracy")
    plt.title("Accuracy Curves")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy (%)")
    plt.legend()

    plt.tight_layout()
    fig_path = os.path.join(root, "train_curves.png")
    plt.savefig(fig_path)
    plt.close()

    return fig_path

@hydra.main(config_path='configs', config_name='config', version_base=None)
def main(cfg: DictConfig):
    # 加载Tokenizer；
    tokenizer = load_tokenizer()

    # 加载数据；
    train_loader, validate_loader = load_llm_ds(
        file_path="data/the-verdict.txt",
        tokenizer=tokenizer,
        train_ratio=0.9,
        context_length=cfg.context_length,
        stride=cfg.context_length,
        batch_size=1,
    )
    print(f"数据加载完成，训练集包括{len(train_loader)}个batch, 验证集包括{len(validate_loader)}个batch。")

    # 1. 写出一个带有未知参数的函数；
    gpt = GPT(
        vocab_size=tokenizer.n_vocab, # 50,257
        context_length=cfg.context_length,
        emb_dim=cfg.emb_dim,
        dropout=cfg.dropout,
        n_heads=cfg.n_heads,
        n_layers=cfg.n_layers,).to(get_device())

    # total_params = sum(p.numel() for p in gpt.parameters())
    # print(f"GPT's total num of parameters: {total_params:,}.")

    # 在Pre-train前，先看下模型进行文字接龙的输出；
    prompt = "Who are you?"
    input = text_to_token_tensor(tokenizer, prompt)
    output = generate_text(
        model=gpt,
        idx=input,
        max_tokens=50,
        context_length=cfg.context_length,
    )
    print(f"Input Prompt: {prompt}\nOutput: {token_tensor_to_text(tokenizer, output)})")

    # 2. 定义一个Loss；
    loss = nn.CrossEntropyLoss()

    # 3. 求解一个Optimize的问题；
    optimizer = torch.optim.AdamW(gpt.parameters(), lr=0.0004, weight_decay=0.1)
    epochs = 500
    best_accuracy = 0.0
    train_losses, val_losses, val_accuracies = [], [], []
    for epoch in range(1, epochs + 1):
        print(
            '[*] Epoch【{:0{width}d}/{}】training start...'.format(
                epoch, epochs, width=len(str(epochs))))
        train_loss = train(train_loader, gpt, loss, optimizer, get_device())
        validation_loss, validate_accuracy = validate(validate_loader, gpt, loss, get_device())
        print("[*] Train loss: {:.4f}, Validation loss: {:.4f}, Validate accuracy: {:.4f}".format(
            train_loss, validation_loss, validate_accuracy))

        if validate_accuracy >= best_accuracy:
            best_accuracy = validate_accuracy
        train_losses.append(train_loss)
        val_losses.append(validation_loss)
        val_accuracies.append(validate_accuracy)

    draw_model_train_curves("./outputs", train_losses, val_losses, val_accuracies)
    print("[*] Training done! Best Validation Accuracy: {:.4f}".format(best_accuracy))

    # 在Pre-train后，看下模型进行文字接龙的输出；
    prompt = "How it happened?"
    input = text_to_token_tensor(tokenizer, prompt)
    output = generate_text(
        model=gpt,
        idx=input,
        max_tokens=50,
        context_length=cfg.context_length,
    )
    print(f"Input Prompt: {prompt}\nOutput: {token_tensor_to_text(tokenizer, output)})")


if __name__ == "__main__":
    main()