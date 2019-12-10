import React, { MouseEvent, RefObject } from 'react';
import productData, { autofeatured_str, autofeaturedURL, autofeaturedIMGMatchURL, autofeaturedIMGMatch_str } from '../dataTypes';
import Product from './Product'

interface Props {
  prodId: string | undefined;
}
interface State {
  selectedTab: typeof autofeaturedIMGMatch_str | typeof autofeatured_str;
  isSearchPage: boolean;
  isCatPage: boolean;
  isProductPage: boolean;
  productsLoaded: number;
  prodId: undefined | number;
  settings: string | undefined;
  isDisplaying: boolean;
  displayData: JSX.Element[];
  isLoading: boolean;
  isScrollLoadEnabled: boolean;
}



export class Autofeatured extends React.Component<Props, State> {
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
      settings: undefined,
      isDisplaying: false,
      displayData: [],
      isLoading: false,
      isScrollLoadEnabled: false
    }
  }

  componentDidMount() {

    // Load settings
    const autofSettingsDiv: Element | null = document.getElementById('autofeatured_settings');
    const settings: string | undefined = (autofSettingsDiv) ? (autofSettingsDiv as HTMLDivElement).innerText : undefined;

    const isSearchPage: Element | null = document.querySelector('h2.search-header');
    const isCatPage: Element | null = document.querySelector('h1.cat-header');
    const isProductPage: Element | null = document.querySelector('h1.product-header');
    let prodId = undefined;

    if (isSearchPage || isCatPage) {
      const productArr = Array.from(document.querySelectorAll('#res-products .row .product-layout'));
      if (productArr.length < 20 && productArr.length > 0) {
        const linkProdOncl = (productArr[0] as any).querySelector('.quick-view a').getAttribute('onclick');
        prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
      }
    }
    if (isProductPage) {
      if (this.props.prodId != undefined && this.props.prodId != "") {
        prodId = Number(this.props.prodId)
      }
    }

    //console.log('isSearchPage', isSearchPage, 'isCatPage', isCatPage, 'isProductPage', isProductPage, 'prodId', prodId);
    //console.log('settings', settings);

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
    if (!prodId || !settings) {
      console.log('loadAutoFeatured: Invalid settings. prodId:', prodId, ' settings: ', settings);
      isDisplaying = false;
    }

    if (isDisplaying) {
      this.setState({
        selectedTab: autofeatured_str,
        settings: settings,
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
      console.log('loadAutoFeatured: Invalid settings', this.state);
      return;
    }

    this.setState({ isLoading: true });

    const request_url: string = this.state.selectedTab === autofeatured_str ? autofeaturedURL : autofeaturedIMGMatchURL;

    const formData = new FormData();
    formData.append('prodId', this.state.prodId + '');
    formData.append('autof_settings', this.state.settings + '');
    formData.append('productsLoaded', this.state.productsLoaded + '');

    try {
      fetch(request_url, {
        method: 'post',
        body: formData
      }).then((res) => res.text())
        .then((text) => text.length ? this.displayData(text) : this.displayData('responce failed'))
        .catch((error) => {
          console.log('err:', error);
          this.setState({ isLoading: false });
          if (this.showMbtnRef.current) this.showMbtnRef.current.style.display = 'none';
        });
    } catch (e) {
      console.log(e);
    }
  }

  displayData = (text: string) => {

    //console.log('text1');
    //console.log(text);

    const data: productData[] = JSON.parse(text);

    const products: JSX.Element[] = [];

    if (data !== undefined && Array.isArray(data) && data.length > 0) {
      data.forEach((data: productData): void => {
        products.push((
          <Product data={data} />
        ));
      });
    }

    //console.log('products');
    //console.log(products);

    const imgLazyLoadInit = () => {
      try {
        const func = ((window as any).pageHandler as any).lazyLoad;
        setTimeout(func, 1000);
      } catch (error) {
        console.error(error);
      }
    };

    this.setState((prevState) => {
      const disArr = [...prevState.displayData];
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


  changeTabHandler = (event: MouseEvent<HTMLElement>) => {
    const setTabTo = (event.target as HTMLElement).id === 'autofeatured_btn' ? autofeatured_str : autofeaturedIMGMatch_str;

    if (this.state.selectedTab !== setTabTo) {
      this.setState({
        displayData: [],
        selectedTab: setTabTo,
        productsLoaded: 0
      }, this.loadAutoFeatured)
    }


  }

  render() {

    const autofeatured_btn_cls = this.state.selectedTab === autofeatured_str ? 'autofeatured-selected' : '';
    const imagematch_btn_cls = this.state.selectedTab === autofeatured_str ? '' : 'autofeatured-selected';

    let loaderCSS, btnCSS;
    if (this.state.isLoading) {
      loaderCSS = {};
      btnCSS = { display: "none" }
    }
    else {
      loaderCSS = { display: "none" };
      btnCSS = {};
    }

    if (!this.state.isDisplaying) {
      return (
        <div className="App"></div>
      )
    }

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
}

