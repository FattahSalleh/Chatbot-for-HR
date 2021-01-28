import re
import collections
from collections import Counter

cnt = Counter()
words = re.findall('\w+', open('tagLog.csv').read())
for word in words:
    cnt[word] += 1
# print (cnt)
# cnt.most_common()
for value, count in cnt.most_common():
    print(value, count)

