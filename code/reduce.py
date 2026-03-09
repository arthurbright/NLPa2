import itertools
from collections import defaultdict, Counter

# Example input: list of (string, count)
import pickle
with open("code/quadline.pickle", 'rb') as f:
    samples = pickle.load(f)
    print(sum([v for v in samples.values()]))
samples = [(k, v) for k, v in samples.items() if len(k) in [3, 4, 5, 6, 7, 8] and v > 12]

import numpy as np
from collections import defaultdict

# -----------------------------
# 1. Input: sampled strings with counts
# -----------------------------
# samples = [
#     ("ABAC", 5),
#     ("BCAC", 3),
#     ("ACAB", 2),
#     # add your data here
# ]

terminals = set()
for s, _ in samples:
    terminals.update(s)
terminals = list(terminals)  # 6 terminals assumed

# -----------------------------
# 2. Define grammar skeleton
# -----------------------------
num_nonterminals = 15
nonterminals = [f"N{i}" for i in range(num_nonterminals)]
start_symbol = "S"  # designate starting symbol

# replace first non-terminal with S
nonterminals[0] = start_symbol

# CNF grammar rules: two types
binary_rules = []
terminal_rules = []

np.random.seed(42)
for nt in nonterminals:
    # terminal rules
    for t in terminals:
        if np.random.rand() < 0.2:
            terminal_rules.append((nt, t, np.random.rand()))
    # binary rules
    for _ in range(2):
        left = np.random.choice(nonterminals)
        right = np.random.choice(nonterminals)
        binary_rules.append((nt, left, right, np.random.rand()))

# Normalize function
def normalize_rules(rules):
    grouped = defaultdict(list)
    for r in rules:
        grouped[r[0]].append(r)
    normed = []
    for nt, group in grouped.items():
        total = sum(r[-1] for r in group)
        if total == 0:  # avoid division by zero
            total = 1.0
        for r in group:
            normed.append(r[:-1] + (r[-1] / total,))
    return normed

terminal_rules = normalize_rules(terminal_rules)
binary_rules = normalize_rules(binary_rules)

# -----------------------------
# 3. Inside algorithm
# -----------------------------
binary_dict = defaultdict(list)
for parent, left, right, prob in binary_rules:
    binary_dict[parent].append((left, right, prob))

terminal_dict = defaultdict(list)
for parent, term, prob in terminal_rules:
    terminal_dict[parent].append((term, prob))

def inside(s):
    n = len(s)
    chart = {nt: np.zeros((n, n)) for nt in nonterminals}
    # terminals
    for i, c in enumerate(s):
        for nt in nonterminals:
            for t, p in terminal_dict.get(nt, []):
                if t == c:
                    chart[nt][i, i] = p
    # binary rules
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            for nt in nonterminals:
                for left, right, p in binary_dict.get(nt, []):
                    for k in range(i, j):
                        chart[nt][i, j] += p * chart[left][i, k] * chart[right][k + 1, j]
    return chart

# -----------------------------
# 4. EM iterations
# -----------------------------
num_iterations = 20
for it in range(num_iterations):
    print(it)
    binary_counts = defaultdict(float)
    terminal_counts = defaultdict(float)
    nt_counts = defaultdict(float)
    
    for s, count in samples:
        n = len(s)
        chart = inside(s)
        total_prob = chart[start_symbol][0, n-1]
        if total_prob == 0:
            continue
        # terminal counts
        for i, c in enumerate(s):
            for nt in nonterminals:
                for t, p in terminal_dict.get(nt, []):
                    if t == c:
                        terminal_counts[(nt, t)] += count * chart[nt][i,i] / total_prob
                        nt_counts[nt] += count * chart[nt][i,i] / total_prob
        # binary counts
        for l in range(2, n + 1):
            for i in range(n - l + 1):
                j = i + l - 1
                for nt in nonterminals:
                    for left, right, p in binary_dict.get(nt, []):
                        sum_split = 0
                        for k in range(i, j):
                            sum_split += chart[left][i,k] * chart[right][k+1,j]
                        binary_counts[(nt, left, right)] += count * p * sum_split / total_prob
                        nt_counts[nt] += count * p * sum_split / total_prob
    # re-estimate probabilities
    for idx, (nt, t, _) in enumerate(terminal_rules):
        prob = terminal_counts[(nt, t)] / nt_counts[nt] if nt_counts[nt] > 0 else 0.0
        terminal_rules[idx] = (nt, t, prob)
    for idx, (nt, l, r, _) in enumerate(binary_rules):
        prob = binary_counts[(nt, l, r)] / nt_counts[nt] if nt_counts[nt] > 0 else 0.0
        binary_rules[idx] = (nt, l, r, prob)
    
    # -----------------------------
    # 5. Remove very low-probability rules and re-normalize
    # -----------------------------
    terminal_rules = [(nt,t,p) for (nt,t,p) in terminal_rules if p > 0.001]
    binary_rules = [(nt,l,r,p) for (nt,l,r,p) in binary_rules if p > 0.001]
    terminal_rules = normalize_rules(terminal_rules)
    binary_rules = normalize_rules(binary_rules)

# -----------------------------
# 6. Print final PCFG
# -----------------------------
print("Learned PCFG with start symbol S:")
for nt, t, p in terminal_rules:
    print(f"{nt} -> {t} [p={p:.3f}]")
for nt, l, r, p in binary_rules:
    print(f"{nt} -> {l} {r} [p={p:.3f}]")
print(len(binary_rules))


import random
from collections import defaultdict

# -----------------------------
# 1. Build dictionaries for fast sampling
# -----------------------------
# terminal_rules and binary_rules are outputs from the EM PCFG
# Format: terminal_rules = [(nt, t, p), ...], binary_rules = [(nt, l, r, p), ...]

term_dict = defaultdict(list)
for nt, t, p in terminal_rules:
    term_dict[nt].append((t, p))

bin_dict = defaultdict(list)
for nt, l, r, p in binary_rules:
    bin_dict[nt].append((l, r, p))

# helper: choose one option weighted by probabilities
def weighted_choice(options):
    items, weights = zip(*options)
    return random.choices(items, weights=weights, k=1)[0]

# -----------------------------
# 2. Recursive sampling function
# -----------------------------
def sample(nt="S"):
    # terminal rule?
    if nt in term_dict and (nt not in bin_dict or random.random() < 0.5):
        t = weighted_choice(term_dict[nt])
        return t
    # binary rule
    if nt in bin_dict:
        l, r = weighted_choice([(l, r, p) for l, r, p in bin_dict[nt]])
        return sample(l) + sample(r)
    # fallback: if no rule exists, pick terminal if possible
    if nt in term_dict:
        return weighted_choice(term_dict[nt])
    return ""  # empty string fallback

# -----------------------------
# 3. Generate N samples
# -----------------------------
N = 10
for _ in range(N):
    s = sample("S")
    print(s)