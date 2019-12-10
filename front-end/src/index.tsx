import React from 'react';
import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';
import { Autofeatured } from './components/Autofeatured';
import PageHandler from './category-js/showmore';

window.addEventListener("load", loadApp);

function loadApp() {

    let pageHandler = new PageHandler();

    (window as any).pageHandler = pageHandler;

    pageHandler.init();


    let prodId: string | undefined = undefined;
    let LoadMoreContainer = document.getElementById('LoadMoreHere');

    if (LoadMoreContainer) {
        prodId = LoadMoreContainer.innerText;
        console.log('prodId', prodId)

        ReactDOM.render(<Autofeatured prodId={prodId} />, LoadMoreContainer);
    }
}

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
