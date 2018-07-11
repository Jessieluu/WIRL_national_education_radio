import React from 'react';
import ReactDOM from 'react-dom';
import Sound from 'react-sound';
/**
 * 這是播放器畫面控制React元件
 */

var op_code = {
    "PLAY_PAUSE" : 0x01,
    "GO_NEXT_AUDIO" : 0x02,
    "SEEK_BAR" : 0x04,
    "ACTIVE_MODE" : 0x08
};
var obj ={};
var audio_new ={};
let id_loading = undefined;
export default class RadioUI extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            position: 0,
            duration: 0,
            current: 0,
            volume: 50,
            play_log_id: -1,
            seekBarLock: false,
            playPauseLock: false,
            interactiveMode: true,
            load_playlog: false,
            button_type: "",
            first_play: true
        };        
    }

    play_pause_button(){
        const onClick = (ev) => {
            ev.preventDefault();
            
            if(this.state.first_play == true){
                this.props.set_operation_code(op_code.PLAY_PAUSE);                
                this.props.set_operation_value("play");  
            }

            if (this.props.play_status === Sound.status.PAUSED ){
                this.props.set_play_status(Sound.status.PLAYING);
                this.props.set_operation_code(op_code.PLAY_PAUSE);
                this.setState({first_play: false});           
                this.props.set_operation_value("play");     
            } else {
                this.props.set_play_status(Sound.status.PAUSED);
                this.props.set_operation_code(op_code.PLAY_PAUSE);
                this.setState({first_play: false});  
                this.props.set_operation_value("pause");                              
            }

            this.setState({playPauseLock: true});

            var t = this;
            // 鎖住play pause
            setTimeout(function (){
                t.setState({playPauseLock: false});
            }, 1000);

            
            setTimeout(()=>this.send_operationLog_to_server(),100);                         
        };

        var icon;
        if (this.props.play_status === Sound.status.PLAYING) {
            icon = <i className="glyphicon glyphicon-pause"></i>;
        } else {
            icon = <i className="glyphicon glyphicon-play"></i>;
        }                
        return(
            <button onClick={onClick} id="playAndPause" className="play playandpause">
                {icon}
            </button>
        );
    }

    backward_button(){
        const onClick = (ev) => {
            this.props.set_play_status(Sound.status.PLAYING);
            this.props.set_operation_code(op_code.GO_NEXT_AUDIO);
            this.setState({button_type: "backward"});
            this.get_new_audio_id();
            if(audio_new['audio_id'] != this.props.audio_id){
                this.send_operationLog_to_server();                
            }
            window.location = this.props.backward;
        };
        return(
            <button onClick={onClick} id="chenge_sound_button" className="last-button">
              <i className="glyphicon glyphicon-step-backward"></i>
            </button>
        );
    }

    forward_button(){
        const onClick = (ev) => {
            this.props.set_play_status(Sound.status.PLAYING);
            this.props.set_operation_code(op_code.GO_NEXT_AUDIO);
            this.setState({button_type: "forward"});
            this.get_new_audio_id();
            if(audio_new['audio_id'] != this.props.audio_id){
                this.send_operationLog_to_server();                
            }
            window.location = this.props.forward;
        };
        return(
            <button onClick={onClick} id="chenge_sound_button" className="next-button">
              <i className="glyphicon glyphicon-step-forward"></i>
            </button>
        );
    }


    turn_volume(){
        const onChange = (e) => {
            this.setState({volume: e.target.value});
        };
        return(
            <div className="volume">
                <input id="vol-control1" type="range" min="0" max="100" step="1" onChange={onChange}/>
            </div>
        );
    }

    auto_next(){
        const onChange = (ev) => {
            // if (ev.target.checked){
            //     this.setState({interactiveMode: true});
            //     this.props.set_interactive(true);
            // } else {
            //     this.setState({interactiveMode: false});
            //     this.props.set_interactive(false);
            // }
        };
        return(
            <div className="auto-next">
                <div className="auto-next-button">
                    <input type="checkbox" value="1" id="AutoPlay" name="check"/>
                    <label htmlFor="AutoPlay"></label>
                </div>
                <span>自動下集</span>
            </div>
        );
    }

    interactive_mode_switch(){
        const onChange = (ev) => {
            if (ev.target.checked){
                this.setState({interactiveMode: true});
                this.props.set_interactive(true);                          
            } else {
                this.setState({interactiveMode: false});
                this.props.set_interactive(false);                      
            }
        };
        return(
            <label className="btn btn-default">
              <input type="checkbox" onChange={onChange} checked={this.state.interactiveMode}/>互動模式
            </label>
        );
    }

    seek_bar() {
        const onClick = (e) => {
            e.preventDefault();
            var seek = (e.nativeEvent.offsetX / e.target.offsetWidth) * this.state.duration;
            var seek_time = seek - this.state.position;
            if (seek_time > 0){
                this.props.set_operation_code(op_code.SEEK_BAR);
                this.props.set_operation_value(str(seek_time)); 
                this.send_operationLog_to_server();
            }
            else if(seek_time < 0){
                var neg_seek_time = this.state.position - seek;
                this.props.set_operation_code(op_code.SEEK_BAR);
                this.props.set_operation_value(str(neg_seek_time)); 
                this.send_operationLog_to_server();
            }
            this.setState({seekBarLock: true});
            this.setState({position: seek});

            var t = this;
            
            // 為了讓Update不要一直洗時間，導致使用者點了時間條後還來不及動作就被洗掉。
            // 所以如果使用者點擊了時間條，就先讓Update不要動作。
            setTimeout(function (){
                t.setState({seekBarLock: false});
            }, 500);
        };
        var style = {
            height: "10px", 
  	        position: "relative"
        };
        var style_absolute = {
  	        position: "absolute"
        };

        var pos = this.state.current / this.state.duration;

        var time = parseInt(this.state.current / 1000);
        var sec = Math.floor(time % 60).toString();
        if (sec.length == 1) {
            sec = "0" + sec;
        }
        var current = Math.floor(time / 60).toString() + ":" + sec;
        var time2 = parseInt(this.state.duration / 1000);
        var sec2 = Math.floor(time % 60).toString();
        if (sec2.length == 1) {
            sec2 = "0" + sec2;
        }
        var duration = Math.floor(time2 / 60).toString() + ":" + sec2;
        return (
            <div style={style}>
                {this.setPins()}
                <progress onClick={onClick} style={style_absolute} className="seekbar" value={pos} max="1"></progress>
                {/*<span className="current_time">{current}</span>*/}
                {/*<span className="duration_time">{duration}</span>*/}
            </div>
        );
    }

    control_row(){
        return (
            <div className="control_area">
              <div className="control_row">
                <div className="button_area">
                    {this.auto_next()}
                    {this.backward_button()}
                    {this.play_pause_button()}
                    {this.forward_button()}
                    {this.turn_volume()}
                </div>
              </div>
            </div>
        );
    }

    update(position, duration) {
        if (!this.state.seekBarLock) {
            this.props.set_current(position / 1000);
            this.props.set_duration(duration / 1000);
            this.setState({'current': position, 'duration':duration});
            if (position >= duration) {
                this.props.set_play_status(Sound.status.PAUSED);
                $(".background-grey").toggle();
                if ($("#AutoPlay:checked").length > 0) {
                    window.location = this.props.forward;
                }
            }
        }
    }

    setPin(request, i) {
        if (this.state.duration == 0) {
            return;
        }
        var style = {
            left: 100 * (request.start / (this.state.duration / 1000)) + "%",
            position: "absolute",
            width: "2px",
            height: "5px", 
            zIndex: 99,
            background: "yellow"
        };
        var onClick = function(e) {
            //alert(this.state.position);
            //this.setState({'position': request.start});
        }
        return(<div className="pin" onClick={onClick} style={style} key={"pin"+i}></div>);
    }
    
    setPins() {
        var t = this;
        var style = {
            width: "100%",
            position: "absolute",
            height: "5px"
        };
        return(
            <div className="pins" style={style}>
                {this.props.questions.map(function (request, i) {
                    return(t.setPin(request, i));
                })}
            </div>);
    }

    send_operationLog_to_server() {
        this.setState({play_log_id: obj['playlog_id']});
        this.setState({load_playlog: true});
        console.log(obj['playlog_id']);        
        console.log(this.props.operation_code);
        console.log(this.props.operation_value);
        $.ajax({
            type: 'POST',
            url: '/radio/add_oplog',
            data: JSON.stringify({
                'play_log' : obj['playlog_id'],
                'operation_code' : this.props.operation_code,
                'operation_value' : this.props.operation_value
            }),
            contentType: "application/json; charset=utf-8",
        });
        
    }

    get_new_audio_id(){
        $.ajax({
            type: 'POST',
            url: '/radio/get_new_audio_id',
            data: JSON.stringify({
                'audio_id' : this.props.audio_id,
                'button_type' : this.state.button_type
            }),
            contentType: "application/json; charset=utf-8",
        }).done(function(msg) {
            var json = msg;
            audio_new = JSON.parse(json);
            console.log(audio_new)
        });        
        this.props.set_operation_value(audio_new['audio_id']); 
    }
    
    render() {       
        if (!this.state.load_playlog && this.props.audio_id && !id_loading){
            id_loading=true
            $.ajax({
                type: 'POST',
                url: '/radio/get_playlog',
                data: JSON.stringify({
                    'audio_id' : this.props.audio_id
                }),
                contentType: "application/json; charset=utf-8",
            }).done(function(msg) {
                var json = msg;
                obj = JSON.parse(json);
                console.log(obj);
            });
        }

        window.onbeforeunload  = CallBeforeExit;
        function CallBeforeExit() {
            $.ajax({
                type: 'POST',
                async: false,
                url: '/radio/add_playlog_end_time',
                data: JSON.stringify({
                    'playLogId' : obj['playlog_id']
                }),
                contentType: "application/json; charset=utf-8"
            });
        }

        return (
            <div id="audioPlayer">
                {this.seek_bar()}
                {this.control_row()}                
              <Sound url={this.props.src}
                     autoLoad={true}
                     playStatus={this.props.play_status}
                     playFromPosition={this.state.position}
                     volume={this.state.volume}
                     onPlaying={({position, duration}) => this.update(position, duration)}
                     />
            </div>
        );
    }
};
