import React, { MouseEvent, RefObject } from 'react';
import productData, { autofeatured_str } from '../dataTypes';
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
  isScrollLoadEnabled: boolean;
}



class AutofeaturedApp extends React.Component<Props, State> {
  showMbtnRef: RefObject<HTMLAnchorElement>;

  constructor(props: Props, state: State) {
    super(props);

    this.showMbtnRef = React.createRef();

    this.state = {
      selectedTab: autofeatured_str,
      isSearchPage: false,
      isCatPage: false,
      isProductPage: false,
      productsLoaded: 0,
      prodId: undefined,
      autof_settings: undefined,
      isDisplaying: false,
      displayData: [],
      isLoading: false,
      isScrollLoadEnabled: false
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

    // Debug mode
    (window as any).AutofeaturedApp = this;

    // Set auto load on scroll
    window.addEventListener('scroll', () => {
      if (this.showMbtnRef.current) {
        let btn_rect = this.showMbtnRef.current.getBoundingClientRect();
        if (btn_rect.top > 2500) {
          this.setState({ isScrollLoadEnabled: true })
        }
        if (btn_rect.top < 1500 && this.state.isScrollLoadEnabled) {
          this.loadAutoFeatured();
          this.setState({ isScrollLoadEnabled: false });
        }
      }
    });

    // Save all data

    let isDisplaying = true;
    if (!prodId || !autof_settings) {
      console.log('loadAutoFeatured: Invalid settings');
      isDisplaying = false;
    }

    if (isDisplaying) {
      this.setState({
        selectedTab: autofeatured_str,
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
  }


  loadAutoFeatured = () => {

    if (!this.state.isDisplaying) {
      console.log('loadAutoFeatured: Invalid settings');
      return;
    }

    this.setState({ isLoading: true });

    let request_url = '';
    if (this.state.selectedTab === autofeatured_str) {
      request_url = 'index.php?route=extension/module/autofeatured/ajaxGetProduct';
    }
    else {
      request_url = 'index.php?route=extension/module/autofeatured/ajaxGetImgMatched';
    }

    var formData = new FormData();
    formData.append('prodId', this.state.prodId + '');
    formData.append('autof_settings', this.state.autof_settings + '');
    formData.append('productsLoaded', this.state.productsLoaded + '');

    fetch(request_url, {
      method: 'post',
      body: formData
    }).then((res) => res.text())
      .then((text) => text.length ? displayData(text) : displayData('responce failed'))
      .catch((error) => {
        console.log('err:', error);
        this.setState({ isLoading: false });
        if (this.showMbtnRef.current) this.showMbtnRef.current.style.display = 'none';
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

        products.forEach(prod => {
          disArr.push(prod);
        })

        return {
          displayData: disArr,
          productsLoaded: prevState.productsLoaded + 40,
          isLoading: false
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
      setTabTo = autofeatured_str;
    }
    else {
      setTabTo = 'imgmatch'
    }

    if (this.state.selectedTab != setTabTo) {
      this.setState({
        displayData: [],
        selectedTab: setTabTo,
        productsLoaded: 0
      }, this.loadAutoFeatured)
    }


  }

  render() {

    let autofeatured_btn_cls = '';
    let imagematch_btn_cls = '';
    this.state.selectedTab == autofeatured_str ?
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
        <div className="row">
          <h3 className="row autofeaturedText ">
            <a id="autofeatured_btn"
              className={autofeatured_btn_cls}
              onClick={this.changeTabHandler}
              key="1">Рекомендуемые товары</a>
            <a id="imagematch_btn"
              className={imagematch_btn_cls}
              onClick={this.changeTabHandler}
              key="2">Визуально похожие товары</a>
          </h3>

          <div className="row"
            id="products-load-container">{this.state.displayData}</div>

          <div id="showmore" className="showmoreBtn col-sm-12">
            <a id="showmore-text-btn"
              onClick={this.loadAutoFeatured}
              style={btnCSS}
              ref={this.showMbtnRef} >Показать еще</a>
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
