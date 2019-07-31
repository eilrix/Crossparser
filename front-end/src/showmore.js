import {
    fixMegafilterPagination, 
    initMegafilterOnWideScreen,
    attachMFandCategs
} from './megafilterPatch';

//import $ from 'jquery';


$(document).ready(function () {

    let pageHandler = new PageHandler();

    window.pageHandler = pageHandler;
    
    pageHandler.init();
});

class PageHandler {

    constructor() {
        this.fixMegafilterPagination = fixMegafilterPagination.bind(this);
        this.initMegafilterOnWideScreen = initMegafilterOnWideScreen.bind(this);
        this.attachMFandCategs = attachMFandCategs.bind(this);
        this.isSearchPage = '';
        this.isProductPage = '';
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
            if (jQuery(window).width() > 992)
            {
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
            $('.pagination').before('<div id="showmore" class="showmoreBtn" style="padding-bottom: 15px;"><a id="showmore-text-btn" onclick="showmore()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
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
                "position":"fixed",
                "bottom":"10px",
                "opacity":"0.8",
                "right":"0",
                "z-index":"9",
                "background-color":"#fff",
                "box-shadow":"0 1px 9px rgba(0, 0, 0, .3)"
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
    

    
    showmore() {
    
        var $next = $('.pagination li.active').next('li').children('a');
        if ($next.length == 0) {
            return;
        }
    
        window.history.pushState(null,$next.innerText,$next.attr('href'));
    
        $.get($next.attr('href'), (data) => {
            this.stopLoadingAnimation();
    
            $data = $(data);
            let products = $data.find('.product-layout');
            let productsArr = Array.from(products);
    
            if (this.isSearchPage){
                console.log(this.storeClassesOfProd);
                productsArr.forEach(prod => {
    
                    prod.classList = this.storeClassesOfProd;
                })
    
            }
            var $container = $('#res-products .row:first-child');
            //$container.append($data.find('#res-products .row:first-child'));
            $container.append(productsArr);
            //$("img.lazy").lazyload();
            $('.pagination').html($data.find('.pagination > *'));
            if ($('.pagination li.active').next('li').children('a').length == 0) {
                $('#showmore').hide();
            }
    
            $data.filter('script').each(function () {
                if ((this.text || this.textContent || this.innerHTML).indexOf("document.write") >= 0) {
                    return;
                }
                $.globalEval(this.text || this.textContent || this.innerHTML || '');
            });
            //$('html, body').animate({ scrollTop: $container.offset().top - 10 }, 'slow');
    
            var paginationTop = this.paginationTop;

            if (paginationTop !== undefined) paginationTop.remove();
            paginationTop = this.$paginationBottom.clone();
            this.$topPaginationContainer.append(paginationTop);
            paginationTop.css({
                "position":"fixed",
                "bottom":"10px",
                "opacity":"0.8",
                "right":"0",
                "z-index":"9",
                "background-color":"#fff",
                "color":"#141414",
                "box-shadow":"0 1px 9px rgba(0, 0, 0, .3)"
            });
            $('.wishlist.oct-button').addClass('cbutton--effect-nikola'); $('.wishlist.oct-button').addClass('cbutton');
            bindEffectForCButton();
    
        }, "html");
        startLoadingAnimation();
        return false;
    }

    startLoadingAnimation()
    {
        var imgObj = $('#load-more-gif');
        var textBtn = $('#showmore-text-btn');
        imgObj.css("display", "block");
        textBtn.css("display", "none");
    
    }
    
    stopLoadingAnimation()
    {
        var imgObj = $('#load-more-gif');
        var textBtn = $('#showmore-text-btn');
        textBtn.css("display", "block");
        imgObj.css("display", "none");
    }
    
    autoLoadInScroll(){
        var flag = true;
        if (document.getElementById('showmore-text-btn') == null) {
            console.log('autoLoadInScroll error');
            return;
        }
        var button = document.getElementById('showmore-text-btn').getBoundingClientRect();
        window.onscroll = () => {
    
            if (document.getElementById('showmore-text-btn') == null) {
                console.log('autoLoadInScroll error');
                return;
            }
            button = document.getElementById('showmore-text-btn').getBoundingClientRect();
            if (button.top > 2500){
                flag = true;
            }
            if (button.top < 1500 && flag) {
                if (this.isProductPage || this.fewProdsInCategory){
                    this.loadAutoFeatured();
                    flag = false
                    return;
                }
                this.showmore();
                flag = false
            }
    
            if (jQuery(window).width() > 992) {
                if (!this.isProductPage) this.attachMFandCategs();
            }
        };
    }
    
    loadMoreIfNotEnough() {
    
        if (document.getElementById('autofeatured_settings') && this.autof_settings == '') {
            this.autof_settings = document.getElementById('autofeatured_settings').innerText;
        }
    
        if (this.isProductPage){
            this.prodId = document.getElementById('LoadMoreHere').innerText;
            document.getElementById('LoadMoreHere').innerText = "";
    
            $("#LoadMoreHere").append('<h3 class="autofeaturedText" class="autofeatured-selected"><a id="autofeatured_btn">Рекомендуемые товары</a><a id="imagematch_btn">Визуально похожие товары</a></h3>');
            $("#LoadMoreHere").after('<div id="showmore" class="showmoreBtn col-sm-12" style="padding-top: 15px;"><a id="showmore-text-btn" onclick="pageHandler.loadAutoFeatured()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
    
            // imagematch switch
            $('#autofeatured_btn').addClass('autofeatured-selected');
    
            $('#imagematch_btn').click( ()=> {
                $('.row.autofeatured').remove();
                $('#imagematch_btn').addClass('autofeatured-selected');
                $('#autofeatured_btn').removeClass('autofeatured-selected');
                this.loadImgMatch();
            })
            $('#autofeatured_btn').click( ()=> {
                $('.row.autofeatured').remove();
                $('#imagematch_btn').removeClass('autofeatured-selected');
                $('#autofeatured_btn').addClass('autofeatured-selected');
                this.productsLoaded = 0;
                this.autoLoadInScroll();
                this.loadAutoFeatured();
            })
    
            this.autoLoadInScroll();
            this.loadAutoFeatured();
            return;
        }
        //Category page:
        if (jQuery(window).width() > 992) {
            window.onscroll = () => {
                if (!this.isProductPage) this.attachMFandCategs();
            }
        }
    
        let productsList = document.querySelectorAll('#res-products .row .product-layout');
        let productArr = Array.from(productsList);
        //console.log(productArr.length);
        if (!productsList) return;
        if (productArr.length > 30) {this.autoLoadInScroll();}
    
        this.storeClassesOfProd = productArr[0].classList;
    
        if (productArr.length < 20) {
            this.fewProdsInCategory = true;
    
            let linkProdOncl = productArr[0].querySelector('.quick-view a').getAttribute('onclick');
            this.prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
            //console.log(this.prodId);
    
            this.loadAutoFeatured();
    
            $('.container .content-row').append('<h3 class="autofeaturedText">Похожие товары</h3>');
        }
    
    
    }
    
    
    loadAutoFeatured() {
    
        if (this.isProductPage == null) {
            let productsList = document.querySelectorAll('#res-products .row .product-layout');
            let productArr = Array.from(productsList);
            let linkProdOncl = productArr[0].querySelector('.quick-view a').getAttribute('onclick');
            this.prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
        }
    
        console.log('prodId: ', this.prodId, 'productsLoaded: ', this.productsLoaded);
        console.log('autof_settings', this.autof_settings);
    
    
        let dataSend = {
            'autof_settings' : this.autof_settings,
            'prodId' : this.prodId,
            'productsLoaded' : this.productsLoaded
        };
        this.startLoadingAnimation();
    
        $.ajax({
            type: "POST",
            url: 'index.php?route=extension/module/autofeatured/ajaxGetProduct',
            data: dataSend
        }).done(( data ) => {
            console.log('post: ', data);
            this.stopLoadingAnimation();
    
            if(this.isProductPage){
                $("#LoadMoreHere").append(data);
                return;
            }
            $('.container .content-row').append(data);
            if(this.firstFlagLoadAutoFeatured){
                this.firstFlagLoadAutoFeatured = false;
                $('footer').before('<div id="showmore" class="showmoreBtn" style="padding-top: 15px;"><a id="showmore-text-btn" onclick="loadAutoFeatured()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
                this.autoLoadInScroll();
            }
        });
    
        this.productsLoaded += 40;
    
    }
    
    loadImgMatch() {
    
        if (this.isProductPage == null) {
            let productsList = document.querySelectorAll('#res-products .row .product-layout');
            let productArr = Array.from(productsList);
            let linkProdOncl = productArr[0].querySelector('.quick-view a').getAttribute('onclick');
            this.prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
        }
        var prod_sku = $('#product > div:nth-child(7) > span.product-sizes-span').text();
        console.log('prodId: ', this.prodId, 'productsLoaded: ', this.productsLoaded);
        console.log('autof_settings', this.autof_settings);
    
    
        let dataSend = {
            'autof_settings' : this.autof_settings,
            'prodId' : prod_sku,
            'productsLoaded' : this.productsLoaded
        };
        this.startLoadingAnimation();
    
        $.ajax({
            type: "POST",
            url: 'index.php?route=extension/module/autofeatured/ajaxGetImgMatched',
            data: dataSend
        }).done(function( data ){
            console.log('post: ', data);
            this.stopLoadingAnimation();
    
            if(this.isProductPage){
                $("#LoadMoreHere").append(data);
                return;
            }
            $('.container .content-row').append(data);
            if(this.firstFlagLoadAutoFeatured){
                this.firstFlagLoadAutoFeatured = false;
                $('footer').before('<div id="showmore" class="showmoreBtn" style="padding-top: 15px;"><a id="showmore-text-btn" onclick="loadAutoFeatured()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
                this.autoLoadInScroll();
            }
        });
    
        this.productsLoaded += 40;
    
    }
    
    customCallAutofeatured(prodId = 0, productsLoaded = 0, spawnBlock = '.container .content-row') {
        window.onscroll = {};
        let dataSend = {
            //'settings' : settings,
            'prodId' : prodId,
            'productsLoaded' : productsLoaded
        };
        this.startLoadingAnimation();
    
        $.ajax({
            type: "POST",
            url: 'index.php?route=extension/module/autofeatured/ajaxGetProduct',
            data: dataSend
        }).done(function( data ){
            console.log('post: ', data);
            this.stopLoadingAnimation();
    
            if(this.isProductPage){
                $("#LoadMoreHere").append(data);
                return;
            }
    
            $(spawnBlock).append(data);
        }).fail(function() {
            console.log( "error" );
            this.stopLoadingAnimation();
        })
    
    }
    
    customCallImgMatch(prodId = 0, productsLoaded = 0, spawnBlock = '.container .content-row') {
        window.onscroll = {};
    
        let dataSend = {
            //'settings' : settings,
            'prodId' : prodId,
            'productsLoaded' : productsLoaded
        };
        this.startLoadingAnimation();
    
        $.ajax({
            type: "POST",
            url: 'index.php?route=extension/module/autofeatured/ajaxGetImgMatched',
            data: dataSend
        }).done(function( data ){
            console.log('post: ', data);
            this.stopLoadingAnimation();
    
            if(this.isProductPage){
                $("#LoadMoreHere").append(data);
                return;
            }
    
            $(spawnBlock).append(data);
        }).fail(function() {
            console.log( "error" );
            this.stopLoadingAnimation();
        })
    
    }
    
}

export default PageHandler;