from collections import defaultdict

lines = []
for sf in ['', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
    file_name = f'output{sf}.txt'
    with open(file_name) as f:
        for line in f:
            line = line.strip().replace(' ', '')
            lines.append(line)


lines.sort(key=lambda line: (len(line), line))

with open("all_output.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

lens = defaultdict(int)
num_lines = len(lines)
for line in lines:
    lens[len(line)] += 1
print("Total number of lines", len(lines))

print("Length distribution =====================")
for k, v in lens.items():
    print(f"Length {k}: \t {v} \t  {v/num_lines}")
# safe to assume that length 6 and length 24 are degenerate?
# lengths: 12, 16, 20, 28, 32

pairs = defaultdict(int)
for line in lines:
    for i in range(0, len(line), 2):
        pairs[line[i:i + 2]] += 1

# filter out degeneracies (occurences 10 or less)
pairs = {k: v for k, v in pairs.items() if v >= 10}
print("Pair distribution ======================")
print("Number of distinct pairs:", len(pairs))
for k, v in sorted(pairs.items(), key=lambda item: item[1], reverse=True):
    print(k, v)

assert len(pairs) == 16

print("Quad distribution ======================")
quads = defaultdict(int)
for line in lines:
    for i in range(0, len(line), 4):
        quads[line[i:i + 4]] += 1

# filter out degeneracies (occurences 10 or less)
quads = {k: v for k, v in quads.items() if v >= 10}
print("Number of distinct quads:", len(quads))
for k, v in sorted(quads.items(), key=lambda item: item[1], reverse=True):
    print(k, v)

assert len(quads) == 60

from sampling_copy import *
from sampling_copy import _load_checkpoint
if True:
    print("Loading model: ============================")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, artifacts = _load_checkpoint("checkpoints/pcfg3.pt", device=device)
def _get_probs(prefix):
    return get_probs(model, device, artifacts, prefix)

def _get_probs_multi(prefix: str, n, TH = 0.001):
    cur = {"": 1.0}
    for i in range(n):
        cur2 = {}
        for x, prob in cur.items():
            if len(x) > 0 and x[-1] == '>':
                cur2[x] = prob
                continue 
            next_probs = _get_probs(prefix + x)
            for k, v in next_probs.items():
                if v < TH: continue
                cur2[x + k] = float(prob * v)
        cur = cur2
    return cur

def similar_dist(d1, d2, ERR = 0.1, topk = 5):
    def _similar_dist(d1, d2):
        # consider the top k next seqs. if they are within a certain error of each other, they are the same.
        d1_sorted =  sorted(d1.items(), key=lambda item: item[1], reverse=True)[:topk]
        for k, v in d1_sorted:
            if k not in d2 or abs(d2[k] - v) > ERR:
                return False
        return True
    return _similar_dist(d1, d2) and _similar_dist(d2, d1)

# pair analysis
if False:
    for pair1 in pairs:
        print("PAIR: ", pair1)
        ab_dist = _get_probs_multi(pair1, 2)
        print_probs(ab_dist)
        for pair in pairs:
            d = _get_probs_multi(pair, 2)
            if similar_dist(ab_dist, d):
                print("Similar dist:", pair)
                print_probs(d)


# quad analysis:
if False:
    q_to_dist = {}
    for q in quads:
        q_to_dist[q] = _get_probs_multi(q, 4)
    with open("code/scratch.txt", "w") as f:
        for quad1 in quads:
            f.write(f"QUAD: {quad1}\n")
            print("QUAD:", quad1)
            ab_dist = q_to_dist[quad1]
            similars = []
            for quad in quads:
                # if quad < quad1: continue
                d = q_to_dist[quad]
                if similar_dist(ab_dist, d, ERR = 0.06, topk = 8):
                    similars.append(quad)
                    # print_probs(d)
            for quad in sorted(similars):
                f.write(f"{quad}\n")
            f.write("\n")


ABBR_PAIR = {
    'ab': 'A', 'cd': 'A',
    'ef': 'B', 'gh': 'B',
    'ij': 'C', 'kl': 'C',
    'mn': 'D', 'op': 'D',
    'qr': 'E', 'st': 'E',
    'uv': 'F', 'wx': 'F',
    'yz': 'G', 'am': 'G',
    'ei': 'H', 'ou': 'H'
}

ABBR_QUAD = {
    'GH': 'I',
    'EF': 'I',
    'FG': 'I',

    'AH': 'J',
    'BG': 'J',

    'AB': 'K',
    'BC': 'K',
    'CD': 'K',

    'AE': 'L',
    'CF': 'L',
    'DE': 'L',

    'GE': 'M',
    'CG': 'M',
    'DH': 'M',

    'HF': 'O',
}

def to_pairs(s: str):
    assert len(s) % 2 == 0
    ans = ""
    for i in range(0, len(s), 2):
        ans += ABBR_PAIR[s[i:i + 2]]
    return ans

def to_quads(s: str):
    s = to_pairs(s)
    assert len(s) % 2 == 0
    ans = ""
    for i in range(0, len(s), 2):
        ans += ABBR_QUAD[s[i:i + 2]]
    return ans
    

quad_lines = defaultdict(int)
quad_lines_list = []
with open('code/scratch.txt', 'w') as f:
    num_illegal = 0
    for line in lines:
        try:
            s = to_quads(line)
            # f.write(f"{s}\n")
            quad_lines[s] += 1
            quad_lines_list.append(s)
        except:
            num_illegal += 1
    print("Num degenerate lines", num_illegal)

with open('code/quadline.txt', 'w') as f:
    num_singles = 0
    for k, v in sorted(quad_lines.items(), key=lambda item: (len(item[0]), item[1]), reverse=False):
        if v > 1:
            f.write(f"{k} \t {v}\n")
        else:
            num_singles += 1
    print("Num singles:", num_singles)

import pickle

with open('code/quadline.pickle', 'wb') as f:
    d = {k: v for k, v in quad_lines.items()}
    print("Dumping: ", len(d), sum([v for v in d.values()]))
    pickle.dump(quad_lines, f)

import random
# with open('code/quadlines.pickle', 'wb') as f:
#     pickle.dump(quad_lines_list, f)
# print_probs(_get_probs_multi("abqrcdeiamst", 2))
# print_probs(_get_probs_multi("abeiamqreiuv", 2))
# print(to_quads("abeiamqreiuv"))
with open('code/training.txt', 'w') as f:
    random.shuffle(quad_lines_list)
    quad_lines_list = [q for q in quad_lines_list if len(q) == 8]
    quad_lines_list = quad_lines_list[:50]
    for quad_line in quad_lines_list:
        line = " ".join([c for c in quad_line]).lower()
        f.write(f"{line}\n")

from collections import Counter
# get pair and quad branching distribution
pair_dist = defaultdict(Counter)
quad_dist = defaultdict(Counter)
for line in lines:
    if len(line) % 4 == 0:
        try:
            ps = to_pairs(line)
            qs = to_quads(line)
        except:
            continue
        for i in range(len(ps)):
            pair_dist[ps[i]][line[i * 2: (i + 1) * 2]] += 1
        for i in range(len(qs)):
            quad_dist[qs[i]][ps[i * 2: (i + 1) * 2]] += 1

print("PAIR DIST")
for k, v in pair_dist.items():
    total = sum(v.values())
    for kk, vv in v.items():
        print(k, kk, vv/total)
print("QUAD DIST")
for k, v in quad_dist.items():
    total = sum(v.values())
    for kk, vv in v.items():
        print(k, kk, vv/total)


print_probs(_get_probs_multi('abei', 2))
print_probs(_get_probs_multi('efyz', 2))

exit()

Q = ['KIM', 'IJO', "JLO", 'MKO']
X = ['IMK', 'JMK', 'IIJ', "IJL"]
X2 = ['IMK', 'JMK', 'IIJ', "IJL", 'IIK']
XQ = X + Q
X2Q = X2 + Q
SING = ['M', 'K', 'I', 'J']
PP = ['II', 'IK', 'KI', 'JM', 'IM', 'IJ', 'JL', 'MK']

all_possible = set()
rules = [
    ["JML", X, 'JM'],
    ['JML', X2Q, 'KI'],
    ['JML', X2, 'IJ'],
    ['JMLL', X, SING], # NOTE: DIFFERENT SING
    ['JMLL', Q, 'K'],
    [X, 'JML', PP],
    [X, Q, 'L', SING],
    [Q, 'L', X, SING], # NOTE: DIFFERNT SING
    []
]

def expand_rule(rule, pre = ""):
    if len(rule) == 0: 
        all_possible.add(pre)
        return
    if isinstance(rule[0], str):
        expand_rule(rule[1:], pre + rule[0])
    else:
        r = rule[1:]
        for k in rule[0]:
            expand_rule(r, pre + k)

for rule in rules:
    expand_rule(rule)

missing = {}
for quad_line in quad_lines:
    if len(quad_line) == 8 and quad_line not in all_possible:
        missing[quad_line] = quad_lines[quad_line]

for k, v in sorted(missing.items(), key=lambda item: item[1]):
    print(f"{k} \t {v}")
