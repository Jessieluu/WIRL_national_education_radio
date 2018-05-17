import jieba
import jieba.analyse
import csv
import io
import re
import pysolr
import sys
import json
import requests
import codecs
from pprint import pprint
import numpy as np
import os
from hanziconv import HanziConv
from zhon.hanzi import punctuation
from sortedcontainers import SortedDict

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


# file path setting
_resultDir = os.path.dirname(os.path.abspath(__file__)) + '/'

# jieba cut load
jieba.analyse.set_stop_words(_resultDir + 'dict_stop_words.txt')
jieba.set_dictionary(_resultDir + 'dict.txt.big')
jieba.load_userdict(_resultDir + 'stopwords.txt')

# scrawler url setting
url = "http://nermoocs.org/solr/EBCStation/select?indent=on&q=*:*&rows=9999&wt=json"
request = requests.get(url).json()


Top10alllist = dict()  #儲存每則文的keywords


# update final tf_idf table
def addNumber(name, number):
    if (name in Top10alllist):
        if Top10alllist[name]<number:
            Top10alllist[name] = number
    else:
        Top10alllist[name] = number
# open stop_words file txt
f = open(_resultDir + 'dict_stop_words.txt', 'r', newline='')
ff = f.read()


# scrawler and jieba
corpus = []
for i in range(126):
    if i is 127:
        break
    elif i is 128:
        j=i
        continue
    j = i
    content = request['response']['docs'][j]['content']
    content = HanziConv.toSimplified(content)
    """
    temp = ""
    for i in content:
        if i not in ff:
            temp+=i
    """
    js = json.dumps(content, ensure_ascii=False)
    #words = jieba.cut_for_search(js)
    words = jieba.cut(js, cut_all=True)
    #js = re.sub("[\\\" ]", "", js)
    # js = re.sub(ur"[%s]+" %punctuation, "", js.decode("utf-8"))
    corpus.append(" ".join(words))
    #print(corpus)

f.close()

# tf_idf API
countvec = CountVectorizer()#该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
trans = TfidfTransformer()#该类会统计每个词语的tf-idf权值

wordFrequence = countvec.fit_transform(corpus)
tfidf = trans.fit_transform(wordFrequence)#第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵

words = countvec.get_feature_names()  # 获取词袋模型中的所有词语
Weight = tfidf.toarray()#将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重


# update td_idf table
for weight in Weight:
    loc = np.argsort(-weight)#將weight降序排列也就是由大到小排列
    for i in range(len(weight)):     #每篇文章all keywords的tfidf值當作代表
        tmp1 = words[loc[i]]
        tmp2 = weight[loc[i]]
        #print (tmp1,tmp2)
        addNumber(tmp1 , tmp2)


# print len(Top10alllist)

# sort tf_idf table
result = []
result = sorted(Top10alllist.items(), key=lambda Top10alllist: Top10alllist[1], reverse=True)


# print tf_idf result
#for i in range(len(result)):
#    print (result[i][0],result[i][1])




# ----------------------------------------- #


# job 1 table create #

# writing to csv set up
f = open(_resultDir + 'jobone.csv', 'w', newline='')
write = csv.writer(f)
csvtable= []

# experiment value
value = [0.33,0.35,0.385,0.4,0.45,0.5,0.55]
temp = []

# iterator all content
for i in range(150):
    if i is 127:
        break
    elif i is 128:
        j = i
        continue
    j = i
    # store csv title
    content = request['response']['docs'][j]['content']
    content = HanziConv.toSimplified(content)
    temp.append('Article :'+str(j))
    write.writerow(temp)
    temp.clear()
    csvtable.append(content)
    write.writerow(csvtable)
    csvtable.clear()
    # iterator all experiment value
    for i in value:
        temp.append(i)
        # iterator all tf_idf
        for r in range(len(result)):
            # if tf_idf value bigger than experiment value
            if result[r][1] > i:
                # then check keyword exist in content or not
                if result[r][0] in content:
                    temp.append(HanziConv.toTraditional(result[r][0]))
        csvtable.append(temp)
        # writing result to csv
        write.writerow(csvtable)
        temp.clear()
        csvtable.clear()

f.close()


# storing tf_idf key,value to csv
f = open(_resultDir + 'tf_idf.csv', 'w', newline='')
write = csv.writer(f)
for r in range(len(result)):
        #print(result[r][1])
    temp.append(HanziConv.toTraditional(result[r][0]))
    temp.append(result[r][1])
    write.writerow(temp)
    temp.clear()
f.close()

# storing different(by experiment value) tf_idf result to csv
temp = []
for i in value:
    fileName = str(i)
    f = open(_resultDir + fileName+'.csv', 'w', newline='')
    write = csv.writer(f)
    for r in range(len(result)):
        #print(result[r][1])
        if result[r][1] > i:
            temp.append(HanziConv.toTraditional(result[r][0]))
            temp.append(result[r][1])
            write.writerow(temp)
        temp.clear()
    f.close()





# relation table creat #
keyword_size = 30

# inital keywordAmount table for store result
keywordAmount = np.zeros((keyword_size,keyword_size),int)

for i in range(126):
    # takes article to calculatling keywords amount
    # article and content are the same thing
    content = request['response']['docs'][i]['content']
    content = HanziConv.toSimplified(content)

    # if keyword A in article
    for r in range(keyword_size):
        if result[r][0] in content:
            # then check other keywords without A
            for j in range(keyword_size):
                # without keyword A
                if j == r:
                    continue
                keyword = result[j][0]
                # keyword appears so that calculate amount +1
                if keyword in content:
                    keywordAmount[r][j] +=1


# open csv to store result
f = open(_resultDir + 'relation.csv', 'w', newline='')
write = csv.writer(f)

# set up horizontal keyword line
list = []
list.append(" ")
for j in range(keyword_size):
    word = result[j][0]
    list.append(HanziConv.toTraditional(word))
write.writerow(list)
list.clear()

# set up to stores result and vertical keyword line to csv
for i in range(keyword_size):
    list.append(HanziConv.toTraditional(result[i][0]))
    for j in range(keyword_size):
        Amount = keywordAmount[i][j]
        list.append(Amount)
    write.writerow(list)
    list.clear()

f.close()




"""
# set up to store realtion table to json file
json_dict = []

#print(new_dict)

for i in range(keyword_size):
    for j in range(keyword_size):
        temp = []
        if keywordAmount[i][j] == 0:
            continue
        temp.append(HanziConv.toTraditional(result[i][0]))
        temp.append(HanziConv.toTraditional(result[j][0]))
        Amount = keywordAmount[i][j]
        temp.append(Amount)
        #print(temp, '\n')
        json_dict.append(temp)
pprint(json_dict)
json_str = json.dumps(json_dict,ensure_ascii=False).encode('utf8')
new_dict = json.loads(json_str)
_json = _resultDir + 'keyword.json'
with open(_json,"w",encoding='utf8') as f:
    json.dump(new_dict,f)

"""

