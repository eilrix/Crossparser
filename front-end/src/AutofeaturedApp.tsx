import React, { MouseEvent } from 'react';
import productData from './dataTypes';
import Product from './Product'

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
  isLoading: boolean;
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
      displayData: [],
      isLoading: false
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

    //console.log('isSearchPage', isSearchPage, 'isCatPage', isCatPage, 'isProductPage', isProductPage, 'prodId', prodId);
    //console.log('autof_settings', autof_settings);

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
        productsLoaded: 0,
        prodId: prodId,
        isDisplaying: isDisplaying,
        displayData: []
      }, this.loadAutoFeatured);
    }
    // Debug mode
    (window as any).AutofeaturedApp = this;
  }


  loadAutoFeatured = () => {

    if (!this.state.isDisplaying) {
      console.log('loadAutoFeatured: Invalid settings');
      return;
    }

    var formData = new FormData();
    formData.append('prodId', this.state.prodId + '');
    formData.append('autof_settings', this.state.autof_settings + '');
    formData.append('productsLoaded', this.state.productsLoaded + '');

    fetch('index.php?route=extension/module/autofeatured/ajaxGetProduct', {
      method: 'post',
      body: formData
    }).then((res) => res.text())
      .then((text) => text.length ? displayData(text) : displayData('responce failed'))
      .catch((error) => {
        console.log('err:', error);
      });

    let displayData = (text: string) => {
      //console.log('text1');
      //console.log(text);

      let data: productData[] = JSON.parse(text);

      let products: JSX.Element[] = [];

      if (data != undefined && data.length > 0) {
        products = data.map((data: productData): JSX.Element => {
          return (
            <Product data={data} />
          )
        })
      }

      //console.log('products');
      //console.log(products);

      this.setState((prevState) => {
        let disArr = prevState.displayData;

        disArr.push(<div key={disArr.length}>{products}</div>);

        return {
          displayData: disArr,
          productsLoaded: prevState.productsLoaded + 40
        };
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


  changeTabHandler = (event: MouseEvent<HTMLElement>) => {

    let setTabTo = ''
    if ((event.target as HTMLElement).id == 'autofeatured_btn') {
      setTabTo = 'autofeatured-selected';
    }
    else {
      setTabTo = 'imgmatch-selected'
    }

    if (this.state.selectedTab != setTabTo) {
      this.setState({
        displayData: [],
        selectedTab: setTabTo
      }, this.loadAutoFeatured)
    }


  }

  render() {

    let autofeatured_btn_cls = '';
    let imagematch_btn_cls = '';
    this.state.selectedTab == 'autofeatured' ?
      autofeatured_btn_cls = 'autofeatured-selected' :
      imagematch_btn_cls = 'autofeatured-selected';

    let loaderCSS, btnCSS;
    if (this.state.isLoading) {
      loaderCSS = {};
      btnCSS = { display: "none" }
    }
    else {
      loaderCSS = { display: "none" };
      btnCSS = {};
    }

    if (this.state.isDisplaying) {
      return (
        <div className="App">
          <h3 className="autofeaturedText ">
            <a id="autofeatured_btn" 
            className={autofeatured_btn_cls} 
            onClick={this.changeTabHandler}
            key="1">Рекомендуемые товары</a>
            <a id="imagematch_btn" 
            className={imagematch_btn_cls} 
            onClick={this.changeTabHandler}
            key="2">Визуально похожие товары</a>
          </h3>

          <div id="products-load-container">{this.state.displayData}</div>

          <div id="showmore" className="showmoreBtn col-sm-12">
            <a id="showmore-text-btn" onClick={this.loadAutoFeatured} style={btnCSS}>Показать еще</a>
            <img id="load-more-gif" style={loaderCSS} src="image/loading.gif" />
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
