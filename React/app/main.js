import React from 'react';
import ReactDOM from 'react-dom';
import QuestionTable from './question-form';
import RadioUI from './radio-ui';
import Caption from './caption'
import Sound from 'react-sound';

export default class RadioQuestion extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            current: 0,
            audio: "",
            interactiveMode: true,
            questions: [],
            playStatus: Sound.status.PAUSED,
            forward: "#",
            backward: "#",
            operation_code: 0,
            operation_value: "",
            "title":"",
            "depiction":"",
            "logo":"",
            keywords: [],
            "duration":"",
            audio_summary:""
        };
    }

    componentDidMount() {
        this.serverRequest = $.getJSON(window.url + "?t=" + Date.now(), function (result) {
            this.setState({
                channel_id: result.channel_id,
                channel_name: result.channel_name,
                audio_id: result.audio_id,
                audio_name: result.audio_name,
                audio: result.audio,
                questions: result.questions,
                forward: result.forward,
                backward: result.backward,
                operation_code: result.operation_code,
                operation_value: result.operation_value,           
                title: result.title,
                depiction: result.depiction,
                keywords: result.keywords,
                logo: result.logo,
                audio_summary: result.audio_summary
            });
        }.bind(this));
    }

    componentWillUnmount() {
        this.serverRequest.abort();
    }

    render() {
    return(
            <div>
                <div className="grey">
                    <div className="program-info">
                        <div className="program-title">{this.state.audio_name}</div>
                        <div className="program-album">{this.state.channel_name}</div>
                        <Caption 
                            current={this.state.current}
                            duration={this.state.duration}
                            audio_id={this.state.audio_id}/>
                    </div>
                    <div className="controller">
                        <RadioUI
                            set_current={(current)=>this.setState({'current': current})}
                            set_interactive={(interactive)=>this.setState({'interactiveMode': interactive})}
                            play_status={this.state.playStatus}
                            set_play_status={(play_status)=>this.setState({'playStatus': play_status})}
                            set_operation_code={(operation_code)=>this.setState({'operation_code': operation_code})}                
                            set_operation_value={(operation_value)=>this.setState({'operation_value': operation_value})}                                            
                            operation_code={this.state.operation_code}
                            operation_value={this.state.operation_value}
                            src={this.state.audio}
                            title={this.state.title}
                            forward={this.state.forward}
                            backward={this.state.backward}
                            logo={this.state.logo}
                            set_duration={(duration)=>this.setState({'duration': duration})}
                            questions={this.state.questions}
                            audio_id={this.state.audio_id}/>
                    </div>
                </div>

                <QuestionTable
                        set_play_status={(play_status)=>this.setState({'playStatus': play_status})}
                        current={this.state.current}
                        is_interactive={this.state.interactiveMode}
                        duration={this.state.duration}
                        depiction={this.state.depiction}
                        audio_name={this.state.audio_name}
                        channel_name={this.state.channel_name}
                        questions={this.state.questions}
                        channel_id={this.state.channel_id}
                        keywords={this.state.keywords}
                        audio_id={this.state.audio_id}
                        audio_summary={this.state.audio_summary} 
                        />

                <div className="clearfix hidden-xs"></div>
				
				<div className="player_feet_group">
					<div className="player-feet"></div>
					<div className="player-feet2"></div>
				</div>
            </div>
        );
    }
}
ReactDOM.render(<RadioQuestion />,$("#main")[0]);
