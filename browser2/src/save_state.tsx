// Stolen from @zaceno's Hyperapp Code-Along
// https://www.youtube.com/watch?v=QqUr_NM6P_Y

function _stateLoader(dispatch, props) {
    let data = localStorage.getItem(props.key);
    if(!data) return;
    data = JSON.parse(data);
    dispatch(props.action, data);
}

export const LocalStorageLoader = (key, action) => [_stateLoader, {key, action}];

function _stateWatcher(dispatch, props) {
    requestAnimationFrame((_) => localStorage.setItem(props.key, JSON.stringify(props.value)));
    return () => {};
}

export const LocalStorageSaver = (key, value) => [_stateWatcher, {key, value}];