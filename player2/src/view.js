import { h } from "hyperapp";  // JSX will be turned into h by rollup
import { timedelta_str, get_attachment, s_to_mns } from "./util.js";
const show_tracks = 5;


/* ====================================================================
Rendering
==================================================================== */

const TitleScreen = ({state, actions}) => (
    <div className={"screen_title"}>
        <div className="info"><div><h1>{state.settings["karakara.player.title"]}</h1></div></div>
        <div className="join_info">
            Join at <span>{state.settings["HOSTNAME"]}</span> -
            Queue is <span>{state.settings["QUEUE_ID"]}</span>
        </div>
    </div>
);

const PreviewScreen = ({state, actions}) => (
    <div className={"screen_preview"}>
        <div className="preview_holder">
            <video src={get_attachment(state.queue[0].track, 'preview')}
                   poster={get_attachment(state.queue[0].track, 'thumbnail')}
                   autoPlay={true} loop={true} muted={true} />
            <video src={get_attachment(state.queue[0].track, 'video')}
                   preload={"auto"} muted={true} style={{display: "none"}} />
        </div>
        <div id="playlist" key={"playlist"}>
            <ol>
                {state.queue.slice(0, show_tracks).map((item) =>
                    <li key={item.time_touched}>
                        <img src={get_attachment(item.track, 'image')} />
                        <p className='title'>{item.track.tags.title}</p>
                        <p className='from'>{item.track.tags.from}</p>
                        <p className='performer'>{item.performer_name}</p>
                        <p className='time'><span>{timedelta_str(item.total_duration*1000)}</span></p>
                    </li>)}
            </ol>
        </div>
        {state.queue.length > show_tracks &&
        <div id="playlist_obscured" key={"playlist_obscured"}>
            <ul>
                {state.queue.slice(show_tracks).map((item) =>
                    <li key={item.time_touched}>{item.performer_name}</li>)}
            </ul>
        </div>
        }

        {/* key= to make sure this element stays put while the above may disappear */}
        <div className="join_info" key={"join_info"}>
            Join at <span>{state.settings["HOSTNAME"]}</span> -
            Queue is <span>{state.settings["QUEUE_ID"]}</span>
            <br/>Event ends at <span>{state.settings["karakara.event.end"]}</span>
        </div>
    </div>
);

const VideoScreen = ({state, actions}) => (
    <div className={"screen_video"}>
        <video src={get_attachment(state.queue[0].track, 'video')}
               autoPlay={true}
               ontimeupdate={(e) => actions.update_progress(e.target.currentTime)}
               onended={() => actions.dequeue()}
        />
        <div id="seekbar" style={{
            left: ((state.progress / state.queue[0].track.duration) * 100) + "%"
        }} />
        <div id="pimpkk" className="pimp">
            KaraKara
        </div>
        <div id="pimpsong" className="pimp">
            {state.queue[0].track.tags.title}
            <br/>Performed by {state.queue[0].performer_name}
        </div>
        {/* too much on screen at once?
        <div id="pimpcontributor" className="pimp">
            Contributed by {state.queue[0].track.tags.contributor}
        </div>
        */}
    </div>
);

function _lineStyle(item, state) {
    const ts = state.progress * 1000;
    if(!state.playing) return "present";
    if(item.text === "-") return "past";
    if(item.start < ts && item.end > ts) return "present";
    if(item.end < ts) return "past";
    if(item.start > ts) return "future";
}

const PodiumScreen = ({state, actions}) => (
    <div className={"screen_podium"}>
        <h1>{state.queue[0].performer_name} - {state.queue[0].track.tags.title}</h1>

        <div className={"lyrics"}>
            <ol>
                {state.queue[0].track.lyrics.map((item) =>
                    <li key={item.start} className={_lineStyle(item, state)}>{item.text}</li>
                )}
            </ol>
        </div>

        {state.playing ?
            <div className={"progressBar"}
                 style={{"background-position": (100 - (state.progress / state.queue[0].track.duration * 100))+"%"}}>
                Track Playing
                <small>(
                    {s_to_mns(state.progress)}
                    {' '}/{' '}
                    {s_to_mns(state.queue[0].track.duration)}
                )</small>
            </div>
            :
            <div className={"startButton"} onclick={() => actions.play()}
                 style={{"background-position": (100 - (state.progress / state.settings["karakara.player.autoplay"] * 100))+"%"}}>
                <span>
                    Press to Start
                    {state.settings["karakara.player.autoplay"] === 0 ?
                        <small>(autoplay disabled)</small> :
                        <small>(autoplay in {Math.ceil(state.settings["karakara.player.autoplay"] - state.progress)} seconds)</small>}
                </span>
            </div>
        }
    </div>
);

function view(state, actions) {
    let screen = <div>Unknown state :(</div>;

    if(window.location.hash === "#podium") screen = <PodiumScreen state={state} actions={actions} />;
    else if(state.queue.length === 0 && !state.playing) screen = <TitleScreen state={state} actions={actions} />;
    else if(state.queue.length > 0 && !state.playing) screen = <PreviewScreen state={state} actions={actions} />;
    else if(state.playing) screen = <VideoScreen state={state} actions={actions} />;

    return <div className={"theme-" + state.settings["karakara.player.theme"]}>
        {screen}
    </div>
}

export { view };