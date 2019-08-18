import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as serviceWorker from './serviceWorker';
import AutofeaturedApp from './AutofeaturedApp';


window.addEventListener("load", loadApp);

function loadApp() {
    
    let prodId: string | undefined = undefined;
    let LoadMoreHere = document.getElementById('LoadMoreHere');
    console.log('LoadMoreHere', LoadMoreHere);
    
    if (LoadMoreHere) {
        prodId = LoadMoreHere.innerText;
        console.log('prodId', prodId)
    
        ReactDOM.render(<AutofeaturedApp prodId={prodId} />, LoadMoreHere);
    }
}

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
