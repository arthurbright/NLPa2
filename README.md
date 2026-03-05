# Task 1
Method: Manual inspection of the transformer's next token probabilities.
Eg for cats/dogs/mice, I print the next token probabilities afer BOS, and take their normalized probabilities. For 'the', just take the transformer probability of 'the' at BOS. For chase/like, take probabilities after prefix 'the cats'.

# Task 2
First, I manually inspected ~100 outputs of the transformer. From those, I was able to deduce that the parts of speech were NN, DT, CD, VB (both direct and indirect (subjectless)), MOD (modifier), JJ, ADV (adverb), INT (intensifier), and PP. "Direct" verbs are always followed by a noun subject, whereas "indirect" verbs may terminate the sentence or be followed by a preposition.

Then, I sorted the terminals into their parts of speech (seen in `task2.py`), and ran aggregations over the transformer's `next_probs` to deduce the probabilities for nonterminals and preterminals. For example, the probabilities for each determiner can simply be determined by taking the model's `next_probs` after BOS and normalizing. The same applies for numbers and intensifiers, since they lead NP's. Most other computations were fairly simple; eg Pr(sentence ends in adverb | sentence contains modifier) could be computed by looking at `next_probs("the students will call the teachers")`.

The most complex calculation was determining the probabilities for the branching of a NP. This involved a system of equations involving the four variables Pr(sentence terminates in an indirect verb), Pr(sentence has indirect verb -> preposition), Pr(sentence has direct verb), and Pr(sentence terminates in adverb). The second half of `scratch2.txt` roughly shows my process in solving the system. 

Aggregation code is in the modified `sampling.py`, as well as code to get preterminal probabilities. This code is in the commented out section "TASK 2: fill out csv".

I noticed some discrepances in probabilities depending on whether a modifier was present, so I made "sentences with a modifier" a separate case with different direct/indirect verb distributions.

Scratch work in `scratch.txt` and `scratch2.txt` (messy)