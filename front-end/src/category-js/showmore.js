import {
    fixMegafilterPagination,
    initMegafilterOnWideScreen,
    attachMFandCategs
} from './megafilterPatch';

var $ = require("jquery");


class PageHandler {

    constructor() {
        this.fixMegafilterPagination = fixMegafilterPagination.bind(this);
        this.initMegafilterOnWideScreen = initMegafilterOnWideScreen.bind(this);
        this.attachMFandCategs = attachMFandCategs.bind(this);
        this.isSearchPage = '';
        this.isProductPage = undefined;
        this.storeClassesOfProd = '';
        this.$topPaginationContainer = '';
        this.prodId = '';
        this.autof_settings = '';
        this.productsLoaded = 0;
        this.fewProdsInCategory = false;
        this.firstFlagLoadAutoFeatured = true;
        this.paginationTop = '';
        this.$focused_item = '';
        this.$items = '';
        this.$paginationBottom = '';
        this.is_mf_attached = '';
    }


    init() {
        console.log('showmore init');
        // Define wether search page loaded or product's
        this.isSearchPage = document.querySelector('h2.search-header');
        this.isProductPage = document.querySelector('h1.product-header');

        if (!this.isProductPage) {
            // < Some tinkering with mega filter >
            if (jQuery(window).width() > 992) {
                this.initMegafilterOnWideScreen();
            }

            //Fix megafilter's pagination
            this.fixMegafilterPagination();

            // </>
        }

        // Start showing autofeatured
        this.getReadyToShowMore();
    }


    getReadyToShowMore() {
        if ($('.pagination li.active').next('li').children('a').length > 0) {
            $('.pagination').before('<div id="showmore" class="showmoreBtn" style="padding-bottom: 15px;"><a id="showmore-text-btn" onclick="window.pageHandler.showmore()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
        }

        //$("img.lazy").lazyload();

        this.loadMoreIfNotEnough();

        this.$paginationBottom = $('#res-products .text-center .pagination');

        if (this.$paginationBottom.length != 0) {
            //this.$topPaginationContainer = $('.sort-row .left-sort-row');
            this.$topPaginationContainer = $('body');
            this.paginationTop = this.$paginationBottom.clone();
            this.$topPaginationContainer.append(this.paginationTop);
            this.paginationTop.css({
                "position": "fixed",
                "bottom": "10px",
                "opacity": "0.8",
                "right": "0",
                "z-index": "9",
                "background-color": "#fff",
                "box-shadow": "0 1px 9px rgba(0, 0, 0, .3)"
            });
        }
    }

    reloadShowMoreAfterFilter() {
        if (this.paginationTop !== undefined) this.paginationTop.remove();
        if ($('.autofeatured').length > 0) $('.autofeatured').remove();
        if ($('.showmoreBtn').length > 0) $('.showmoreBtn').remove();
        if ($('#showmore').length > 0) $('#showmore').remove();
        if ($('.autofeaturedText').length > 0) $('.autofeaturedText').remove();
        //$('.subcats-row').remove();
        this.fewProdsInCategory = false;
        this.firstFlagLoadAutoFeatured = true;
        this.productsLoaded = 0;
        if ($('#oct-slide-panel > ul').length > 0) $('#oct-slide-panel > ul').remove();
        if ($('.cat-desc-box').length > 0) $('.cat-desc-box').remove();

        this.fixMegafilterPagination();

        this.getReadyToShowMore();

    }


    // Only in category and search page. Shows products from next page
    showmore() {

        var $next = $('.pagination li.active').next('li').children('a');
        if ($next.length == 0) {
            return;
        }


        $.get($next.attr('href'), (data) => {
            this.stopLoadingAnimation();

            window.history.pushState(null, $next.innerText, $next.attr('href'));

            var $data = $(data);
            let products = $data.find('.product-layout');
            let productsArr = Array.from(products);

            if (this.isSearchPage) {
                console.log(this.storeClassesOfProd);
                productsArr.forEach(prod => {

                    prod.classList = this.storeClassesOfProd;
                })

            }
            var $container = $('#res-products .row:first-child');
            $container.append(productsArr);
            $('.pagination').html($data.find('.pagination > *'));
            if ($('.pagination li.active').next('li').children('a').length == 0) {
                $('#showmore').hide();
            }

            var paginationTop = this.paginationTop;

            if (paginationTop !== undefined) paginationTop.remove();
            paginationTop = this.$paginationBottom.clone();
            this.$topPaginationContainer.append(paginationTop);
            paginationTop.css({
                "position": "fixed",
                "bottom": "10px",
                "opacity": "0.8",
                "right": "0",
                "z-index": "9",
                "background-color": "#fff",
                "color": "#141414",
                "box-shadow": "0 1px 9px rgba(0, 0, 0, .3)"
            });
            $('.wishlist.oct-button').addClass('cbutton--effect-nikola'); $('.wishlist.oct-button').addClass('cbutton');
            bindEffectForCButton();

        }, "html");
        this.startLoadingAnimation();
        return false;
    }

    startLoadingAnimation() {
        var imgObj = $('#load-more-gif');
        var textBtn = $('#showmore-text-btn');
        imgObj.css("display", "block");
        textBtn.css("display", "none");

    }

    stopLoadingAnimation() {
        var imgObj = $('#load-more-gif');
        var textBtn = $('#showmore-text-btn');
        textBtn.css("display", "block");
        imgObj.css("display", "none");
    }


    autoLoadInScroll() {
        var flag = true;
        if (document.getElementById('showmore-text-btn') == null) {
            console.log('autoLoadInScroll error');
            return;
        }
        var button = document.getElementById('showmore-text-btn').getBoundingClientRect();
        window.addEventListener('scroll', () => {
            if (document.getElementById('showmore-text-btn') == null) {
                console.log('autoLoadInScroll error');
                return;
            }
            button = document.getElementById('showmore-text-btn').getBoundingClientRect();
            if (button.top > 2500) {
                flag = true;
            }
            if (button.top < 1500 && flag) {
                if (this.isProductPage || this.fewProdsInCategory) {
                    flag = false
                    return;
                }
                this.showmore();
                flag = false
            }

            if (jQuery(window).width() > 992) {
                if (!this.isProductPage) this.attachMFandCategs();
            }
        });
    }

    loadMoreIfNotEnough() {

        if (this.isProductPage) return;

        let productsList = document.querySelectorAll('#res-products .row .product-layout');
        let productArr = Array.from(productsList);
        //console.log(productArr.length);
        if (productArr.length == 0) return;
        if (productArr.length > 30) { this.autoLoadInScroll(); }

        this.storeClassesOfProd = productArr[0].classList;
    }


    lazyLoad() {
        $("img.lazy").lazyload();
    }

}

export default PageHandler;