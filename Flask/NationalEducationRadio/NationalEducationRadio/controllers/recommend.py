"""

include :8 recommend module
output : final recommend audio
"""

from NationalEducationRadio.service import get_blueprint
from NationalEducationRadio.models.recommend.batch import similar_audio, op_habit
from NationalEducationRadio.models.db.Audio import Audio
from NationalEducationRadio.models.db.User import User
from NationalEducationRadio.models.db.TimeHotPlay import TimeHotPlay
from NationalEducationRadio.models.db.OperationLog import OperationLog
from NationalEducationRadio.models.db.PlayLog import PlayLog
from NationalEducationRadio.models.db.HotPlay import HotPlay
from NationalEducationRadio.models.db.SearchLog import SearchLog
from NationalEducationRadio.models.db.SearchSelectedLog import SearchSelectedLog
import json
import sys
from collections import OrderedDict, Set
from operator import itemgetter

radio = get_blueprint('radio')

# userTimeHotPlay Module, done
def countUserTimeHotPlay(top_k, user_id, recommendTable):

    # ****** countUserTimeHotPlay Module Start ******
    print("****** Start processing countUserTimeHotPlay core Module ! ******", file=sys.stderr)

    # cold start condition, if time_hot_play audio numbers < top_k or Null then return
    user = User.query.filter_by(id=user_id).first()
    # avoid user not watch any audio
    if user.most_use_time == None:
        return recommendTable
    timeHotPlay = TimeHotPlay.query.order_by(TimeHotPlay.count).all()
    # timeHotPlay numbers are three times audio numbers
    #if len(timeHotPlay)/3 < top_k:
    #    print("\ncountUserTimeHotPlay module do nothing!\n")
    #    return recommendTable
    # cold start end

    # for take top k audio
    flag = 0
    # iterator, for all dataSet start from Most count to Low count
    # update final recommend table
    for k in range(len(timeHotPlay)-1, -1, -1):
        # audio is timeHot then add to final rank table
        if timeHotPlay[k].time_zone == user.most_use_time:
            audio_id = timeHotPlay[k].audio_id
            flag += 1
            if audio_id not in recommendTable:
                recommendTable[audio_id] = 1
            else:
                recommendTable[audio_id] += 1
        # get top k audio then break
        if flag == top_k:
            break
    print("\nAfter countUserTimeHotPlay Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing countUserTimeHotPlay core Module done! ******\n", file=sys.stderr)
    return recommendTable
    # ****** countUserTimeHotPlay Module End ******

# timehotPlay Module, done
def timeHotPlay(top_k, user_id, recommendTable):

    # *** timeHotPlay Module Start ***

    print("****** Start processing timeHotPlay core Module! ******", file=sys.stderr)

    # get all data from TimeHotPlay db with order
    dataSet = TimeHotPlay.query.order_by(TimeHotPlay.count).all()

    # cold start condition, if db does not have data then return
    #if len(dataSet) < top_k:
    #    print("\ntimeHotPlay module do nothing!\n")
    #    return recommendTable

    # get the most timeHot audio time_zone
    timeHotTimeZone = dataSet[len(dataSet)-1].time_zone

    # prevent repeat add same time hot audio
    user = User.query.filter_by(id=user_id).first()
    userMostUseTime = user.most_use_time

    # avoid to double calculate same TimeHot with userTimeHotPlay Module
    if timeHotTimeZone != userMostUseTime:
        # for take top k audio
        flag = 0
        # iterator, for all dataSet start from Most count to Low count
        # update final recommend table
        for k in range(len(dataSet)-1, -1, -1):
            # audio is timeHot then add to final rank table
            if dataSet[k].time_zone == timeHotTimeZone:
                audio_id = dataSet[k].audio_id
                flag += 1
                if audio_id not in recommendTable:
                    recommendTable[audio_id] = 1
                else:
                    recommendTable[audio_id] += 1
            # get top k audio then break
            if flag == top_k:
                break
    print("\nAfter timeHotPlay Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing timeHotPlay core Module done! ******\n", file=sys.stderr)
    return recommendTable
    # *** TimeHotPlay Module End ***

# hot_play Module, done
def hotPlay(top_k, recommendTable):

    # *** hotPlay Module Start ***
    print("****** Start processing hotplay core Module! ******", file=sys.stderr)

    # query all ordered data from HotPlay db
    hotPlay = HotPlay.query.order_by(HotPlay.audio_id).all()

    # cold start condition, if db does not have data then return
    #if len(hotPlay) < top_k:
    #    print("\nhotPlay module do nothing!\n")
    #    return recommendTable

    # iterator, for ordered dataSet from hotPlay db
    # update final recommend table
    flag = 0
    for i in range(len(hotPlay)):
        audio_id = hotPlay[i].audio_id
        flag += 1
        if audio_id not in recommendTable:
            recommendTable[audio_id] = 1
        else:
            recommendTable[audio_id] += 1
        # get top k audio then break
        if flag == top_k:
            break
    print("\nAfter hotplay Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing hotplay core Module done! ******\n", file=sys.stderr)
    return recommendTable
    # *** hotPlay Module End ***

# op_habit Module, done
def opHabit(top_k, user_id, recommendTable):

    # ****** opHabit Module Start ******
    print("****** Start processing opHabit core Module! ******")

    # query all data from User db by user_id
    user = User.query.filter_by(id=user_id).first()

    # cold start condition, if user operation_ranks len < 5 data then return.
    # data form: A,B,C  len:6
    #if len(user.operation_ranks)/2+1 < top_k:
    #    print("\nopHabit module do nothing!\n")
    #    return recommendTable

    # for save audio which have user operation
    audio_operation_rank = {}
    # iterator, for audio appear in operation_ranks from User db by user_id
    op_ranks = user.operation_ranks.split(",")

    flag = 0
    audioIdSet = set()
    # calculate the most often appear audio until audio count > top_k
    for i in op_ranks:
        # use set to avoid repeat add audio , EX : 1,1,1,3,4
        # need to convert to int, otherwise can not be found on recommendTable
        audioIdSet.add(int(i))

    # update final recommend table
    for s in audioIdSet:
        flag += 1
        if s not in recommendTable:
            recommendTable[s] = 1
        else:
            recommendTable[s] += 1
        if flag == top_k:
            break
    print("\nAfter opHabit Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing opHabit core Module done! \n******")
    return recommendTable

    # ****** opHabit Module End ******

# audio_similar Module, done
def similarAudio(top_k, user_id, audio_id, recommendTable):

    # ****** similarAudio Module Start ******
    print("****** Start processing similarAudio core Module! ******")

    # query similar_audio from Audio db by user watching audio_id
    audio = Audio.query.filter_by(audio_id=audio_id).first()
    # db storage is json format
    tsimilar_audio = json.loads(audio.similar_audio)
    # cold start condition, if db does not have enough data then return
    # if len(similar_audio) < top_k:
    #    print("\nsimilarAudio module do nothing!\n")
    #    return recommendTable

    # for take all element from json
    orderSimilarAudio = {}
    # iterator json data insert to orderSimilarAudio dict
    for i in tsimilar_audio:
        key = int(list(i.keys())[0])
        value = int(list(i.values())[0])
        orderSimilarAudio[key] = value
    # sort dict by using OrderedDict
    orderedSimilarAudio = OrderedDict(sorted(orderSimilarAudio.items(), key=lambda t: t[1], reverse=True))

    # update final recommend table start
    flag = 0
    # iterator, update ordered dataSet to final table
    for (k, v) in orderedSimilarAudio.items():
        flag += 1
        if k not in recommendTable:
            recommendTable[k] = 1
        else:
            recommendTable[k] += 1
        # get top k audio then break
        if flag == top_k:
            break
    print("\nAfter similarAudio Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing similarAudio core Module done! \n******")
    return recommendTable

    # *** similarAudio Module End ***

# searchselect Module, done
def searchSelect(top_k, user_id, recommendTable):

    # ****** Start processing searchselect Module  !******
    print("****** Start processing searchselect core Module! ******")

    # get two times search text data from one user to processing whole module
    userSearchTextLen = 2

    # get user search text data
    userSearchLog = SearchLog.query.filter_by(user=user_id).all()

    # cold start condition, if db does not have enough search data
    # or search_select_logs then return
    if len(userSearchLog) == 0 or len(SearchSelectedLog.query.all()) < top_k:
        print("\nsearchSelect module do nothing!\n")
        return recommendTable

    # using search_id to link SearchSelectedLog db for calculate audio rank
    # initial parameters, rankTable: save audio numbers count and rank
    rankTable = {}
    # iterator, retrieval search text of one user
    for i in range(userSearchTextLen):
        # query all similar keywords of data from SearchLog db
        searchLogdb = SearchLog.query.filter(SearchLog.search_text.ilike("%" + userSearchLog[i].search_text + "%")).all()

        # iteration for query all similar keywords
        for j in range(len(searchLogdb)):
            # get search_id from SearchLogdb
            searchLogdbId = searchLogdb[j].search_id
            # query search_id from SearchSelectedLog db by search_id
            searchSelectLogdb = SearchSelectedLog.query.filter_by(search_id=searchLogdbId)
            # get audioId from SearchSelectedLog
            audioId = searchSelectLogdb[0].audio

            # calculate audio count, must be initialized rankTable first
            # when audioId not store on rankTable, otherwise count plus one
            if audioId not in rankTable:
                rankTable[audioId] = 1
            else:
                rankTable[audioId] += 1
        # sorting attribute count on rankTable by using OrderedDict
        # output from largest to smallest
    orderedRankTable = OrderedDict(sorted(rankTable.items(), key=lambda t: t[1], reverse=True))

    # update final recommend table start
    flag = 0
    # iterator, update ordered dataSet to final table
    for (k, v) in orderedRankTable.items():
        flag += 1
        if k not in recommendTable:
            recommendTable[k] = 1
        else:
            recommendTable[k] += 1
        # get top k audio then break
        if flag == top_k:
            break
    print("\nAfter searchselect Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing searchselect core Module done! \n******")
    return recommendTable
    # ****** Processing searchselect Module done !******

# searchkeywords Module, done
def searchKeywords(top_k, user_id, recommendTable):

    # ****** Start processing searchselect Module!******
    print("****** Start processing searchkeywords core Module! ******")

    # get two times search text data from one user to processing whole module
    userSearchTextLen = 2

    # get user search text data
    userSearchLog = SearchLog.query.filter_by(user=user_id).all()

    # cold start condition, if db does not have enough search data
    # or playLog data then return
    if len(userSearchLog) == 0 or len(PlayLog.query.all()) < top_k:
        print("\nsearchKeywords module do nothing!\n")
        return recommendTable

    # iterator, retrieval search text of one user
    for u in range(userSearchTextLen):
        # query all similar search keywords of data from SearchLog db
        searchLogdb = SearchLog.query.filter(SearchLog.search_text.ilike("%" + userSearchLog[u].search_text + "%")).all()
        # get all search similar keywords user besides myself
        similarUser = set()
        for s in range(len(searchLogdb)):
            if searchLogdb[s].user is not user_id:
                similarUser.add(searchLogdb[s].user)

        # use search similar keywords user to calculate
        # the number of watch audios from PlayLog db
        audioWatchRank = {}
        for i in similarUser:
            # filter user information from PlayLog db by user id each time
            oneUserWatchAudio = PlayLog.query.filter_by(user=i).all()
            # get one user have seen audio
            for j in range(len(oneUserWatchAudio)):
                audioId = oneUserWatchAudio[j].audio
                if audioId not in audioWatchRank:
                    audioWatchRank[audioId] = 1
                else:
                    audioWatchRank[audioId] += 1
        # sorting attribute audio count on audioWatchRank by using OrderedDict
        # output from largest to smallest
        orderedRankTable = OrderedDict(sorted(audioWatchRank.items(), key=lambda t: t[1], reverse=True))

    # update final recommend table start
    flag = 0
    # iterator, update ordered dataSet to final table
    for (k, v) in orderedRankTable.items():
        flag += 1
        if k not in recommendTable:
            recommendTable[k] = 1
        else:
            recommendTable[k] += 1
        # get top k audio then break
        if flag == top_k:
            break
    print("\nAfter searchkeywords Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing searchkeywords core Module done! \n******")
    return recommendTable
    # ****** Processing searchkeywords Module done !******

# relationkeywords, done
def relationKeywords(top_k, user_id, recommendTable):

    # ****** Start processing relation Module!******
    print("****** Start processing searchKeywords core Module! ******\n")

    # ******** get user watch audio rank start ********

    # filter all watch audio_Id from one user
    userPlayLog = PlayLog.query.filter_by(user=user_id).all()

    # cold start condition, if db does not have enough userPlaylog data
    if len(userPlayLog) == 0:
        print("\nrelationKeywords module do nothing!\n")
        return recommendTable

    rankTable = {}
    # retrieval all watch audio to one user
    for i in range(len(userPlayLog)):
        audioId = userPlayLog[i].audio
        # calculate audio count
        # must be initialized rankTable first if audioId not store on rankTable,otherwise count plus one
        if audioId not in rankTable:
            rankTable[audioId] = 1
        else:
            rankTable[audioId] += 1
    # sorting attribute count on rankTable by using OrderedDict, output from largest to smallest
    orderedRankTable = OrderedDict(sorted(rankTable.items(), key=lambda t: t[1], reverse=True))

    # ******** get user highest watch audio rank end! ********


    # ******** create relationkeywordset Start ********
    print("****** Start processing relationKeywords create! ******\n")
    # query top_k audio
    queryLen = len(orderedRankTable)
    if queryLen > 5:
        queryLen = 5
    # record my top k watch audio id
    topAudioId = set()
    # save all relation keyword by top k audio rank
    relationKeywordSet = set()
    for i in range(queryLen):
        # get highest rank audio id by sorted RankTable
        highestAudioId = list(orderedRankTable.items())[i]
        # get audio keyword by audio id
        getKeyword = Audio.query.filter_by(audio_id=highestAudioId[0]).first().keyword
        # split "," on Db
        splitList = getKeyword.split(",")
        for j in splitList:
            if j is not '':
                relationKeywordSet.add(j)
        topAudioId.add(highestAudioId[0])

    print("\nAfter relationKeywords Module processing!")
    print("\n Current RecommendTable State:\n\n", recommendTable, "\n")
    print("****** Processing relationKeywords create done! ******\n")
    # ******** create relationkeywordset End ********


    # ******** Final audio recommendation by relationkeyword Start ********
    print("****** Start processing relationKeywords audio recommend table! ******\n")
    audioDbLen = Audio.query.count()
    # for sorting all audio count rank
    audioRankTable = {}
    # retrieval all watch audio expect top k rank audio
    for i in range(1, audioDbLen+1):
        AudioId = i
        # exclude user top k audio
        if AudioId not in topAudioId:
            # get audio keyword by audio id
            getKeyword = Audio.query.filter_by(audio_id=AudioId).first().keyword
            # for calculate audio keyword appear count
            audioCount = 0
            # split "," on Db
            splitList = getKeyword.split(",")
            for j in splitList:
                # if keyword appear both on relation keyword set and article, then this audio count plus one
                if j in relationKeywordSet:
                    audioCount += 1
            if AudioId not in audioRankTable:
                audioRankTable[AudioId] = audioCount
            else:
                return str("Error occur!")
    # sorting attribute count on rankTable by using OrderedDict, output from largest to smallest
    audioRecommendTable = OrderedDict(sorted(audioRankTable.items(), key=lambda t: t[1], reverse=True))
    print("****** Processing relationKeywords audio recommend table done! ******\n")

    # update final recommend table start
    flag = 0
    # iterator, update ordered dataSet to final table
    for (k, v) in audioRecommendTable.items():
        flag += 1
        if k not in recommendTable:
            recommendTable[k] = 1
        else:
            recommendTable[k] += 1
        # get top k audio then break
        if flag == top_k:
            break

    print("****** Processing relationKeywords core Module done! \n******")
    return recommendTable
    # ******** Final audio recommendation by relationkeyword End ********


# radioRecSysCoreModule
# using Composite pattern concept to write for convenient add new module
@radio.route('/recommend/<int:user_id>/<int:audio_id>', methods=['GET', ])
def recommend(user_id, audio_id):
    # initial top k audio
    top_k = 5
    recommendTable = {}
    # (1,1),(3,1),(4,1)
    recommendTable = countUserTimeHotPlay(top_k, user_id, recommendTable)
    recommendTable = timeHotPlay(top_k, user_id, recommendTable)
    recommendTable = hotPlay(top_k, recommendTable)
    recommendTable = opHabit(top_k, user_id, recommendTable)
    recommendTable = similarAudio(top_k, user_id, audio_id, recommendTable)
    recommendTable = searchSelect(top_k, user_id, recommendTable)
    recommendTable = searchKeywords(top_k, user_id, recommendTable)
    recommendTable = relationKeywords(top_k, user_id, recommendTable)

    # sort final recommend table
    orderedRankTable = OrderedDict(sorted(recommendTable.items(), key=lambda t: t[1], reverse=True))
    return json.dumps(orderedRankTable, ensure_ascii=False)

