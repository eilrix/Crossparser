import React from 'react';


interface Props {
  prodId: string | undefined;
}
interface State {
  selectedTab: string;
  isSearchPage: boolean;
  isCatPage: boolean;
  isProductPage: boolean;
  productsLoaded: number;
  prodId: undefined | number;
  autof_settings: string | undefined;
  isDisplaying: boolean;
  displayData: JSX.Element[];
}

class AutofeaturedApp extends React.Component<Props, State> {

  constructor(props: Props, state: State) {
    super(props);

    this.state = {
      selectedTab: 'autofeatured',
      isSearchPage: false,
      isCatPage: false,
      isProductPage: false,
      productsLoaded: 0,
      prodId: undefined,
      autof_settings: undefined,
      isDisplaying: false,
      displayData: []
    }
  }

  componentDidMount() {

    let autof_settingsDiv = document.getElementById('autofeatured_settings');
    let autof_settings: string | undefined;
    autof_settingsDiv ? autof_settings = autof_settingsDiv.innerText : autof_settings = undefined;

    let isSearchPage = document.querySelector('h2.search-header');
    let isCatPage = document.querySelector('h1.cat-header');
    let isProductPage = document.querySelector('h1.product-header');
    let prodId = undefined;

    if (isSearchPage || isCatPage) {
      let productsList = document.querySelectorAll('#res-products .row .product-layout');
      if (productsList) {
        let productArr = Array.from(productsList);
        if (productArr.length < 20 && productArr.length > 0) {

          let linkProdOncl = (productArr[0] as any).querySelector('.quick-view a').getAttribute('onclick');
          prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
        }
      }
    }
    if (isProductPage) {
      if (this.props.prodId != undefined && this.props.prodId != "") {
        prodId = Number(this.props.prodId)
      }
    }

    console.log('isSearchPage', isSearchPage, 'isCatPage', isCatPage, 'isProductPage', isProductPage, 'prodId', prodId);
    console.log('autof_settings', autof_settings);

    let isDisplaying = true;
    if (!prodId || !autof_settings) {
      console.log('loadAutoFeatured: Invalid settings');
      isDisplaying = false;
    }

    if (isDisplaying) {
      this.setState({
        selectedTab: 'autofeatured',
        autof_settings: autof_settings,
        isSearchPage: isSearchPage ? true : false,
        isProductPage: isProductPage ? true : false,
        isCatPage: isCatPage ? true : false,
        prodId: prodId,
        isDisplaying: isDisplaying,
        displayData: []
      }, this.loadAutoFeatured);
    }
    (window as any).AutofeaturedApp = this;
  }


  loadAutoFeatured = () => {

    if (!this.state.isDisplaying) {
      console.log('loadAutoFeatured: Invalid settings');
      return;
    }

    var formData = new FormData();
    formData.append('prodId', this.state.prodId + '');
    formData.append('autof_settings', (this.state.autof_settings as string));
    formData.append('productsLoaded', '0');

    (window as any).formData = formData;
    (window as any).autof_settings = this.state.autof_settings;

    fetch('index.php?route=extension/module/autofeatured/ajaxGetProduct', {
      method: 'post',
      body: formData
    }).then((res) => res.text())
      .then((text) => text.length ? displayData(text) : displayData('responce failed'))
      .catch((error) => {
        console.log('err:', error);
      });

    let displayData = (text: string) => {
      console.log(text);
      var regex = /onclick=/gi;
      text = text.replace(regex, 'onClick=');
      
      this.setState((prevState) => {
        let disArr = prevState.displayData;

        disArr.push(<div key={disArr.length}>{require('html-react-parser')(text)}</div>);

        return { displayData: disArr };
      }, imgLazyLoadInit)
    }

    let imgLazyLoadInit = () => {
      try {
        let func = ((window as any).pageHandler as any).lazyLoad;
        setTimeout(func, 1000);
      } catch (error) {
        console.error(error);
      }
    }


  }

  render() {

    if (this.state.isDisplaying) {
      return (
        <div className="App">
          <h3 className="autofeaturedText autofeatured-selected">
            <a id="autofeatured_btn">Рекомендуемые товары</a>
            <a id="imagematch_btn">Визуально похожие товары</a>
          </h3>

          <div id="products-load-container">{this.state.displayData}</div>

          <div id="showmore" className="showmoreBtn col-sm-12">
            <a id="showmore-text-btn" onClick={this.loadAutoFeatured}>Показать еще</a>
            <img id="load-more-gif" style={{ display: "none" }} src="image/loading.gif" />
          </div>

        </div>
      );
    }
    else {
      return (
        <div className="App"></div>
      )
    }
  }
}

export default AutofeaturedApp;
