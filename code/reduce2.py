import itertools
import math
from collections import defaultdict

def js_divergence(p, q):
    keys = set(p) | set(q)
    m = {k: (p.get(k,0)+q.get(k,0))/2 for k in keys}
    def kl(a,b):
        s=0
        for k in keys:
            if a.get(k,0) > 0:
                s += a[k]*math.log(a[k]/b[k])
        return s
    return (kl(p,m)+kl(q,m))/2

# Build automaton from binary rules
def build_automaton(rules):
    transitions = defaultdict(dict)
    terminals = set()
    for A,B,C,p in rules:
        if C is not None and B.startswith("T_"):
            x = B[2:]
            transitions[A][x] = (C,p)
            terminals.add(x)
    return transitions, terminals

# Compute k-step distributions recursively
def k_step_distribution(transitions, k):
    # returns dict: state -> dict of terminal sequences -> probability
    dist = {}
    for s in transitions:
        dist[s] = defaultdict(float)
        queue = [("",1.0,s)]
        while queue:
            seq, prob, state = queue.pop(0)
            if len(seq) == k:
                dist[s][seq] += prob
            else:
                for x,(t,p) in transitions.get(state, {}).items():
                    queue.append((seq+x, prob*p, t))
    return dist

# Merge states based on distributions
def merge_states(transitions, dist, threshold):
    states = list(transitions.keys())
    while True:
        best = None
        best_d = float("inf")
        for i in range(len(states)):
            for j in range(i+1,len(states)):
                s1 = states[i]
                s2 = states[j]
                d = js_divergence(dist[s1], dist[s2])
                if d < best_d:
                    best_d = d
                    best = (s1,s2)
        if best is None or best_d > threshold:
            break
        s1,s2 = best
        # merge s2 into s1
        for x,(t,p) in transitions[s2].items():
            if x in transitions[s1]:
                t1,p1 = transitions[s1][x]
                transitions[s1][x] = (t1,p1+p)
            else:
                transitions[s1][x] = (t,p)
        del transitions[s2]
        states.remove(s2)
        # redirect incoming edges
        for s in transitions:
            for x,(t,p) in list(transitions[s].items()):
                if t == s2:
                    transitions[s][x] = (s1,p)
        # recompute distribution after merge
        dist = k_step_distribution(transitions, len(next(iter(dist.values()))))
    return transitions

# Normalize probabilities
def normalize_transitions(transitions):
    for s in transitions:
        total = sum(p for _,p in transitions[s].values())
        for x,(t,p) in transitions[s].items():
            transitions[s][x] = (t,p/total)

# Convert automaton to binary PCFG rules
def automaton_to_pcfg(transitions, terminals):
    rules = []
    for A in transitions:
        for x,(B,p) in transitions[A].items():
            T = "T_"+x
            rules.append((A,T,B,p))
    for x in terminals:
        rules.append(("T_"+x,x,None,1.0))
    return rules

# Hierarchical compression: 3-char, 2-char, then 1-char
def compress_pcfg_hierarchical(rules, thresholds=(0.02,0.02,0.02)):
    transitions, terminals = build_automaton(rules)
    # Step 1: 3-char
    print("getting dist")
    dist3 = k_step_distribution(transitions, 3)
    print("merging")
    transitions = merge_states(transitions, dist3, thresholds[0])
    # Step 2: 2-char
    dist2 = k_step_distribution(transitions, 2)
    transitions = merge_states(transitions, dist2, thresholds[1])
    # Step 3: 1-char
    dist1 = k_step_distribution(transitions, 1)
    transitions = merge_states(transitions, dist1, thresholds[2])
    # Normalize
    normalize_transitions(transitions)
    return automaton_to_pcfg(transitions, terminals)

# ===========
rules = []
with open('pcfg3_post.csv', 'r') as f:
    ii = -1
    for line in f:
        ii += 1
        if ii == 0: continue
        line = line.split(",")
        # print(line)
        if line[2] == 'nonterminal':
            next = line[3].split()
            rules.append((line[1], next[0], next[1], float(line[4])))

print(len(rules))
compressed_rules = compress_pcfg_hierarchical(rules, thresholds=(0.02, 0.02, 0.02))
print(compressed_rules, len(compressed_rules))

id = 60

with open('pcfg3_scratch.csv', 'w') as w:
    with open('pcfg3_pre.csv', 'r') as f:
        for line in f:
            w.write(line)
    
    for r in rules:
        id += 1
        w.write(f"{id},{r[0]},nonterminal,{r[1]} {r[2]},{r[3]}\n")