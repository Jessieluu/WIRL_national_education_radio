import React from 'react';
import ReactDOM from 'react-dom';
import classNames from 'classnames';

var obj ={};
let id_loading = undefined;
export default class Caption extends React.Component{
    constructor(props){
        super(props);

        this.state = {
            caption: '',
            startTime: 0,
            endTime: 0,
            load_caption: false,
        }
    }

    caption(){
        var time = this.props.current;
        var timeFix = Math.floor(time * 100) / 100  
        var caption = ""
        for(let i in obj){
            if (timeFix > obj[i].start_time && timeFix < obj[i].end_time)
                caption = obj[i].caption;
        }

        return(<div className="program-subtitle">
                {caption}
        </div>);
    }

    render(){
        if (!this.state.load_playlog && this.props.audio_id && !id_loading){
            id_loading=true
            $.ajax({
                type: 'POST',
                url: '/radio/captionGet',
                data: JSON.stringify({
                    'audio_id' : this.props.audio_id   
                    // update
                }),
                contentType: "application/json; charset=utf-8",
            }).done(function(msg) {
                var json = msg;
                obj = JSON.parse(json);
                console.log(obj);
            });
        }

        return (
            <div>
                {this.caption()}
            </div>
        );
    }
}