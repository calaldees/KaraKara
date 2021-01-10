function errorParser(dispatch, response) {
    response.json().then(json => {
        dispatch((state) => ({...state, notification: json.messages[0]}))
    }).catch(err => {
        console.log(err);
        dispatch((state) => ({...state, notification: "Internal Error"}))
    });
}
export const DisplayErrorResponse = ({response}) => [errorParser, response];
