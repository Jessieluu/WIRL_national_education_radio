import json
import pysolr
import re
from io import StringIO

from flask import redirect, url_for, render_template, session, flash
from flask.ext.login import current_user, login_required, logout_user, login_user

from NationalEducationRadio.service import get_blueprint
from NationalEducationRadio.service import db
from NationalEducationRadio.models.db.User import User, AccessLevel
from NationalEducationRadio.models.db.Category import Category
from NationalEducationRadio.models.db.Channel import Channel
from NationalEducationRadio.models.db.Audio import Audio
from NationalEducationRadio.models.db.Record import Record
from NationalEducationRadio.models.form.ChannelForm import ChannelForm
from NationalEducationRadio.models.form.LoginForm import LoginForm
from NationalEducationRadio.models.form.AudioForm import AudioForm
from NationalEducationRadio.models.form.KeywordForm import KeywordForm
from NationalEducationRadio.models.form.CaptionForm import CaptionForm
from NationalEducationRadio.models.units.tools import password_encryption, required_to_flash, audio_upload, parse_question_csv, get_solr_data, article_filter
from NationalEducationRadio.models.units.login import backstage_required
from NationalEducationRadio.models.units.keywords import get_keyword

admin = get_blueprint('admin')


@admin.route('/', methods=['GET', 'POST'])
def index():
    """
    登入後台
    :return: 登入後臺頁面
    """
    def login_redirect():
        return redirect(url_for('admin.channel'))

    if current_user.is_anonymous is not True:
        return login_redirect()

    form = LoginForm()
    if form.validate_on_submit():
        admin_user = User.query.filter_by(account=form.account.data, password=password_encryption(form.password.data)).first()
        print(admin_user)
        if admin_user is not None:
            session['level'] = admin_user.level
            login_user(admin_user)
            return login_redirect()
        else:
            flash('帳號或密碼錯誤')
    required_to_flash(form)
    return render_template('admin/index.html', form=form)


@admin.route('/logout')
@login_required
@backstage_required
def logout():
    """
    登出後台
    :return: 轉址到登入後台
    """
    logout_user()
    return redirect(url_for('admin.index'))


@admin.route('/channel')
@login_required
@backstage_required
def channel():
    chals = Channel.query.all()
    return render_template('admin/channel.html', chals=chals, user=current_user)

@admin.route('/channel/insert', methods=['GET', 'POST'])
@login_required
@backstage_required
def channel_insert():
    form = ChannelForm()
    if form.validate_on_submit():
        new_channel = Channel(channel_name=form.channel_name.data, category=form.channel_category.data, channel_memo=form.channel_memo.data)
        return redirect(url_for('admin.channel'))
    return render_template('admin/channel_form.html', form=form, behavior="新增")

@admin.route('/channel/update/<id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def channel_update(id):
    form = ChannelForm()
    if form.validate_on_submit():
        edit_channel = Channel.query.filter_by(channel_id=form.channel_id.data).first()
        edit_channel.channel_name = form.channel_name.data
        edit_channel.category = form.channel_category.data
        edit_channel.channel_memo = form.channel_memo.data
        return redirect(url_for('admin.channel'))
    channel = Channel.query.filter_by(channel_id=id).first()
    form.channel_id.data = channel.channel_id
    form.channel_name.data = channel.channel_name
    form.channel_category.data = channel.category
    form.channel_memo.data = channel.channel_memo
    return render_template('admin/channel_form.html', channel=channel, form=form, behavior="編輯")

# *****
@admin.route('/channel/delete/<id>', methods=['GET','POST'])
@login_required
@backstage_required
def channel_delete(id):
    form = ChannelForm()
    if form.validate_on_submit():
        del_audio = Audio.query.filter_by(audio_channel=id).all()
        for d in range(len(del_audio)):
            del_record = Record.query.filter_by(audio_id=del_audio[d].audio_id).all()
            for r in range(len(del_record)):
                db.session.delete(del_record[r])
            db.session.delete(del_audio[d])
        del_channel = Channel.query.filter_by(channel_id=form.channel_id.data).first()
        db.session.delete(del_channel)
        return redirect(url_for('admin.channel'))
    channel = Channel.query.filter_by(channel_id=id).first()
    form.channel_id.data = channel.channel_id
    form.channel_name.data = channel.channel_name
    form.channel_category.data = channel.category
    form.channel_memo.data = channel.channel_memo
    return render_template('admin/channel_form.html', channel=channel, form=form, readonly=1, behavior="刪除")




@admin.route('/audio/<channel_id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def audio(channel_id):
    channel = Channel.query.filter_by(channel_id=channel_id).first()
    audios = Audio.query.filter_by(channel=channel).all()
        
    return render_template('admin/audio.html', audios=audios, user=current_user, channel=channel)

@admin.route('/audio/add/<channel_id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def audio_add(channel_id):
    form = AudioForm()
    channel = Channel.query.filter_by(channel_id=channel_id).first()
    if form.validate_on_submit():
        new_audio = Audio(
            audio_name=form.audio_name.data,  
            channel=channel,
            audio_file=audio_upload(form.audio_file.data),
            audio_question=parse_question_csv(form.audio_question.data))
        return redirect(url_for('admin.audio', channel_id = channel.channel_id))
    
    form.audio_channel.data = channel.channel_id
    return render_template('admin/audio_form.html', form=form, behavior="新增", isdelete=0, channel=channel)

@admin.route('/audio/delete/<id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def audio_delete(id):
    form = AudioForm()
    form.uncheckFileUpload()
    if form.validate_on_submit():
        del_audio = Audio.query.filter_by(audio_id=form.audio_id.data).first()
        if Record.query.filter_by(audio_id=form.audio_id.data).all() is not None:
            del_record = Record.query.filter_by(audio_id=form.audio_id.data).all()
            for d in range(len(del_record)):
                db.session.delete(del_record[d])
        if Audio.query.filter_by(audio_id=form.audio_id.data).first() is not None:
            del_audio = Audio.query.filter_by(audio_id=form.audio_id.data).first()
            db.session.delete(del_audio)
        return redirect(url_for('admin.audio', channel_id = del_audio.channel.channel_id))
    audio = Audio.query.filter_by(audio_id=id).first()
    form.audio_id.data = audio.audio_id
    form.audio_name.data = audio.audio_name
    form.audio_channel.data = audio.channel.channel_id
    return render_template('admin/audio_form.html', form=form, readonly=1, behavior="刪除", isdelete=1, channel=audio.channel)

@admin.route('/audio/edit/<id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def audio_edit(id):
    form = AudioForm()
    form.uncheckFileUpload()
    audio = Audio.query.filter_by(audio_id=id).first()
    if form.validate_on_submit():
        audio.audio_name = form.audio_name.data
        print(form.audio_file.data.filename)
        if form.audio_file.data.filename:
            audio.audio_file = audio_upload(form.audio_file.data)

        if form.audio_question.data.filename:
            audio.audio_question = parse_question_csv(form.audio_question.data)

        return redirect(url_for('admin.audio', channel_id = audio.channel.channel_id))
    form.audio_id.data = audio.audio_id
    form.audio_name.data = audio.audio_name
    form.audio_channel.data = audio.channel.channel_id
    return render_template('admin/audio_form.html', form=form, readonly=0, behavior="編輯", isdelete=0, channel=audio.channel)

@admin.route('/audio/view/<id>', methods=['GET'])
@login_required
@backstage_required
def audio_view(id):
    audio = Audio.query.filter_by(audio_id=id).first()
    records = Record.query.filter_by(audio=audio).all()
    questions = json.load(StringIO(audio.audio_question))
    for question in questions:
        question['correct'] = 0
        question['wrong'] = 0

    for record in records:
        recordData = json.load(StringIO(record.record_data))
        for data in recordData:
            for question in questions:
                if data['id'] == question['id']:
                    if data['user_answer'] == data['answer'][0]:
                        question['correct'] = question['correct'] + 1
                    else:
                        question['wrong'] = question['wrong'] + 1
                    break

    return render_template('admin/audio_view.html', questions=questions)

#****
@admin.route('/audio/keyword_view/<id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def keyword_view(id):
    audio = Audio.query.filter_by(audio_id=id).first()
    success, dontuse, summary = get_solr_data(audio.audio_id)
    keywords = audio.keyword
    if keywords is None:
        keywords = "關鍵字尚未建置"
    form = KeywordForm()
    if form.validate_on_submit():
        solr = pysolr.Solr('http://127.0.0.1/solr/EBCStation', timeout=10)
        if "<eps>" in form.keyword_content.data:
            solrContent = article_filter(form.keyword_content.data)
        else:
            solrContent = form.keyword_content.data
        top10, summary = get_keyword(form.keyword_id.data, solrContent)
        solr.delete(q='audio_id:'+id)
        solr.add([
        {
            "audio_id": form.keyword_id.data,
            "content": solrContent,
            "summary" : summary
        }])
        return redirect(url_for('admin.audio', channel_id = audio.channel.channel_id))
    form.keyword_id.data = audio.audio_id
    return render_template('admin/keyword_view.html', audio=audio, form=form, success=success, keywords=keywords, summary=summary)


# need to add
@admin.route('/audio/caption_view/<id>', methods=['GET', 'POST'])
@login_required
@backstage_required
def caption_view(id):
    audio = Audio.query.filter_by(audio_id=id).first()
    form = CaptionForm()
    caption = ""
    if form.validate_on_submit():
        solr = pysolr.Solr('http://127.0.0.1/solr/EBCStationCaption', timeout=10)
        caption = form.caption_content.data
        solr.delete(q='audio_id:'+id)
        solr.add([
        {
            "audio_id": form.caption_id.data,
            "caption": form.caption_content.data,
        }])
        return redirect(url_for('admin.audio', channel_id=audio.channel.channel_id))
    form.caption_id.data = audio.audio_id
    return render_template('admin/caption_view.html', audio=audio, form=form, caption=caption)
