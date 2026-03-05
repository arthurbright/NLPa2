lines = [
    "u v a m a b o u y z q r",
    "q r w x e f y z e i u v a b q r q r u v k l y z a b e f e f y z",
    "g h y z m n q r y z s t",
    "a m e i c d e i a m q r",
    "y z e i c d e i o u u v i j u v c d q r e f y z a m s t a b e f",
    "a b s t q r u v a b e i a b q r a m s t c d q r u v y z a m q r",
    "e f y z y z q r o u w x",
    "y z q r e f i j y z q r",
    "e f y z y z s t o u u v",
    "u v y z e f i j q r u v y z q r",
    "c d o u y z s t y z o u i j u v",
    "y z s t i j o p e i u v m n q r e f y z m n o u e f k l g h i j",
    "q r u v c d e i m n q r s t w x i j m n s t u v e i u v m n q r",
    "a b e f a m e i y z q r a b s t s t w x y z q r a b g h a b e i",
    "a b o u a m q r c d q r w x y z y z e i e f a m a b e i k l y z",
    "a b q r q r u v y z o u a b o u q r u v a b e i a b s t",
    "i j m n q r u v y z q r a b q r y z o u y z q r i j o p g h y z",
    "y z e i y z e i e f y z g h y z y z q r k l u v a b e i y z s t",
    "c d q r a b e i y z q r a b e f e f y z m n e i e f i j",
    "g h i j q r w x y z s t a b q r a m e i e f a m k l w x g h i j",
    "c d e i k l a m m n q r u v y z u v y z c d e i i j m n y z e i",
    "a m e i q r u v e f i j y z e i q r w x i j m n q r u v q r u v",
    "y z e i a b e i m n q r c d e i y z s t m n s t u v a m i j y z",
]

from collections import defaultdict
seen = defaultdict(int)
for line in lines:
    line = line.split()
    for i in range(0, len(line), 2):
        seen[line[i] + line[i + 1]] += 1

for k, v in sorted(seen.items(), key=lambda item: item[1], reverse=True):
    print(f"{k}: {v}")
print(len(seen))

seen2 = set()
for k in ['', 'ab', 'abef', 'abei', 'abgh', 'abou', 'abqr', 'abst', 'am', 'amei', 'amou', 'amqr', 'amst', 'cd', 'cdef', 'cdei', 'cdgh', 'cdou', 'cdqr', 'cdst', 'ef', 'efam', 'efij', 'efkl', 'efyz', 'gh', 'gham', 'ghij', 'ghkl', 'ghyz', 'ij', 'ijam', 'ijmn', 'ijop', 'ijuv', 'ijwx', 'ijyz', 'kl', 'klam', 'klmn', 'klop', 'kluv', 'klwx', 'klyz', 'mn', 'mnei', 'mnou', 'mnqr', 'mnst', 'op', 'opei', 'opou', 'opqr', 'opst', 'qr', 'qruv', 'qrwx', 'st', 'stuv', 'stwx', 'uv', 'uvam', 'uvyz', 'wx', 'wxam', 'wxyz', 'yz', 'yzei', 'yzou', 'yzqr', 'yzst']:
    for i in range(0, len(line), 2):
        seen2.add(k[i:i + 2])
print(seen2, len(seen2))