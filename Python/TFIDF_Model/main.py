#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import requests
import string
from urllib.request import urlopen
import time
import json
import sys
import re
import math
import operator
from hanziconv import HanziConv
import jieba


_fetcherDir = "./fetcher/";
_loaderDir = "./loader/"
_segmentationDir = "./segmentation/"
_resultDir = "./result/"

allDir = [_fetcherDir, _loaderDir, _segmentationDir, _resultDir]
for x in allDir:
	if os.path.isdir(x) is False:
			os.mkdir(x)

url = "http://140.124.183.39:8983/solr/EBCStation/select?indent=on&q=id:test_*&sort=id%20asc&wt=json"
url += '&start={0}&rows={1}'


def fetcher(url, start = 0, limit = 10000, rows = 2500):
	global _fetcherDir
	s = start
	i = 0
	while s < start + limit :
		print ("rows: " + str(s) + "~" + str(s + rows))
		jsonData = requests.get(url.format(s, rows)).json()
		f = open(_fetcherDir + str(i), 'w')
		f.write(json.dumps(jsonData))
		s += rows
		i += 1

	return i

# fetcher(url, 0, 105, 105)


def loader(maxDocIndex):
	global _fetcherDir
	global _loaderDir

	i = 0
	result = []

	for i in range(0, maxDocIndex):
		f = open(_fetcherDir + str(i), "r")
		r = f.read()
		f.close()

		j = json.loads(r)
		response = j['response']['docs']
		for row in response:
			# print (row)
			index = str(row['id'][5:])
			one = { 'id' : 0, 'content': None}
			try:
				one['id'] = row['id'][5:]
				one['content'] = row['content']
				result.append(one)
			except KeyError:
				pass
			except :
				sys.exit(0)
	f = open(_loaderDir + "result", "w")
	print (result)
	r = json.dumps(result)
	f.write(r)
	f.close()

# loader(fetcher(url, start = 0, rows = 105, limit = 105));
# loader(1)

def segmentation(start, end):
	global _loaderDir
	global _segmentationDir

	f = open(_loaderDir + "result", "r")
	r = f.read()
	f.close()
	j = json.loads(r)

	for i in range(start, end) :
	    print (i)
	    row = j[i]

	    content = row['content'] 
	    content = re.sub('[0-9\/\\\s+\!]', '', content)
	    content = HanziConv.toSimplified(content)

	    seg_list = list(jieba.cut(content, cut_all = False))

	    s = {'index':i, 'seg_list':seg_list}    
	    f = open(_segmentationDir + str(i), "w")
	    f.write(json.dumps(s, ensure_ascii=False))
	    f.close()

# segmentation(0, 105)
# segmentation(0, 1000);


def create_DF_Table(start, end):

	global _segmentationDir
	global _resultDir
	result = {}
	allword = []
	stopword = [
		'！', '~', '。', '：', '@', '、', '∼',
		'阿', '喔', '啦', '啊', '了', '的',
		'推', '要', '真', '了', '和', '是',
		'就', '你', '妳', '他', '她', '才', 
		'都','而','及','與','著','或',
		'一個', '沒有', '是否',
		'我們','你們','妳們','他們','她們', '哈哈哈', '啊啊啊']

	for i in range(start, end) :
		print (i)
	    f = open(_segmentationDir + str(i), "r")
	    j = json.loads(f.read())
	    f.close()
	    exist = {}

	    seg_list = j['seg_list']
	    for word in seg_list:
	        if word not in stopword:
	            if word not in exist:
	                exist[word] = True
	                if word not in result:
	                    result[word] = 1
	                else:
	                    result[word] += 1


	f = open(_resultDir + "df_table", "w")
	f.write(json.dumps(result, ensure_ascii=False))
	f.close()


create_DF_Table(0, 105);


def tf_idf(articleID, rankCount = 10, docTotal = 1000):
	global _segmentationDir
	global _resultDir

	f = open(_resultDir + "df_table", "r")
	df = json.loads(f.read(), encoding="UTF8")
	f.close()

	f = open(_segmentationDir + str(articleID), "r")
	segments = json.loads(f.read())['seg_list']
	f.close() 

	tf = {}

	for word in segments:
		if word in tf:
			tf[word] += 1
		else:
			tf[word] = 1

	idf = {}
	tf_idf = {}

	for word in tf:
		try:
			idf[word] = math.log(docTotal / df[word])
			tf_idf[word] = tf[word] * idf[word]
		except KeyError:
			pass		

	sort_tf_idf = sorted(tf_idf.items(), key=operator.itemgetter(1))
	sort_tf_idf.reverse()

	for i in range(rankCount):
		word, score = sort_tf_idf[i]
		print (str(i+1) + "." + HanziConv.toTraditional(word))

tf_idf(articleID = 0, docTotal = 105)


