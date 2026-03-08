import torch
from torch import nn


class Conv1D(nn.Module):
    """
    这里沿用了GPT-2中的实现，
    GPT-2里的Conv1D实际上就是Linear层；
    名字来源于早期把 1×1 Conv1D 当作线性投影的历史实现习惯。

    另外这里有个点需要注意下：
    如果我们把这里换成Linear实现，那么这里Weight其实是Weight的Transpose转置，是和GPT-2实现是有差异的。
    """
    def __init__(self, d_in, d_out):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(d_in, d_out))
        self.bias = nn.Parameter(torch.zeros(d_out))

    def forward(self, x):
        return torch.matmul(x, self.weight) + self.bias

class MaskedMultiHeadAttention(nn.Module):
    """
    基于Masked的多Multi-Head Self-Attention机制实现；
    """
    def __init__(self, emb_dim, dropout, num_heads):
        super().__init__()
        assert emb_dim % num_heads == 0

        self.num_heads = num_heads
        self.head_dim = emb_dim // num_heads

        # 参考gpt实现，初始化了一个组合了Q，K，V和Multi-Head的更大的Matrix；
        self.c_attn = Conv1D(emb_dim, 3 * emb_dim)

        # output projection
        # 这个输出投影层并不是必需的，但它在许多大语言模型架构中被广泛使用；
        # 这就是我们在这里添加它以保持完整性的原因。
        self.c_proj = nn.Linear(emb_dim, emb_dim)

        # dropout；
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x):
        # batch_size、context_length、emb_dim；
        B, T, C = x.size()

        # qkv projection
        # [B, T, 3*C]
        qkv = self.c_attn(x)
        # [B, T, C]
        q, k, v = qkv.split(C, dim=2)

        # reshape to heads
        # shape: [B, T, heads, head_dim] ---> [B, heads, T, head_dim]
        q = q.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)

        # scaled dot-product attention
        att = (q @ k.transpose(2, 3)) / (self.head_dim ** 0.5)

        # causal mask
        mask = torch.tril(torch.ones(T, T, device=x.device)).view(1, 1, T, T)
        att = att.masked_fill(mask == 0, float('-inf'))

        att = torch.softmax(att, dim=-1)
        att = self.attn_dropout(att)

        # attention * values
        # shape: [B, heads, T, head_dim]
        y = att @ v

        # reshape back -> [B, T, C]
        y = y.transpose(1, 2).contiguous().view(B, T, C)

        # output projection
        # shape: [batch_size, context_length, emb_dim]
        y = self.resid_dropout(self.c_proj(y))

        return y

class GELU(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return 0.5 * x * (1 + torch.tanh(
            torch.sqrt(torch.tensor(2 / torch.pi)) * (x + 0.044715 * torch.pow(x, 3))))

class FeedForward(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        hidden_dim = 4 * emb_dim
        self.c_fc = Conv1D(emb_dim, hidden_dim)
        self.act = GELU()
        self.c_proj = Conv1D(hidden_dim, emb_dim)

    def forward(self, x):
        return self.c_proj(self.act(self.c_fc(x)))

class LayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps=1e-5):
        super().__init__()

        self.eps = eps
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        var = x.var(-1, keepdim=True, unbiased=False)
        x_norm = (x - mean) / (torch.sqrt(var + self.eps))
        return x_norm * self.weight + self.bias

class TransformerBlock(nn.Module):
    def __init__(self, emb_dim, dropout, n_heads):
        super().__init__()
        # Attention前LayerNorm1;
        self.ln_1 = LayerNorm(emb_dim)

        # Self-Attention权重；
        # 这里包括c_attn和c_proj；
        self.attn = MaskedMultiHeadAttention(
            emb_dim=emb_dim,
            dropout=dropout,
            num_heads=n_heads,
        )

        # FeedForward前LayerNorm2；
        self.ln_2 = LayerNorm(emb_dim)

        # MLP(FeedForward网络)；
        # 这里包括c_fc和c_proj；
        self.mlp = FeedForward(emb_dim)

        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x):
        resid = x
        x = self.ln_1(x)
        x = self.attn(x)
        x = self.resid_dropout(x)
        x = x + resid # residual connection

        resid = x
        x = self.ln_2(x)
        x = self.mlp(x)
        x = self.resid_dropout(x)
        x = x + resid # residual connection

        return x

class Transformer(nn.Module):
    def __init__(self, vocab_size, context_length, emb_dim, dropout, n_heads, n_layers):
        super().__init__()
        # word token embedding
        # shape：[vocab_size, hidden_dim]
        self.wte = nn.Embedding(vocab_size, emb_dim)

        # word position embedding
        # shape：[context_length, hidden_dim]
        self.wpe = nn.Embedding(context_length, emb_dim)

        self.dropout = nn.Dropout(dropout)

        # transformer blocks，对于small 124M 模型包括12层；
        self.h = nn.Sequential(
            *[TransformerBlock(emb_dim, dropout, n_heads)
              for _ in range(n_layers)])

        # Transformer最后的LayerNorm；
        self.ln_f = nn.LayerNorm(emb_dim)

    def forward(self, inputs):
        device = inputs.device

        B, T = inputs.size()

        te = self.wte(inputs)
        pe = self.wpe(torch.arange(T, device=device))
        x = te + pe

        x = self.dropout(x)
        x = self.h(x)
        x = self.ln_f(x)

        return x

class GPT(nn.Module):
    def __init__(
            self,
            vocab_size, context_length, emb_dim, dropout,
            n_heads, n_layers):
        """
        :param vocab_size: 词表长度；
        :param context_length: 模型支持的最长上下文；
        :param emb_dim: wte和wpe Embedding维度；
        :param dropout: dropout比例；
        :param n_heads: 模型自注意力头的数量；
        :param n_layers: 模型中Transformer Block的数量；
        """
        super().__init__()
        self.transformer = Transformer(
            vocab_size, context_length, emb_dim, dropout,
            n_heads, n_layers)

        # 输出层权重，GPT-2中使用权重共享，transformer.wte.weight；
        # 将emb_dim维度投影到vocab_size维度，输出即为对应词表中各个Token的概率分布；
        self.lm_head = nn.Linear(emb_dim, vocab_size, bias=False)
        self.lm_head.weight = self.transformer.wte.weight

    def forward(self, inputs):
        x = self.transformer(inputs)
        logits = self.lm_head(x)
        return logits