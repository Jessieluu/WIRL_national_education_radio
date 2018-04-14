#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json
import os
import jieba
import math
import operator
from hanziconv import HanziConv
import re
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

doc = ""
i = 0
result = {}
allword = []
stopword = ['！', '~', '。', '：', '，', '│', '@', '阿', '喔', '啦', '啊', '了', '的', 
'、', '推', '要', '真',
'了','和','是','就', '你', '妳', '他', '她', '才', '∼'
'都','而','及','與','著','或','一個','沒有',
'我們','你們','妳們','他們','她們','是否', '哈哈哈', '啊啊啊', "\n", "=", "～", "→", ":",
str(chr(32)), str(chr(10)), str(chr(13))]



f = open("fs/tfidf", "r")
df = json.loads(f.read(), encoding="UTF8")
f.close()

f = open("fs/input", "r")
r = f.read()
f.close()

c = re.sub('[ \n0-9\/\\\s+\!]', '', r)
c = HanziConv.toSimplified(c)

seg_list = list(jieba.cut( c , cut_all = False))
tf = {}

for word in seg_list:
    if word not in stopword:
		if word in tf:
			tf[word] += 1
		else:
			tf[word] = 1

idf = {}
tf_idf = {}
docTotal = 100000
for word in tf:
	try:
		if word in df :
			idf[word] = math.log( docTotal / df[word] + 1)
		else :
			idf[word] = math.log( docTotal / 1)

		tf_idf[word] = tf[word] * idf[word]
	except KeyError:
		pass		

sort_tf_idf = sorted(tf_idf.items(),  key=operator.itemgetter(1))
sort_tf_idf.reverse()

keywordRank = ""
for i in range(5):
	word, score = sort_tf_idf[i]
	# for char in word:
	# 	print ord(char)
	keywordRank += (HanziConv.toTraditional(word)) 
	if i != 4:
		keywordRank += ","

print keywordRank

f = open("fs/output", "w")
r = f.write(keywordRank)
f.close()
