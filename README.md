# Task 1
Simple inspection of the transformer's next token probabilities.
Eg for cats/dogs/mice, I print the next token probabilities afer BOS, and take their normalized probabilities. For 'the', just take the transformer probability of 'the' at BOS. For chase/like, take probabilities after prefix 'the cats'.

# Task 2
First, I manually inspected ~100 outputs of the transformer. From those, I was able to deduce that the preterminals were NN, DT, CD, VB (both direct and indirect (subjectless)), MOD (modifier), JJ, ADV (adverb), and PP. Then, I sorted the terminals into their categories, and ran aggregations over the transformer's `next_probs` to deduce the probabilities for nonterminals and preterminals. 

I noticed some discrepances in probabilities depending on whether a modifier was present, so I made "sentences with a modifier" a separate case with different direct/indirect verb distributions.