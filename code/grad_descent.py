import torch
import torch.nn as nn
import torch.nn.functional as F

class CNFPCFG(nn.Module):
    def __init__(self, R, vocab):
        super().__init__()
        self.R = R
        self.vocab = vocab
        
        # Binary rule logits: [X,Y,Z]
        self.binary_logits = nn.Parameter(
            torch.randn(R, R, R) * 0.01
        )
        
        # Start distribution
        self.start_logits = nn.Parameter(
            torch.randn(R)
        )
        
        # Terminal emission matrix (fixed identity)
        self.terminals = torch.eye(len(vocab))

    def binary_rules(self):
        # shape: [R, R, R]
        probs = F.softmax(
            self.binary_logits.view(self.R, -1),
            dim=-1
        )
        return probs.view(self.R, self.R, self.R)

    def start_probs(self):
        return F.softmax(self.start_logits, dim=-1)

    def inside(self, string):
        if len(string) == 0:
            return 0
        n = len(string)
        R = self.R
        rules = self.binary_rules()
        
        # Chart: [i, j, X]
        chart = torch.zeros(n, n, R)
        
        # Base case (length 1)
        for i, token in enumerate(string):
            chart[i, i, token] = 1.0  # preterminal assumption
        
        # Dynamic program
        for span in range(2, n+1):
            for i in range(n-span+1):
                j = i + span - 1
                val = torch.zeros(R, device=chart.device)

                for k in range(i, j):
                    left = chart[i, k].clone()
                    right = chart[k+1, j].clone()
                    
                    # X -> YZ
                    # contraction
                    contrib = torch.einsum(
                        "xyz,y,z->x",
                        rules,
                        left,
                        right
                    )
                    val = val + contrib
                chart[i,j] = val

        
        start = self.start_probs()
        # print(string, torch.dot(start, chart[0, n-1]))
        return torch.dot(start, chart[0, n-1])
    
    def next_token_dist(self, prefix, vocab):
        base_prob = self.inside(prefix)
        
        probs = []
        for token in range(len(vocab)):
            extended = prefix + [token]
            p = self.inside(extended)
            probs.append(p / base_prob)
            
        probs = torch.stack(probs)
        return probs / probs.sum()

def train(model: CNFPCFG, sample_prefixes_fn, probs_fn, vocab, epochs=500, lr=1e-2):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(epochs):
        loss = 0.0
        
        # sample prefixes from transformer
        print("sampling prefixes...")
        prefixes = sample_prefixes_fn()
        
        print("computing loss...")
        ii = 0
        for prefix in prefixes:
            ii += 1
            # print(ii)
            true_dist = probs_fn(prefix)  # dict
            # true_dist = {i: 1/26 for i in range(26)}

            true_probs = torch.tensor(
                [true_dist[v] for v in vocab]
            )
            pred_probs = model.next_token_dist(prefix, vocab)
            log_pred = torch.log_softmax(pred_probs, dim=-1)

            loss = loss + F.kl_div(
                log_pred,
                true_probs,
                reduction='batchmean'
            )
        
        print("backwarding")
        opt.zero_grad()
        loss.backward()
        opt.step()
        
        if epoch % 1 == 0:
            print("epoch", epoch, "loss", loss.item())