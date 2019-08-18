import React from 'react';
import ReactDOM from 'react-dom';
import AutofeaturedApp from './AutofeaturedApp';
import * as serviceWorker from './serviceWorker';
import PageHandler from './showmore'

/*
$(document).ready(function () {

    let pageHandler = new PageHandler();

    window.pageHandler = pageHandler;
    
    pageHandler.init();
});*/

ReactDOM.render(<AutofeaturedApp />, document.getElementById('root'));





// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
