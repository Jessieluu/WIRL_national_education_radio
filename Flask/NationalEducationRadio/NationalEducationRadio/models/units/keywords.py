import os
import requests
import json
import re
import math
import operator
from hanziconv import HanziConv
import jieba
_resultDir = os.path.dirname(os.path.abspath(__file__)) + "/keyword/"

def segmentation_one(id, content):

	stopword = [
		'！', '~', '。', '：', '@', '、', '∼', '，',
		'阿', '喔', '啦', '啊', '了', '的',
		'推', '要', '真', '了', '和', '是',
		'就', '你', '妳', '他', '她', '才', '且', 
		'都','而','及','與','著','或',
		'一個', '沒有', '是否',
		'我們','你們','妳們','他們','她們', '哈哈哈', '啊啊啊']
	for word in stopword:
		content = content.replace(word, "")



	content = re.sub('[\s+]', '', content.replace("<UNK>", ""))
	content = re.sub('[0-9\/\\\s+\!]', '', content)
	content = HanziConv.toSimplified(content)
	seg_list = list(jieba.cut(content, cut_all = False))
	s = {'index':id, 'seg_list':seg_list}
	return s

def update_DF_Table(article):

	global _resultDir
	f = open(_resultDir + "df_table", "r")
	df = json.loads(f.read(), encoding="UTF8")
	f.close()

	result = {}
	allword = []
	stopword = [
		'！', '~', '。', '：', '@', '、', '∼', '，',
		'阿', '喔', '啦', '啊', '了', '的',
		'推', '要', '真', '了', '和', '是',
		'就', '你', '妳', '他', '她', '才', '且', 
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

def tf_idf(article, rankCount = 10):
	global _resultDir
	config = os.path.dirname(os.path.abspath(__file__)) + "/keyword/config.txt"
	with open(config, 'r', encoding='utf-8') as infile:
		docTotal = int(infile.read())
	docTotal += 1
	f = open(config, "w")
	f.write(str(docTotal))
	f.close()

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
	keywordRank = []
	for i in range(rankCount):
		word, score = sort_tf_idf[i]
		keywordRank.append(HanziConv.toTraditional(word))
	return (keywordRank, tf_idf)

def get_summary(content, tf_idf):

	sort_tf_idf = sorted(tf_idf.items(), key=operator.itemgetter(1))
	sort_tf_idf.reverse()
	for i in range(10):
		word, score = sort_tf_idf[i]
		print (str(i+1) + "." + HanziConv.toTraditional(word))



	contentSegment = re.split('，|。', content)

	segmentScoreList = []
	for i in range(len(contentSegment)):
		score = 0
		total = 0
		seg_list = segmentation_one(1, contentSegment[i])['seg_list']
		for seg in seg_list:
			try:
				score += tf_idf[seg]
				total += 1
			except KeyError:
				pass

		if total != 0:
			segmentScoreList.append({
				'segment' : contentSegment[i],
				'score' : score / total
			})

	scoreList = sorted(segmentScoreList, key=lambda k: k['score'], reverse=True)

	goals = []
	i = 0
	for s in scoreList:
		if len(s['segment']) > 10:
			goals.append(s['segment'])
			i += 1
			if i == 5:
				break

	result = []
	for i in range(len(contentSegment)):
		if contentSegment[i] in goals:
			try:
				result.append(contentSegment[i])
			except:
				pass
	return '，'.join(result) + "。"


def get_keyword(id, content):

	article = segmentation_one(id, content)
	update_DF_Table(article)
	top10, tf_idf_obj = tf_idf(article)
	summary = get_summary(content, tf_idf_obj)


	return (top10, summary)

