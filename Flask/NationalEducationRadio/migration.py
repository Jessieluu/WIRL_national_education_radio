import hashlib
import random
import string
from datetime import datetime

from NationalEducationRadio.service import app, db
from NationalEducationRadio.models.db.User import User
from NationalEducationRadio.models.db.Category import Category
from NationalEducationRadio.models.db.Channel import Channel
from NationalEducationRadio.models.db.Audio import Audio
from NationalEducationRadio.models.db.PlayLog import PlayLog
from NationalEducationRadio.models.db.TimeHotPlay import TimeHotPlay
from NationalEducationRadio.models.db.OperationLog import OperationLog
from NationalEducationRadio.models.db.HotPlay import HotPlay


"""
    batch create data for db test data
"""

def create_data():

    #createUser()
    createCategory()
    createChannel()
    createAudio()
    #createPlayLog()
    #createTimeHotPlay()
    #createOperationLog()
    #hotPlay()
    print("Finished all create !")
"""
    audio = Audio(
            channel=chal_1,
            audio_name="AAA",  
            audio_file="test.wav",
            audio_question='[{"id": 1, "content": "\u6771\u5357\u4e9e\u570b\u5bb6\u5e38\u898b\u780d\u4f10\u68ee\u6797\u6216\u711a\u6797\uff0c\u4e3b\u8981\u662f\u70ba\u4e86\u7a2e\u690d\u54ea\u4e00\u7a2e\u7d93\u6fdf\u4f5c\u7269\uff1f", "type": "single", "start": "0", "end": "5", "answer": [2], "options": [{"id": 1, "label": "\u76f8\u601d\u6a39"}, {"id": 2, "label": "\u68d5\u6ada\u6a39"}, {"id": 3, "label": "\u6a61\u81a0\u6a39"}, {"id": 4, "label": "\u6930\u5b50\u6a39"}]}, {"id": 2, "content": "\u674e\u5947\u82f1\u6559\u6388\u8ac7\u5230\u5357\u6975\u7814\u7a76\u6700\u5927\u7684\u6536\u7a6b\u9664\u4e86\u505a\u7814\u7a76\u5916\uff0c\u6700\u68d2\u7684\u4e8b\u60c5\u662f\uff1f", "type": "single", "start": "6", "end": "9", "answer": [8], "options": [{"id": 5, "label": "\u89c0\u8cde\u661f\u7a7a"}, {"id": 6, "label": "\u96ea\u5730\u98a8\u60c5"}, {"id": 7, "label": "\u770b\u5357\u6975\u7279\u6709\u52d5\u7269"}, {"id": 8, "label": "\u6975\u5149\u7f8e\u666f"}]}, {"id": 3, "content": "\u672c\u96c6\u300c\u53f0\u7063 special\u300d\u4ecb\u7d39\u7684\u53f0\u7063\u7279\u6709\u7a2e\u52d5\u7269\u662f\u4ec0\u9ebc\uff1f", "type": "single", "start": "10", "end": "20", "answer": [11], "options": [{"id": 9, "label": "\u53f0\u7063\u9ed1\u718a"}, {"id": 10, "label": "\u9ad8\u5c71\u767d\u8179\u9f20"}, {"id": 11, "label": "\u9ec3\u5589\u8c82"}, {"id": 12, "label": "\u68d5\u80cc\u4f2f\u52de"}]}]')
    audio2 = Audio(
            channel=chal_2,
            audio_name="BB",  
            audio_file="test.wav",
            audio_question='[{"id": 1, "content": "\u6771\u5357\u4e9e\u570b\u5bb6\u5e38\u898b\u780d\u4f10\u68ee\u6797\u6216\u711a\u6797\uff0c\u4e3b\u8981\u662f\u70ba\u4e86\u7a2e\u690d\u54ea\u4e00\u7a2e\u7d93\u6fdf\u4f5c\u7269\uff1f", "type": "single", "start": "0", "end": "5", "answer": [2], "options": [{"id": 1, "label": "\u76f8\u601d\u6a39"}, {"id": 2, "label": "\u68d5\u6ada\u6a39"}, {"id": 3, "label": "\u6a61\u81a0\u6a39"}, {"id": 4, "label": "\u6930\u5b50\u6a39"}]}, {"id": 2, "content": "\u674e\u5947\u82f1\u6559\u6388\u8ac7\u5230\u5357\u6975\u7814\u7a76\u6700\u5927\u7684\u6536\u7a6b\u9664\u4e86\u505a\u7814\u7a76\u5916\uff0c\u6700\u68d2\u7684\u4e8b\u60c5\u662f\uff1f", "type": "single", "start": "6", "end": "9", "answer": [8], "options": [{"id": 5, "label": "\u89c0\u8cde\u661f\u7a7a"}, {"id": 6, "label": "\u96ea\u5730\u98a8\u60c5"}, {"id": 7, "label": "\u770b\u5357\u6975\u7279\u6709\u52d5\u7269"}, {"id": 8, "label": "\u6975\u5149\u7f8e\u666f"}]}, {"id": 3, "content": "\u672c\u96c6\u300c\u53f0\u7063 special\u300d\u4ecb\u7d39\u7684\u53f0\u7063\u7279\u6709\u7a2e\u52d5\u7269\u662f\u4ec0\u9ebc\uff1f", "type": "single", "start": "10", "end": "20", "answer": [11], "options": [{"id": 9, "label": "\u53f0\u7063\u9ed1\u718a"}, {"id": 10, "label": "\u9ad8\u5c71\u767d\u8179\u9f20"}, {"id": 11, "label": "\u9ec3\u5589\u8c82"}, {"id": 12, "label": "\u68d5\u80cc\u4f2f\u52de"}]}]')
    audio3 = Audio(
            channel=chal_3,
            audio_name="CC",  
            audio_file="test.wav",
            audio_question='[{"id": 1, "content": "\u6771\u5357\u4e9e\u570b\u5bb6\u5e38\u898b\u780d\u4f10\u68ee\u6797\u6216\u711a\u6797\uff0c\u4e3b\u8981\u662f\u70ba\u4e86\u7a2e\u690d\u54ea\u4e00\u7a2e\u7d93\u6fdf\u4f5c\u7269\uff1f", "type": "single", "start": "0", "end": "5", "answer": [2], "options": [{"id": 1, "label": "\u76f8\u601d\u6a39"}, {"id": 2, "label": "\u68d5\u6ada\u6a39"}, {"id": 3, "label": "\u6a61\u81a0\u6a39"}, {"id": 4, "label": "\u6930\u5b50\u6a39"}]}, {"id": 2, "content": "\u674e\u5947\u82f1\u6559\u6388\u8ac7\u5230\u5357\u6975\u7814\u7a76\u6700\u5927\u7684\u6536\u7a6b\u9664\u4e86\u505a\u7814\u7a76\u5916\uff0c\u6700\u68d2\u7684\u4e8b\u60c5\u662f\uff1f", "type": "single", "start": "6", "end": "9", "answer": [8], "options": [{"id": 5, "label": "\u89c0\u8cde\u661f\u7a7a"}, {"id": 6, "label": "\u96ea\u5730\u98a8\u60c5"}, {"id": 7, "label": "\u770b\u5357\u6975\u7279\u6709\u52d5\u7269"}, {"id": 8, "label": "\u6975\u5149\u7f8e\u666f"}]}, {"id": 3, "content": "\u672c\u96c6\u300c\u53f0\u7063 special\u300d\u4ecb\u7d39\u7684\u53f0\u7063\u7279\u6709\u7a2e\u52d5\u7269\u662f\u4ec0\u9ebc\uff1f", "type": "single", "start": "10", "end": "20", "answer": [11], "options": [{"id": 9, "label": "\u53f0\u7063\u9ed1\u718a"}, {"id": 10, "label": "\u9ad8\u5c71\u767d\u8179\u9f20"}, {"id": 11, "label": "\u9ec3\u5589\u8c82"}, {"id": 12, "label": "\u68d5\u80cc\u4f2f\u52de"}]}]')
 
    db.session.add_all([audio, audio2, audio3])
    db.session.commit()
"""
# add User
def createUser():

    adm_1 = User(id=1, account="admin1", name="test1", password="123", level=1)
    adm_2 = User(id=2, account="admin2", name="test2", password="123", level=1)
    adm_3 = User(id=3, account="admin3", name="test3", password="123", level=1)
    db.session.add_all([adm_1, adm_2, adm_3])
    db.session.commit()

# add Caregory
def createCategory():
    cls_1 = Category(category_id=1, category_name='教育')
    cls_2 = Category(category_id=2, category_name='兒童')
    cls_3 = Category(category_id=3, category_name='藝術')
    # cls_4 = Category(category_name='旅遊')
    cls_5 = Category(category_id=5, category_name='生活')
    # cls_6 = Category(category_name='自然')
    # cls_7 = Category(category_name='音樂')
    db.session.add_all([cls_1, cls_2, cls_3, cls_5])
    db.session.commit()

# add Channel
def createChannel():
    chal_1 = Channel(channel_id=1, channel_category=1, channel_name="從心歸零", channel_memo="從心歸零")
    chal_2 = Channel(channel_id=2, channel_category=2, channel_name="不單單是藝術", channel_memo="不單單是藝術")
    chal_3 = Channel(channel_id=3, channel_category=3, channel_name="教育行動家", channel_memo="教育行動家")
    chal_4 = Channel(channel_id=4, channel_category=5, channel_name="哲學Café", channel_memo="哲學Café")
    db.session.add_all([chal_1, chal_2, chal_3, chal_4])
    db.session.commit()

# add Audio
def createAudio():
    aud_1 = Audio(audio_id=1, audio_name="test1", audio_channel=1)
    aud_2 = Audio(audio_id=2, audio_name="test2", audio_channel=2)
    aud_3 = Audio(audio_id=3, audio_name="test3", audio_channel=3)
    aud_4 = Audio(audio_id=4, audio_name="test4", audio_channel=4)
    db.session.add_all([aud_1, aud_2, aud_3, aud_4])
    db.session.commit()

# add playLog
def createPlayLog():
    #1435983900 = morning, 1435955100 = evening, 1435926300 = afternoon
    log_1 = PlayLog(play_log_id=1, audio=1, user=1, star_time="1435983900")
    log_2 = PlayLog(play_log_id=2, audio=2, user=2, star_time="1435955100")
    log_3 = PlayLog(play_log_id=3, audio=3, user=3, star_time="1435926300")
    log_4 = PlayLog(play_log_id=4, audio=3, user=3, star_time="1435983900")
    db.session.add_all([log_1, log_2, log_3, log_4])
    db.session.commit()

# add TimeHotPlay
def createTimeHotPlay():
    thp_1 = TimeHotPlay(id=1, audio_id=1, count=2, time_zone="evening")
    thp_2 = TimeHotPlay(id=2, audio_id=2, count=3, time_zone="afternoon")
    thp_3 = TimeHotPlay(id=3, audio_id=3, count=4, time_zone="morning")
    thp_4 = TimeHotPlay(id=4, audio_id=4, count=5, time_zone="morning")
    db.session.add_all([thp_1, thp_2, thp_3, thp_4])
    db.session.commit()

# add OperationLog
def createOperationLog():
    otl_1 = OperationLog(operation_log_id=1, play_log=1, operation_code=1)
    otl_2 = OperationLog(operation_log_id=2, play_log=2, operation_code=2)
    otl_3 = OperationLog(operation_log_id=3, play_log=3, operation_code=3)
    otl_4 = OperationLog(operation_log_id=4, play_log=4, operation_code=4)
    db.session.add_all([otl_1, otl_2, otl_3, otl_4])
    db.session.commit()

# add hotPlay
#def hotPlay():
