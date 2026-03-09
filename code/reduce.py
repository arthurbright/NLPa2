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


def build_automaton(rules):
    transitions = defaultdict(dict)
    terminals = set()

    for A,B,C,p in rules:

        # binary rule A → T_x B
        if C is not None and B[0] == B[1]:
            x = B
            transitions[A][x] = (C,p)
            terminals.add(x)

    return transitions, terminals


def emission_distribution(transitions):
    dist = {}

    for s in transitions:
        d = {}
        for x,(t,p) in transitions[s].items():
            d[x] = p
        dist[s] = d

    return dist


def merge_states(transitions, threshold):

    dist = emission_distribution(transitions)
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
                transitions[s1][x] = (t1, p1+p)
            else:
                transitions[s1][x] = (t,p)

        del transitions[s2]
        states.remove(s2)

        # update incoming edges
        for s in transitions:
            for x,(t,p) in list(transitions[s].items()):
                if t == s2:
                    transitions[s][x] = (s1,p)

        dist = emission_distribution(transitions)

    return transitions


def normalize_transitions(transitions):

    for s in transitions:
        total = sum(p for _,p in transitions[s].values())
        for x,(t,p) in transitions[s].items():
            transitions[s][x] = (t,p/total)


def automaton_to_pcfg(transitions, terminals):

    rules = []

    for A in transitions:
        for x,(B,p) in transitions[A].items():

            T = "T_"+x
            rules.append((A,T,B,p))

    # for x in terminals:
    #     rules.append(("T_"+x, x, None, 1.0))

    return rules


def compress_pcfg(rules, merge_threshold=0.02):

    transitions, terminals = build_automaton(rules)

    transitions = merge_states(transitions, merge_threshold)

    normalize_transitions(transitions)

    return automaton_to_pcfg(transitions, terminals)

# ==============================================================


rules = []
with open('pcfg_scratch.csv', 'r') as f:
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
compressed_rules = compress_pcfg(rules, merge_threshold=0.3)
print(compressed_rules, len(compressed_rules))

id = 60
with open('pcfg_scratch.csv', 'w') as w:
    with open('pcfg3_pre.csv', 'r') as f:
        for line in f:
            w.write(line)
    
    for r in rules:
        id += 1
        w.write(f"{id},{r[0]},nonterminal,{r[1]} {r[2]},{r[3]}\n")


# print(automaton_to_pcfg(compressed_rules, []))
# ("S","a","A",0.4)
# ("S","b","B",0.6)