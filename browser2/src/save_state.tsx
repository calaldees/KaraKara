
export class SaveStateManager {
    storage: string;
    last_saved: {};
    keys: Array<string>;

    constructor(state, keys) {
        this.storage = "saved_state";
        this.last_saved = {};
        this.keys = keys;

        if(!("version" in keys)) {
            keys.push("version");
        }
        let state_version = state.version || 1;
        let saved_state = JSON.parse(window.localStorage.getItem(this.storage) || "{}");
        if(state_version != saved_state.version) {
            window.localStorage.removeItem(this.storage);
            saved_state = {};
        }
        keys.map(x => state[x] = saved_state[x] || state[x]);
        keys.map(x => this.last_saved[x] = saved_state[x]);
    }

    save_state_if_changed(state) {
        let changed = this.keys.filter(x => this.last_saved[x] != state[x]);
        if(changed.length > 0) {
            changed.map(x => this.last_saved[x] = state[x]);
            // console.log("Changed", changed, "saving state:", this.last_saved);
            window.localStorage.setItem(this.storage, JSON.stringify(this.last_saved));
        }
    }    
};
