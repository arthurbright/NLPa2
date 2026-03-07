from collections import defaultdict

lines = []
for sf in ['', '1', '2', '3', '4', '5']:
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
if True:
    with open("code/scratch.txt", "w") as f:
        for quad1 in quads:
            f.write(f"QUAD: {quad1}\n")
            print("QUAD:", quad1)
            ab_dist = _get_probs_multi(quad1, 4)
            similars = []
            for quad in quads:
                if quad < quad1: continue
                d = _get_probs_multi(quad, 4)
                if similar_dist(ab_dist, d):
                    similars.append(quad)
                    # print_probs(d)
            for quad in sorted(similars):
                f.write(f"{quad}\n")
            f.write("\n")


