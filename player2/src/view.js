import { h } from "hyperapp";  // JSX will be turned into h by rollup
import { timedelta_str, get_attachment, get_tag, s_to_mns, get_hostname, get_queue_id } from "./util.js";
const show_tracks = 5;


// ====================================================================
// Common components
// ====================================================================

function _lineStyle(item, state) {
    const ts = state.progress * 1000;
    if(!state.playing) return "present";
    if(item.text === "-") return "past";
    if(item.start < ts && item.end > ts) return "present";
    if(item.end < ts) return "past";
    if(item.start > ts) return "future";
}

const Lyrics = ({state}) => (
    <div className={"lyrics"}>
        <ol>
            {state.queue[0].track.lyrics.map((item) =>
                <li key={item.start} className={_lineStyle(item, state)}>
                    <span>{item.text}</span>
                </li>
            )}
        </ol>
    </div>
);


// ====================================================================
// Screens
// ====================================================================

const ClickScreen = ({state, actions}) => (
    <div className={"screen_title"}>
        <h1 onclick={() => actions.click()}>Click to Activate</h1>
    </div>
);

const TitleScreen = ({state, actions}) => (
    <div className={"screen_title"}>
        <h1>{state.settings["karakara.player.title"]}</h1>
        <div id="join_info">
            Join at <strong>{get_hostname()}</strong> -
            Queue is <strong>{get_queue_id()}</strong>
        </div>
    </div>
);

const PreviewScreen = ({state, actions}) => (
    <div className={"screen_preview"}>
        <div className="preview_holder">
            <video src={get_attachment(state, state.queue[0].track, 'preview')}
                   poster={get_attachment(state, state.queue[0].track, 'thumbnail')}
                   autoPlay={true}
                   onloadstart={e => {e.target.volume = state.settings["karakara.player.video.preview_volume"]}}
                   loop={true} />
            <video src={get_attachment(state, state.queue[0].track, 'video')}
                   preload={"auto"} muted={true} style={{display: "none"}} />
        </div>
        <div id="playlist" key={"playlist"}>
            <ol>
                {state.queue.slice(0, show_tracks).map((item) =>
                    <li key={item.time_touched}>
                        <img src={get_attachment(state, item.track, 'image')} />
                        <p className='title'>{get_tag(item.track.tags.title)}</p>
                        <p className='from'>{get_tag(item.track.tags.from)}</p>
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
        <div id="join_info" key={"join_info"}>
            Join at <strong>{get_hostname()}</strong> -
            Queue is <strong>{get_queue_id()}</strong>
            {state.settings["karakara.event.end"] &&
                <span><br/>Event ends at <strong>{state.settings["karakara.event.end"]}</strong></span>
            }
        </div>
    </div>
);

const VideoScreen = ({state, actions}) => (
    <div className={"screen_video"}>
        <video src={get_attachment(state, state.queue[0].track, 'video')}
               autoPlay={true}
               ontimeupdate={(e) => actions.set_progress(e.target.currentTime)}
               onended={() => actions.send_ended("ended")}
        />
        <div id="seekbar" style={{
            left: ((state.progress / state.queue[0].track.duration) * 100) + "%"
        }} />
        <div id="pimpkk" className="pimp">
            KaraKara
        </div>
        <div id="pimpsong" className="pimp">
            {get_tag(state.queue[0].track.tags.title)}
            <br/>Performed by {state.queue[0].performer_name}
        </div>
        {/* too much on screen at once?
        <div id="pimpcontributor" className="pimp">
            Contributed by {get_tag(state.queue[0].track.tags.contributor)}
        </div>
        */}
        {(state.settings["karakara.player.subs_on_screen"] && state.queue[0].track.lyrics) ?
            <Lyrics state={state} /> :
            null
        }

    </div>
);

const PodiumScreen = ({state, actions}) => (
    <div className={"screen_podium"}>
        <h1>{state.queue[0].performer_name} - {get_tag(state.queue[0].track.tags.title)}</h1>

        {/*
        if we have lyrics, show them, else show the video,
        give the video key=playing so that it creates a new
        object when switching from preview to play
         */}
        {state.queue[0].track.lyrics ?
            <Lyrics state={state} /> :
            <div className="preview_holder">
                <video src={get_attachment(state, state.queue[0].track, 'video')}
                       autoPlay={true} muted={!state.playing}
                       key={state.playing}
                />
            </div>
        }

        {state.playing ?
            <div className={"progressBar"}
                 style={{"background-position": (100 - (state.progress / state.queue[0].track.duration * 100))+"%"}}>
                Track Playing
                <small>(
                    {s_to_mns(state.progress)}
                    {' '}/{' '}
                    {s_to_mns(state.queue[0].track.duration)}
                )</small>
            </div> :
            <div className={"startButton"} onclick={() => actions.send("play")}
                 style={{"background-position": (100 - (state.progress / state.settings["karakara.player.autoplay"] * 100))+"%"}}>
                <span>
                    Press to Start
                    {state.settings["karakara.player.autoplay"] === 0 ?
                        <small>(autoplay disabled)</small> :
                        <small>(autoplay in {Math.ceil(state.settings["karakara.player.autoplay"] - state.progress)} seconds)</small>
                    }
                </span>
            </div>
        }
    </div>
);


// ====================================================================
// Decide which screen to use based on current state
// ====================================================================

function view(state, actions) {
    let screen = <div>Unknown state :(</div>;

    if(!state.clicked)
        screen = <ClickScreen state={state} actions={actions} />;
    else if(state.queue.length === 0)
        screen = <TitleScreen state={state} actions={actions} />;
    else if(window.location.hash === "#podium")
        screen = <PodiumScreen state={state} actions={actions} />;
    else if(state.queue.length > 0 && !state.playing)
        screen = <PreviewScreen state={state} actions={actions} />;
    else if(state.queue.length > 0 && state.playing)
        screen = <VideoScreen state={state} actions={actions} />;

    return <div className={"theme-" + state.settings["karakara.player.theme"]}>
        {screen}
    </div>;
}

export { view };