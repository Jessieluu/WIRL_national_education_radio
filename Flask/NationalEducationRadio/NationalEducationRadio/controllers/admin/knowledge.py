from NationalEducationRadio.service import get_blueprint
from NationalEducationRadio.models.db.Audio import Audio

from flask import request
import requests
from collections import Set
from hanziconv import HanziConv
from ast import literal_eval
import json

radio = get_blueprint('radio')


# final need to change id to audio_id #
@radio.route('/knowldge', methods=['GET', ])
def knowldge():

    finalResult = []
    # get search keyword
    keyword = str(request.args.get('keyword'))
    # scrawler setting
    url = "http://127.0.0.1/solr/EBCStation/select?indent=on&q=*:*&rows=9999&wt=json"
    # url = "http://nermoocs.org/solr/EBCStation/select?indent=on&q=*:*&rows=9999&wt=json"
    article = requests.get(url).json()
    # db length
    articleLen = article['response']['numFound']
    # save audio_id
    audioID = set()
    # filter Audio ID
    for a in range(articleLen):
        if len(audioID) is 100:
            break
        if article['response']['docs'][a]['audio_id'].isdigit() is True and keyword in article['response']['docs'][a]['content']:
            audioID.add(article['response']['docs'][a]['audio_id'])
    # query Audio Info from db
    for i in audioID:
        # save one audio format result
        result = {}
        result["id"] = i
        audioInfo = Audio.query.filter_by(audio_id=i).first()
        if audioInfo is None:
             continue
        
        # processing keyword string format
        keywordList = []
        if audioInfo.keyword is not None:    
            for k in HanziConv.toTraditional(audioInfo.keyword).split(","):
                if k is not '':
                    keywordList.append(k)
        # save json format parameters
        result["KeyWord"] = keywordList
        result["type"] = int(audioInfo.audio_channel)
        result["title"] = int(audioInfo.audio_name)
        result["text"] = ""
        # get similar audio ID
        similarAudioData = Audio.query.filter_by(audio_id=i).first().similar_audio
        # save ID
        similarAudioID = []
        # str covert to dict
        if similarAudioData is not None:
            listSimilarAudio = literal_eval(similarAudioData)
            # save audio all similarAudioID
            for l in listSimilarAudio:
                for k in l.keys():
                    similarAudioID.append(int(k))
                    
        result["links"] = similarAudioID
        finalResult.append(result)

    print(finalResult)

    return "OK"
