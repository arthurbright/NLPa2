import pickle
with open("code/quadline.pickle", 'rb') as f:
    lines = pickle.load(f)
    print(sum([v for v in lines.values()]))

rules = []

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# preterminals
for x in alphabet:
    if x != 'S':
        rules.append((x, x.lower(), 1.0))
    else:
        rules.append(('S2', 's', 1.0))

# TODO probs
pairs = [
    'AA A B', 0.7,
    'AA C D', 0.3,
    'BB E F', 0.7,
    'BB G H', 0.3,
    'CC I J', 0.7,
    'CC K L', 0.3,
    'DD M N', 0.7,
    'DD O P', 0.3,
    'EE Q R', 0.7,
    'EE S2 T', 0.3,
    'FF U V', 0.7,
    'FF W X', 0.3,
    'GG Y Z', 0.7,
    'GG A M', 0.3,
    'HH E I', 0.7,
    'HH O U', 0.3,
]

quads = [
    'IIII GG HH', 0.3,
    'IIII EE FF', 0.5,
    'IIII FF GG', 0.2,

    'JJJJ AA HH', 0.632,
    'JJJJ BB GG', 0.368,

    'KKKK AA BB', 0.5,
    'KKKK BB CC', 0.2,
    'KKKK CC DD', 0.3,

    'LLLL AA EE', 0.5,
    'LLLL CC FF', 0.3,
    'LLLL DD EE', 0.2,
    
    'MMMM GG EE', 0.8,
    'MMMM CC GG', 0.1,
    'MMMM DD HH', 0.1,

    'OOOO HH FF', 1.0,
]

for i in range(0, len(pairs), 2):
    a, b, c = pairs[i].split()
    p = pairs[i + 1]
    rules.append((a, b, c, p))

for i in range(0, len(quads), 2):
    a, b, c = quads[i].split()
    p = quads[i + 1]
    rules.append((a, b, c, p))
    

import pygtrie
from collections import defaultdict

def tetra(s):
    return s + s + s + s

lens = [3, 4, 5, 6, 7, 8]
len_to_cnt = defaultdict(int)
total_cnt = 0
for line in lines:
    if len(line) not in lens: continue
    len_to_cnt[len(line)] += lines[line]
    total_cnt += lines[line]
lines = [l for l in lines if len(l) in lens and lines[l] > 12]

# REDUCE THINGS FIRST



rules2 = []
if True:
    for l in lens:
        TH = 10
        d = {k: v for k, v in lines.items() if len(k) == l and ((l < 8 and v >= TH) or v > 1)}
        # build series of conditionals

        trie = pygtrie.CharTrie()
        for k in d:
            trie[k] = d[k]

        def next_char_count(prefix):
            try:
                _i = trie.items(prefix=prefix)
            except KeyError as _:
                print("no prefix", f"'{prefix}'")
                return {}
            ans = defaultdict(int)
            for k, v in _i:
                if len(k) > len(prefix):
                    ans[k[len(prefix)]] += v
            return ans
        
        seen_prefixes = set()

        todo = [""]
        # BFS
        while len(todo) > 0:
            cur_prefix = todo.pop()
            probs = next_char_count(cur_prefix)
            total = sum(probs.values())
            if len(cur_prefix) == l - 2:
                for c in probs:
                    last_probs = next_char_count(cur_prefix + c)
                    for c2 in last_probs:
                        lhs = f"n{l}{cur_prefix}" if len(cur_prefix) > 0 else "S"
                        rules2.append((lhs, tetra(c), tetra(c2), last_probs[c2]/total))
            else:
                for c in probs:
                    lhs = f"n{l}{cur_prefix}" if len(cur_prefix) > 0 else "S"
                    _p = probs[c]/total
                    if len(cur_prefix) == 0: _p = _p * len_to_cnt[l]/total_cnt
                    rules2.append((lhs, tetra(c), f"n{l}{cur_prefix + c}", _p))
                    todo.append(cur_prefix + c)






# ===================================================
id = 0

rules.extend(rules2)
with open('pcfg_scratch.csv', 'w') as f:
    f.write('ID,LHS,LHS Type,RHS,Probability\n')
    for r in rules:
        id += 1
        if len(r) == 3:
            f.write(f"{id},{r[0]},preterminal,{r[1]},{r[2]}\n")
        else:
            f.write(f"{id},{r[0]},nonterminal,{r[1]} {r[2]},{r[3]}\n")

print(len(rules))
print("TODO: tune threshold")

