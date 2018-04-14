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

def segmentation_one(id, content):
	content = re.sub('[0-9\/\\\s+\!]', '', content)
	content = HanziConv.toSimplified(content)
	seg_list = list(jieba.cut(content, cut_all = False))
	s = {'index':id, 'seg_list':seg_list}
	return s

def update_DF_Table(article):

	global _segmentationDir
	global _resultDir
	f = open(_resultDir + "df_table", "r")
	df = json.loads(f.read(), encoding="UTF8")
	f.close()

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

	exist = {}
	seg_list = article['seg_list']
	for word in seg_list:
	    if word not in stopword:
	        if word not in exist:
	            exist[word] = True
	            if word not in df:
	                df[word] = 1
	            else:
	                df[word] += 1

	f = open(_resultDir + "df_table", "w")
	f.write(json.dumps(df, ensure_ascii=False))
	f.close()

def tf_idf(article, rankCount = 10, docTotal = 1000):
	global _segmentationDir
	global _resultDir

	f = open(_resultDir + "df_table", "r")
	df = json.loads(f.read(), encoding="UTF8")
	f.close()
	segments = article['seg_list']
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
			# print (word)
			pass		

	sort_tf_idf = sorted(tf_idf.items(), key=operator.itemgetter(1))
	sort_tf_idf.reverse()

	for i in range(rankCount):
		word, score = sort_tf_idf[i]
		print (str(i+1) + "." + HanziConv.toTraditional(word))

filename = "data2/1050105-1.txt"
config = "config.txt"

solrID = 999
with open(filename, 'r', encoding='utf-8') as infile:
	solrContent = re.sub('[\s+]', '', infile.read().replace("<UNK>", ""))
article = segmentation_one(solrID, solrContent)

with open(config, 'r', encoding='utf-8') as infile:
	docTotal = int(infile.read())


update_DF_Table(article)
tf_idf(article, docTotal = docTotal)

docTotal += 1

f = open(config, "w")
f.write(str(docTotal))
f.close()
