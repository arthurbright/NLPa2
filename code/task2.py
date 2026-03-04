# 200 terminals, 20  nonterminals.

# not including '<pad>', '<bos>', '<eos>', '<unk>',
vocab = ['<pad>', '<bos>', '<eos>', '<unk>', 'a', 'abroad', 'admire', 'admired', 'admires', 'ahead', 'ancient', 'anywhere', 'arrive', 'arrived', 'arrives', 'artist', 'artists', 'at', 'away', 'back', 'big', 'brave', 'bridge', 'bridges', 'bright', 'build', 'builds', 'built', 'by', 'call', 'called', 'calls', 'calm', 'can', 'car', 'careful', 'cars', 'cat', 'cats', 'chase', 'chased', 'chases', 'cities', 'city', 'collapse', 'collapsed', 'collapses', 'cough', 'coughed', 'coughs', 'could', 'cried', 'cries', 'cry', 'dance', 'danced', 'dances', 'depart', 'departed', 'departs', 'doctor', 'doctors', 'dog', 'dogs', 'downstairs', 'eager', 'eight', 'elsewhere', 'everywhere', 'find', 'finds', 'five', 'follow', 'followed', 'follows', 'forest', 'forests', 'found', 'four', 'from', 'garden', 'gardens', 'gentle', 'happy', 'help', 'helped', 'helps', 'home', 'honest', 'idea', 'ideas', 'in', 'inside', 'kind', 'later', 'laugh', 'laughed', 'laughs', 'libraries', 'library', 'machine', 'machines', 'may', 'meet', 'meets', 'met', 'might', 'modern', 'move', 'moved', 'moves', 'music', 'near', 'nearby', 'nine', 'noisy', 'on', 'one', 'outside', 'pause', 'paused', 'pauses', 'planet', 'planets', 'praise', 'praised', 'praises', 'prefer', 'preferred', 'prefers', 'professor', 'professors', 'project', 'projects', 'quick', 'quiet', 'quite', 'really', 'river', 'rivers', 'saw', 'see', 'sees', 'serious', 'seven', 'should', 'shout', 'shouted', 'shouts', 'six', 'sleep', 'sleeps', 'slept', 'slow', 'small', 'smart', 'smile', 'smiled', 'smiles', 'sneeze', 'sneezed', 'sneezes', 'solve', 'solved', 'solves', 'somewhere', 'songs', 'soon', 'stories', 'story', 'student', 'students', 'teacher', 'teachers', 'ten', 'the', 'this', 'three', 'today', 'tomorrow', 'tonight', 'travel', 'traveled', 'travels', 'two', 'upstairs', 'very', 'visit', 'visited', 'visits', 'wait', 'waited', 'waits', 'wander', 'wandered', 'wanders', 'watch', 'watched', 'watches', 'wild', 'will', 'with', 'would', 'yesterday']
print(len(vocab))

pos_to_token = {
    "number": [
        "eight", "five", "four", "nine", "one",
        "seven", "six", "ten", "three", "two"
    ],
    "determiner": [
        "a", "the", "this"
    ],
    "preposition": [
        "at", "by", "from", "in", "inside",
        "near", "on", "outside", "with"
    ],
    "adjective": [
        "ancient", "big", "brave", "bright", "calm",
        "careful", "eager", "gentle", "happy", "honest",
        "kind", "modern", "noisy", "quick", "quiet",
        "serious", "slow", "small", "smart", "wild"
    ],
    "noun": [
        "artist", "artists", "bridge", "bridges",
        "car", "cars", "cat", "cats",
        "cities", "city",
        "doctor", "doctors",
        "dog", "dogs",
        "forest", "forests",
        "garden", "gardens",
        "home",
        "idea", "ideas",
        "libraries", "library",
        "machine", "machines",
        "music",
        "planet", "planets",
        "professor", "professors",
        "project", "projects",
        "river", "rivers",
        "songs",
        "stories", "story",
        "student", "students",
        "teacher", "teachers"
    ],
    "verb_direct": [
        "admire", "admired", "admires",
        "build", "builds", "built",
        "call", "called", "calls",
        "chase", "chased", "chases",
        "find", "finds", "found",
        "follow", "followed", "follows",
        "help", "helped", "helps",
        "meet", "meets", "met",
        "move", "moved", "moves",
        "praise", "praised", "praises",
        "prefer", "preferred", "prefers",
        "see", "sees", "saw",
        "solve", "solved", "solves",
        "visit", "visited", "visits",
        "watch", "watched", "watches",
    ], 
    "verb_subjectless": [
        "arrive", "arrived", "arrives",
        "collapse", "collapsed", "collapses",
        "cough", "coughed", "coughs",
        "cry", "cried", "cries",
        "dance", "danced", "dances",
        "depart", "departed", "departs",
        "laugh", "laughed", "laughs",
        "pause", "paused", "pauses",
        "shout", "shouted", "shouts",
        "sleep", "sleeps", "slept",
        "smile", "smiled", "smiles",
        "sneeze", "sneezed", "sneezes",
        "travel", "traveled", "travels",
        "wait", "waited", "waits",
        "wander", "wandered", "wanders",
    ],
    "adverb": [
        "abroad", "ahead", "anywhere", "away", "back",
        "downstairs", "elsewhere", "everywhere",
        "later", "nearby",
        "somewhere", "soon",
        "today", "tomorrow", "tonight",
        "upstairs", "yesterday"
    ],
    "intensifier": [
        "really", "quite", "very"
    ],
    "modifier": [
        "can", "could", "may", "might", "should", "will", "would"
    ],
    "other": [
        '<pad>', '<eos>', '<bos>', '<unk>'
    ]
}

vocab_set = set(vocab)
vocab_set_2 = set()
for k, v in pos_to_token.items():
    for l in v:
        assert l not in vocab_set_2
        vocab_set_2.add(l)
print(len(vocab_set_2))

token_to_pos = {}
for k, v in pos_to_token.items():
    for a in v:
        token_to_pos[a] = k

pos_name_to_abrv = {}
pos_name_to_abrv['noun'] = 'NN'
pos_name_to_abrv['determiner'] = 'DT'
pos_name_to_abrv['number'] = 'CD'
pos_name_to_abrv['adjective'] = 'JJ'
pos_name_to_abrv['adverb'] = 'ADV'
pos_name_to_abrv['modifier'] = 'MOD'
pos_name_to_abrv['verb_direct'] = 'VB_dir'
pos_name_to_abrv['verb_subjectless'] = 'VB_ind'
pos_name_to_abrv['preposition'] = 'PP'
pos_name_to_abrv['intensifier'] = 'INT'