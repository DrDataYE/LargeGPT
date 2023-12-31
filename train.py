import torch
import torch.nn as nn
from torch.nn import functional as F
import datetime
from utils import encode, decode, vocab_size, text

from rich.console import Console

console = Console()
import argparse

# ... (الكود السابق)

parser = argparse.ArgumentParser(description='Hyperparameters Configuration')

# Hyperparameters
parser.add_argument('--batch_size', type=int, default=16, help='Batch size for training')
parser.add_argument('--block_size', type=int, default=32, help='Maximum context length for predictions')
parser.add_argument('--max_iters', type=int, default=1000, help='Maximum number of training iterations')
parser.add_argument('--eval_interval', type=int, default=100, help='Interval for evaluation')
parser.add_argument('--learning_rate', type=float, default=1e-3, help='Learning rate')
parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu', help='Device for training (cuda or cpu)')
parser.add_argument('--eval_iters', type=int, default=200, help='Number of iterations for evaluation')
parser.add_argument('--n_embd', type=int, default=512, help='Number of embedding dimensions')
parser.add_argument('--n_head', type=int, default=8, help='Number of attention heads')
parser.add_argument('--n_layer', type=int, default=6, help='Number of layers in the model')
parser.add_argument('--dropout', type=float, default=0.1, help='Dropout rate')

args = parser.parse_args()

# ... (الكود السابق)

batch_size = args.batch_size
block_size = args.block_size
max_iters = args.max_iters
eval_interval = args.eval_interval
learning_rate = args.learning_rate
device = args.device
eval_iters = args.eval_iters
n_embd = args.n_embd
n_head = args.n_head
n_layer = args.n_layer
dropout = args.dropout
# hyperparameters
# batch_size = 16  # how many independent sequences will we process in parallel?
# block_size = 32  # what is the maximum context length for predictions?
# max_iters = 1000
# eval_interval = 100
# learning_rate = 1e-3
# device = 'cuda' if torch.cuda.is_available() else 'cpu'  # or tpu
# eval_iters = 200
# n_embd = 512  # زيادة عدد الوحدات لتعزيز القدرة التعبيرية
# n_head = 8   # زيادة عدد الرؤوس لتحسين التعامل مع السياقات المتعددة
# n_layer = 6  # زيادة عدد الطبقات لتعميق النموذج
# dropout = 0.1  # زيادة قليلة في الانخراط (Dropout) لتقليل الزيادة الجدية
# ------------

torch.manual_seed(1337)


# Train and test splits
data = torch.tensor(encode(text), dtype=torch.long)
n = int(0.9*len(data))  # first 90% will be train, rest val
train_data = data[:n]
val_data = data[n:]

# data loading


def get_batch(split):
    # generate a small batch of data of inputs x and targets y
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y


@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


def save_model(model):
    torch.save(model.state_dict(), 'trained_model.bin')





class Head(nn.Module):
    """ one head of self-attention """

    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(
            torch.ones(block_size, block_size)))

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)   # (B,T,C)
        q = self.query(x)  # (B,T,C)
        # compute attention scores ("affinities")
        # (B, T, C) @ (B, C, T) -> (B, T, T)
        wei = q @ k.transpose(-2, -1) * C**-0.5
        wei = wei.masked_fill(
            self.tril[:T, :T] == 0, float('-inf'))  # (B, T, T)
        wei = F.softmax(wei, dim=-1)  # (B, T, T)
        wei = self.dropout(wei)
        # perform the weighted aggregation of the values
        v = self.value(x)  # (B,T,C)
        out = wei @ v  # (B, T, T) @ (B, T, C) -> (B, T, C)
        return out


class MultiHeadAttention(nn.Module):
    """ multiple heads of self-attention in parallel """

    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.dropout(self.proj(out))
        return out


class FeedFoward(nn.Module):
    """ a simple linear layer followed by a non-linearity """

    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    """ Transformer block: communication followed by computation """

    def __init__(self, n_embd, n_head):
        # n_embd: embedding dimension, n_head: the number of heads we'd like
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedFoward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

# super simple bigram model


class BigramLanguageModel(nn.Module):

    def __init__(self):
        super().__init__()
        # each token directly reads off the logits for the next token from a lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(
            *[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)  # final layer norm
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape

        # idx and targets are both (B,T) tensor of integers
        tok_emb = self.token_embedding_table(idx)  # (B,T,C)
        pos_emb = self.position_embedding_table(
            torch.arange(T, device=device))  # (T,C)
        x = tok_emb + pos_emb  # (B,T,C)
        x = self.blocks(x)  # (B,T,C)
        x = self.ln_f(x)  # (B,T,C)
        logits = self.lm_head(x)  # (B,T,vocab_size)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def generate(self, idx, max_new_tokens, temperature=0.7):
        # idx is (B, T) array of indices in the current context
        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_cond = idx[:, -block_size:]
            # get the predictions with adjusted temperature
            logits, loss = self(idx_cond)
            # focus only on the last time step
            logits = logits[:, -1, :]  # becomes (B, C)
            # apply softmax with adjusted temperature to get probabilities
            probs = F.softmax(logits / temperature, dim=-1)  # (B, C)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1)  # (B, 1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1)  # (B, T+1)
        return idx

model = BigramLanguageModel()
m = model.to(device)
def train():
    
    console.print("Device :",device,justify="center")
    
    # print the number of parameters in the model
    console.print(sum(p.numel() for p in m.parameters())/1e6, 'M parameters', sep="", style="bold",justify='center')

    # create a PyTorch optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    with console.status("[bold]Training ...", spinner='aesthetic') as status:
        for iter in range(max_iters):
            # every once in a while evaluate the loss on train and val sets
            if iter % eval_interval == 0 or iter == max_iters - 1:
                losses = estimate_loss()
                console.print(
                    f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f} time:{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # sample a batch of data
            xb, yb = get_batch('train')

            # evaluate the loss
            logits, loss = model(xb, yb)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

    console.print("Done Training!",style="bold")
    # Save the trained model in binary format
    save_model(model)
    console.print("Done Save the Model",style="bold")

# train()

def chat(user_input: str, max_new_tokens=2000, temperature=0.7):

    # Encode the user input to the tensor format expected by the model
    input_tensor = torch.tensor(
        encode(user_input), dtype=torch.long, device=device).unsqueeze(0)

    # Adjust the temperature parameter to control the diversity of the generated text
    temperature = 0.7  # You can experiment with different temperature values

    generated_tensor = m.generate(
        input_tensor, max_new_tokens=max_new_tokens, temperature=temperature)[0]

    # Convert the generated tensor back to text
    generated_text = decode(generated_tensor.tolist())

    return generated_text

