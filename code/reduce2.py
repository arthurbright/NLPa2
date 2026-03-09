import math
from collections import defaultdict, deque

# ---- JS divergence ----
def js_divergence(p,q):
    keys = set(p)|set(q)
    m = {k:(p.get(k,0)+q.get(k,0))/2 for k in keys}
    def kl(a,b):
        s=0
        for k in keys:
            if a.get(k,0)>0:
                s += a[k]*math.log(a[k]/b[k])
        return s
    return (kl(p,m)+kl(q,m))/2

# ---- Build automaton ----
def build_automaton(rules):
    transitions = defaultdict(dict)
    terminals = set()
    for A,B,C,p in rules:
        if C is not None and B.startswith("T_"):
            x = B[2:]
            transitions[A][x] = (C,p)
            terminals.add(x)
    return transitions, terminals

# ---- Compute suffix distributions of length k with offset ----
def suffix_distributions(transitions, k, offset=0):
    """
    offset=0: right-aligned suffix (end of sequence)
    offset>0: shifted window to the left
    returns: dict state -> dict(suffix string -> probability)
    """
    dist = {}
    for s in transitions:
        dist[s] = defaultdict(float)
        queue = deque()
        queue.append(("",1.0,s))
        while queue:
            seq, prob, state = queue.popleft()
            if len(seq) == k + offset:
                # take the window slice
                key = seq[offset:] if offset>0 else seq
                dist[s][key] += prob
            else:
                for x,(t,p) in transitions.get(state, {}).items():
                    queue.append((seq+x, prob*p, t))
    return dist

# ---- Merge two states into a new nonterminal ----
def merge_pair(transitions, s1, s2, next_nt_id):
    new_nt = f"M{next_nt_id}"
    next_nt_id += 1
    # combine outgoing transitions
    transitions[new_nt] = {}
    for x,(t,p) in transitions[s1].items():
        if t != s1 and t != s2:
            transitions[new_nt][x] = (t,p)
    for x,(t,p) in transitions[s2].items():
        if t != s1 and t != s2:
            if x in transitions[new_nt]:
                t0,p0 = transitions[new_nt][x]
                transitions[new_nt][x] = (t0,p0+p)
            else:
                transitions[new_nt][x] = (t,p)
    # redirect incoming edges from OTHER states only
    for s in transitions:
        if s==s1 or s==s2:
            continue
        for x,(t,p) in list(transitions[s].items()):
            if t==s1 or t==s2:
                transitions[s][x] = (new_nt,p)
    # remove old states
    del transitions[s1]
    del transitions[s2]
    return new_nt, next_nt_id

next_nt_id = 0
# ---- Sliding suffix merge ----
def sliding_suffix_merge(rules, thresholds=(0.05,0.05,0.05)):
    global next_nt_id
    transitions, terminals = build_automaton(rules)

    # Define window offsets: 0=right-aligned, 1=shift left by 1, 2=shift left by 2
    offsets = [0,1,2]

    for window_len, threshold in zip([3,2,1], thresholds):
        for offset in offsets:
            merged = True
            while merged:
                merged = False
                dist = suffix_distributions(transitions, window_len, offset)
                states = list(transitions.keys())
                n = len(states)
                for i in range(n):
                    for j in range(i+1,n):
                        s1,s2 = states[i],states[j]
                        d = js_divergence(dist[s1], dist[s2])
                        if d <= threshold:
                            new_nt, next_nt_id = merge_pair(transitions,s1,s2,next_nt_id)
                            merged = True
                            break
                    if merged:
                        break

    return transitions, terminals

# ---- Convert automaton back to binary PCFG ----
def automaton_to_pcfg(transitions, terminals):
    rules = []
    for A in transitions:
        for x,(B,p) in transitions[A].items():
            rules.append((A,f"T_{x}",B,p))
    # for t in terminals:
    #     rules.append((f"T_{t}",t,None,1.0))
    return rules




# ===========
rules = []
with open('pcfg_mock.csv', 'r') as f:
    for line in f:
        line = line.split(",")
        # print(line)
        if line[2] == 'nonterminal':
            _next = line[3].split()
            rules.append((line[1], f'T_{_next[0][0]}', _next[1], float(line[4])))

print(len(rules))

transitions, terminals = sliding_suffix_merge(rules, thresholds=(0.02,0.02,0.02))
compressed = automaton_to_pcfg(transitions, terminals)

print(len(compressed))

transitions, terminals = sliding_suffix_merge(compressed, thresholds=(0.02,0.02,0.02))
compressed = automaton_to_pcfg(transitions, terminals)

for r in compressed:
    print(r)

print(len(compressed))
id = 60

with open('pcfg3_scratch.csv', 'w') as w:
    with open('pcfg3_pre.csv', 'r') as f:
        for line in f:
            w.write(line)
    
    for r in rules:
        id += 1
        w.write(f"{id},{r[0]},nonterminal,{r[1]} {r[2]},{r[3]}\n")