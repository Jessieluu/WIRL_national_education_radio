import React from 'react';
import ReactDOM from 'react-dom';
import classNames from 'classnames';
import Sound from 'react-sound';

export default class QuestionTable extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            hasStopQuestionId:-1,
            closeFloatBox: -1
        };
    }

    if_correct(question_index, value) {
        if (typeof this.props.questions[question_index].user_answer == 'undefined') {
            return false;
        } else if (this.props.questions[question_index].user_answer == value
            && this.props.questions[question_index].answer == value) {
            return true;
        }
        return false;
    }

    if_wrong(question_index, value) {
        if (typeof this.props.questions[question_index].user_answer == 'undefined') {
            return false;
        } else if (this.props.questions[question_index].answer != value
            && this.props.questions[question_index].user_answer == value) {
            return true;
        }
        return false;
    }

    send_answer_to_server() {
        var finish = true;
        console.log(this.props.questions);
        for (var question_index in this.props.questions) {
            if (typeof this.props.questions[question_index].user_answer == 'undefined') {
                finish = false;
            }
        }
        if (finish == true) {
            console.log(this.props.questions);
            $.ajax({
                type: 'POST',
                url: '/radio/dosomething',
                data: JSON.stringify({
                    'audio_id' : this.props.audio_id,
                    'channel_id' : this.props.channel_id,
                    'questions' : this.props.questions
                }),
                contentType: "application/json; charset=utf-8",
            });
        }
    }

    single_option(option, question_id, question_index){
        var id = "option_" + option.id;
        var name = "option_" + question_id;
        const click_handler = (e) => {
            if (this.props.questions[question_index].user_answer != null) {
                return;
            }
            if (window.answer_count < 1 && this.props.questions[question_index].answer != option.id) {
                alert("答錯嚕！您還有一次機會！");
                ++window.answer_count;
            } else {
                this.props.set_play_status(Sound.status.PLAYING);
                $(".background-grey").toggle();
                window.answer_count = 0;
                if (this.props.questions[question_index].answer == option.id) {
                    $(e.target).removeClass('normal').addClass('correct-answer');
                    this.props.questions[question_index].correct = true;
                } else {
                    $(e.target).removeClass('normal').addClass('wrong-answer');
                    this.props.questions[question_index].correct = false;
                }
                this.props.questions[question_index].user_answer = option.id;
            }
            this.send_answer_to_server();
        }
        window.answer_count = 0;
        var class_name = Object();
        class_name.option = true;

        // var style={
        //     "border-radius": "5px",
        //     border: "solid 1px #FFF",
        //     "margin-top": "10px",
        //     "padding-left": "5px",
        //     height: "32px",
        //     "line-height": "32px",
        //     cursor: "pointer"
        // }

        if (this.if_correct(question_index, option.id) || (!(typeof this.props.questions[question_index].user_answer == 'undefined') && this.props.questions[question_index].answer == option.id) ) {
            class_name.correct = true;
            // style["color"] = "#0F0";
        } else if (this.if_wrong(question_index, option.id)) {
            class_name.wrong = true;
            // style["color"] = "#F00";
        } else {
            class_name.normal = true;
        }
        var option_id = "option_" + question_id + "_" + id;
        return(
            <li id={option_id} className={classNames(class_name)} onClick={click_handler} key={"s" + option.id}>
                {option.label}
            </li>
        );
    }

    option_table(options, type, question_id, question_index) {
        var op = [];
        for(var i in options) {
            if (type == "single") {
                op.push(this.single_option(options[i], question_id, question_index));
            } else if (type == "multiple") {
                op.push(this.multiple_option(options[i], question_id, question_index));
            }
        }
        return (<ul className="option-table">{op}</ul>);
    }

    interactive(question_id) {
        var sid = this.state.hasStopQuestionId;
        if (this.props.is_interactive && this.state.hasStopQuestionId != question_id) {
            var t = this;
            setTimeout(function () {
                t.props.set_play_status(Sound.status.PAUSED);
                t.setState({hasStopQuestionId: question_id});
                $(".background-grey").toggle();
            }, 1);
        }
    }

    show_score() {
        
        const close = (e) => {
            location.reload(true);
        }
        $(".background-grey").toggle();
        var empty = 0;
        var correct = 0;
        var wrong = 0;
        for (var index in this.props.questions) {
            if (typeof this.props.questions[index].correct == 'undefined' || this.props.questions[index].correct == null) {
                ++empty;
            } else if (this.props.questions[index].correct) {
                ++correct;
            } else {
                ++wrong;
            }
        }
        return(
            <div className="question-block">
                <div className="board">
                    <div className="header">
                        <div className="program-title">{this.props.audio_name}</div>
                        <div className="album-title">{this.props.channel_name}</div>
                    </div>
                    <div className="content">   
                        <div className="question">廣播結束！<br/>您一共有: <br/>{empty}題未作答<br/>{correct}正確<br/>{wrong}錯誤</div>
                        <button className="skip" onClick={close}>確定 >></button>
                    </div>    
                </div>
            </div>
        
        );
    }

    skip(id) {
        
        const close = (e) => {
            this.setState({"closeFloatBox": id});
            $(".background-grey").toggle();
            this.props.set_play_status(Sound.status.PLAYING);
        }

        if (this.state.closeFloatBox != -1 && id != this.state.closeFloatBox) {
            this.setState({"closeFloatBox": -1});
        }

        return(<button className="skip" onClick={close}>跳過 >></button>);
    }

    keywords(){
        var keywords = this.props.keywords;

        return(<div className="keywords">
            {this.props.keywords.map((word) => (
                <span>#{word}</span>
            ))}
        </div>);
    }

    question() {
        if ($(".switch:checked").length == 0) {
            return;
        }

        var time = this.props.current;

        return(<div>
                {(time >= this.props.duration - 1 && this.props.duration != 0) ?
                    <div>{this.show_score()}</div>
                : null}

                {this.props.questions.map((result, i) => (
                    <div key={i}>
                        {this.state.closeFloatBox != result.id && (time - 1 >= result.start && time - 1 < result.end) ?
                            <div className="question-block">
                                <div className="board">
                                    <div className="header">
                                        <div className="program-title">{this.props.audio_name}</div>
                                        <div className="album-title">{this.props.channel_name}</div>
                                    </div>
                                    <div className="content">
                                        {this.interactive(result.id)}                                     
                                        <div className="question-text">{result.content}</div>
                                        {this.option_table(result.options, result.type, result.id, i)}  
                                        {this.skip(result.id)}
                                    </div>    
                                </div>
                            </div>
                        : null}                                                                
                    </div>                        
                ))}       
        </div>);
    }

    render() {

        return (
            <div className="question_table">
				<div className="intro-title">節目摘要</div>
                <div className="intro-content">
                    {this.props.depiction}
                </div>
                {this.keywords()} 
                {this.question()} 
            </div>            
        );
    }
}
