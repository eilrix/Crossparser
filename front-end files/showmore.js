var $cookie = function () {};
var isSearchPage;
var $isProductPage;
var storeClassesOfProd;
var $topPaginationContainer;
var prodId;
var autof_settings = '';
var productsLoaded = 0;
var fewProdsInCategory = false;
var firstFlagLoadAutoFeatured = true;
var paginationTop;

/*
$(window).on('load', function () {
    $('body').after('<div id="KedPreloader"></div>');
    document.getElementById('KedPreloader').style.display = "block";
 document.getElementById('KedPreloader').style.display = "block";
})*/
function getReadyToShowMore() {
    if ($('.pagination li.active').next('li').children('a').length > 0) {
        $('.pagination').before('<div id="showmore" class="showmoreBtn" style="padding-bottom: 15px;"><a id="showmore-text-btn" onclick="showmore()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
    }
    if ($.totalStorage != undefined && $.totalStorage('display') != null) {
        $cookie = $.totalStorage;
    } else if ($.cookie != undefined && $.cookie('display') != null) {
        $cookie = $.cookie;
    }
    $("img.lazy").lazyload();

    loadMoreIfNotEnough();

    $paginationBottom = $('#res-products .text-center .pagination');
    if ($paginationBottom.length != 0) {
        //$topPaginationContainer = $('.sort-row .left-sort-row');
        $topPaginationContainer = $('body');
        paginationTop = $paginationBottom.clone();
        $topPaginationContainer.append(paginationTop);
        paginationTop.css({
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

function reloadShowMoreAfterFilter() {
    if (paginationTop !== undefined) paginationTop.remove();
    if ($('.autofeatured').length > 0) $('.autofeatured').remove();
    if ($('.showmoreBtn').length > 0) $('.showmoreBtn').remove();
    if ($('#showmore').length > 0) $('#showmore').remove();
    if ($('.autofeaturedText').length > 0) $('.autofeaturedText').remove();
    //$('.subcats-row').remove();
    fewProdsInCategory = false;
    firstFlagLoadAutoFeatured = true;
    productsLoaded = 0;
    if ($('#oct-slide-panel > ul').length > 0) $('#oct-slide-panel > ul').remove();
    if ($('.cat-desc-box').length > 0) $('.cat-desc-box').remove();

    fix_megafilter_paginationshit();

    getReadyToShowMore();

}

var $focused_item = '';
var $items;

$(document).ready(function () {
    isSearchPage = document.querySelector('h2.search-header');
    isProductPage = document.querySelector('h1.product-header');

    //Some tinkering with mega filter

    if (jQuery(window).width() > 992)
    {
        $('.pagination').before('<script src="//code.jquery.com/ui/1.12.1/jquery-ui.js"></script>');

        $items = $("#mfilter-box-1 .mfilter-filter-item");

        $("#mfilter-box-1").detach().appendTo("#content .row.sort-row");
        $("#column-left").css({'width': '15%'});
        $("#column-left + #content").css({'width': '85%'});

        // Set auto closing for PC:

        // Avoid fantom click on #grid-view
        var grid_view = $('#grid-view');

        $('body').click(function( event ) {

            $clicked_elem = $(event.target);
            //console.log('$clicked_elem', $clicked_elem)

            if (($items.has($clicked_elem).length == 0) && ($clicked_elem[0] != grid_view[0])) {
                //Click outside mf
                if ($focused_item != '') {
                    // Close focused
                    close_focused_item();
                    $focused_item = '';
                }
                return;
            }
            if ($items.has($clicked_elem).length > 0) {
                // Click on mf
                // Find focus item
                var $new_focused_item;
                $items.each( function (i) {
                    if ($($items[i]).has($clicked_elem).length != 0 ) {
                        $new_focused_item = $($items[i]);
                        //console.log('new foc item', $new_focused_item);
                    }
                });
                if ($focused_item == '') {
                    $focused_item = $new_focused_item;
                }
                if ($new_focused_item[0] != $focused_item[0]) {
                    //console.log('update foc item for', $focused_item, $new_focused_item);
                    close_focused_item();

                    $focused_item = $new_focused_item;
                }

            }

        });

        function close_focused_item() {
            $focused_item.find('> .mfilter-content-opts').slideUp('normal');
            var heading = $focused_item.find('> .mfilter-heading');
            heading.addClass('mfilter-collapsed');
        }


        // Attach mf and categories to top:
        is_mf_attached = false;

    }

    //Fix megafilter's pagination
    fix_megafilter_paginationshit();




    getReadyToShowMore();

});

function fix_megafilter_paginationshit () {

    $paginationBottom = $('#res-products .text-center .pagination li a');
    if ($paginationBottom.length != 0)
    {
        $paginationBottom.each( function (i) {
            var href =  jQuery($paginationBottom[i]).attr('href');

            var somea_arr = href.split('?');
            var curr_page = somea_arr[somea_arr.length - 1].split('=');
            var is_curr_page = curr_page[0];
            //console.log('is_curr_page', is_curr_page);

            if (is_curr_page == 'page') {
                curr_page = curr_page[curr_page.length - 1];
                href = window.location.href + '&page=' + curr_page;

                //console.log('href2', href);
                jQuery($paginationBottom[i]).attr('href', href);
            }
        })
    }
}


function attach_mf_cats() {

    var max_height = $('#res-products').height() + $('#res-products').offset().top - 700;

    if ($("#sstore-3-level").hasClass('column-left-attached')) {
        is_mf_attached = true;
    }
    else {
        is_mf_attached = false;
    }

    $('.sort-row-wrapper').height()
    //console.log(window.pageYOffset);
    if ((window.pageYOffset > 520) && (window.pageYOffset < max_height)) {
        // Attach
        if (!is_mf_attached) {
            is_mf_attached = true;
            console.log();
            console.log('attach!');
            console.log('window.pageYOffset', window.pageYOffset);
            console.log('max_height', max_height);

            $height_wrapper = $('.sort-row-wrapper').height();
            $('.sort-row-wrapper').css({
                'height' : $height_wrapper
            });

            //$("#content .row.sort-row").addClass('sortrow-attached');
            //$("#content .row.sort-row").switchClass( "", "sortrow-attached", 1000, "easeInOutQuad" );
            /*
            var $moveon = window.pageYOffset - $("#content .row.sort-row").offset().top;
            $("#content .row.sort-row").animate({
                top: `+=${$moveon}`
            }, 200, function() {
                $("#content .row.sort-row").addClass('sortrow-attached');
            });*/

            $("#content .row.sort-row").addClass('sortrow-attached');

            //$("#sstore-3-level").addClass('column-left-attached');
            //$("#sstore-3-level").switchClass( "", "column-left-attached", 1000, "easeInOutQuad" );
            /*
            $moveon = window.pageYOffset - $("#sstore-3-level").offset().top;
            $("#content .row.sort-row").animate({
                top: `+=${$moveon + 80}`
            }, 300, function() {
                $("#sstore-3-level").addClass('column-left-attached');
            });*/

            $("#sstore-3-level").addClass('column-left-attached');

        }
    }
    if (window.pageYOffset < 520 || window.pageYOffset >  max_height) {
        // Detach
        if (is_mf_attached) {
            console.log();
            console.log('detach!');
            console.log('window.pageYOffset', window.pageYOffset);
            console.log('max_height', max_height);

            $("#content .row.sort-row").css({'top': '0'})
            $("#content .row.sort-row").removeClass('sortrow-attached');

            $("#sstore-3-level").removeClass('column-left-attached');

            is_mf_attached = false;
        }
    }
/*
    setTimeout( ()=>{
        attach_mf_cats();
        }, 1000);*/
}

function showmore() {

    var $next = $('.pagination li.active').next('li').children('a');
    if ($next.length == 0) {
        return;
    }

    window.history.pushState(null,$next.innerText,$next.attr('href'));

    $.get($next.attr('href'), function (data) {
        stopLoadingAnimation();

        $data = $(data);
        let products = $data.find('.product-layout');
        let productsArr = Array.from(products);

        if (isSearchPage){
            console.log(storeClassesOfProd);
            productsArr.forEach(prod => {

                prod.classList = storeClassesOfProd;
            })

        }
        var $container = $('#res-products .row:first-child');
        //$container.append($data.find('#res-products .row:first-child'));
        $container.append(productsArr);
        $("img.lazy").lazyload();
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

        if (paginationTop !== undefined) paginationTop.remove();
        paginationTop = $paginationBottom.clone();
        $topPaginationContainer.append(paginationTop);
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
function startLoadingAnimation()
{
    var imgObj = $('#load-more-gif');
    var textBtn = $('#showmore-text-btn');
    imgObj.css("display", "block");
    textBtn.css("display", "none");

}

function stopLoadingAnimation()
{
    var imgObj = $('#load-more-gif');
    var textBtn = $('#showmore-text-btn');
    textBtn.css("display", "block");
    imgObj.css("display", "none");
}

function autoLoadInScroll(){
    var flag = true;
    if (document.getElementById('showmore-text-btn') == null) {
        console.log('autoLoadInScroll error');
        return;
    }
    var button = document.getElementById('showmore-text-btn').getBoundingClientRect();
    window.onscroll = function() {

        if (document.getElementById('showmore-text-btn') == null) {
            console.log('autoLoadInScroll error');
            return;
        }
        button = document.getElementById('showmore-text-btn').getBoundingClientRect();
        if (button.top > 2500){
            flag = true;
        }
        if (button.top < 1500 && flag) {
            if (isProductPage || fewProdsInCategory){
                loadAutoFeatured();
                flag = false
                return;
            }
            showmore();
            flag = false
        }

        if (jQuery(window).width() > 992) {
            attach_mf_cats();
        }
    };
}

function loadMoreIfNotEnough() {

    if (document.getElementById('autofeatured_settings') && autof_settings == '') {
        autof_settings = document.getElementById('autofeatured_settings').innerText;
    }

    if (isProductPage){
        prodId = document.getElementById('LoadMoreHere').innerText;
        document.getElementById('LoadMoreHere').innerText = "";

        $("#LoadMoreHere").append('<h3 class="autofeaturedText" class="autofeatured-selected"><a id="autofeatured_btn">Рекомендуемые товары</a><a id="imagematch_btn">Визуально похожие товары</a></h3>');
        $("#LoadMoreHere").after('<div id="showmore" class="showmoreBtn col-sm-12" style="padding-top: 15px;"><a id="showmore-text-btn" onclick="loadAutoFeatured()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');

        // imagematch switch
        $('#autofeatured_btn').addClass('autofeatured-selected');

        $('#imagematch_btn').click( ()=> {
            $('.row.autofeatured').remove();
            $('#imagematch_btn').addClass('autofeatured-selected');
            $('#autofeatured_btn').removeClass('autofeatured-selected');
            loadImgMatch();
        })
        $('#autofeatured_btn').click( ()=> {
            $('.row.autofeatured').remove();
            $('#imagematch_btn').removeClass('autofeatured-selected');
            $('#autofeatured_btn').addClass('autofeatured-selected');
            productsLoaded = 0;
            autoLoadInScroll();
            loadAutoFeatured();
        })

        autoLoadInScroll();
        loadAutoFeatured();
        return;
    }
    //Category page:
    if (jQuery(window).width() > 992) {
        window.onscroll = function() {
            attach_mf_cats();
        }
    }

    let productsList = document.querySelectorAll('#res-products .row .product-layout');
    let productArr = Array.from(productsList);
    //console.log(productArr.length);
    if (!productsList) return;
    if (productArr.length > 30) {autoLoadInScroll();}

    storeClassesOfProd = productArr[0].classList;

    if (productArr.length < 20) {
        fewProdsInCategory = true;

        let linkProdOncl = productArr[0].querySelector('.quick-view a').getAttribute('onclick');
        prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
        //console.log(prodId);

        loadAutoFeatured();

        $('.container .content-row').append('<h3 class="autofeaturedText">Похожие товары</h3>');
    }


}


function loadAutoFeatured() {

    if (isProductPage == null) {
        let productsList = document.querySelectorAll('#res-products .row .product-layout');
        let productArr = Array.from(productsList);
        let linkProdOncl = productArr[0].querySelector('.quick-view a').getAttribute('onclick');
        prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
    }

    console.log('prodId: ', prodId, 'productsLoaded: ', productsLoaded);
    console.log('autof_settings', autof_settings);


    let dataSend = {
        'autof_settings' : autof_settings,
        'prodId' : prodId,
        'productsLoaded' : productsLoaded
    };
    startLoadingAnimation();

    $.ajax({
        type: "POST",
        url: 'index.php?route=extension/module/autofeatured/ajaxGetProduct',
        data: dataSend
    }).done(function( data ){
        console.log('post: ', data);
        stopLoadingAnimation();

        if(isProductPage){
            $("#LoadMoreHere").append(data);
            return;
        }
        $('.container .content-row').append(data);
        if(firstFlagLoadAutoFeatured){
            firstFlagLoadAutoFeatured = false;
            $('footer').before('<div id="showmore" class="showmoreBtn" style="padding-top: 15px;"><a id="showmore-text-btn" onclick="loadAutoFeatured()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
            autoLoadInScroll();
        }
    });

    productsLoaded += 40;

}

function loadImgMatch() {

    if (isProductPage == null) {
        let productsList = document.querySelectorAll('#res-products .row .product-layout');
        let productArr = Array.from(productsList);
        let linkProdOncl = productArr[0].querySelector('.quick-view a').getAttribute('onclick');
        prodId = linkProdOncl.split('(')[1].replace("'", "").replace("')", "").replace(";", "");
    }
    var prod_sku = $('#product > div:nth-child(7) > span.product-sizes-span').text();
    console.log('prodId: ', prodId, 'productsLoaded: ', productsLoaded);
    console.log('autof_settings', autof_settings);


    let dataSend = {
        'autof_settings' : autof_settings,
        'prodId' : prod_sku,
        'productsLoaded' : productsLoaded
    };
    startLoadingAnimation();

    $.ajax({
        type: "POST",
        url: 'index.php?route=extension/module/autofeatured/ajaxGetImgMatched',
        data: dataSend
    }).done(function( data ){
        console.log('post: ', data);
        stopLoadingAnimation();

        if(isProductPage){
            $("#LoadMoreHere").append(data);
            return;
        }
        $('.container .content-row').append(data);
        if(firstFlagLoadAutoFeatured){
            firstFlagLoadAutoFeatured = false;
            $('footer').before('<div id="showmore" class="showmoreBtn" style="padding-top: 15px;"><a id="showmore-text-btn" onclick="loadAutoFeatured()">Показать еще</a><img id="load-more-gif"  style="display: none; margin: 0px auto;" src="image/loading.gif"></div>');
            autoLoadInScroll();
        }
    });

    productsLoaded += 40;

}

function customCallAutofeatured(prodId = 0, productsLoaded = 0, spawnBlock = '.container .content-row') {
    window.onscroll = {};
    let dataSend = {
        //'settings' : settings,
        'prodId' : prodId,
        'productsLoaded' : productsLoaded
    };
    startLoadingAnimation();

    $.ajax({
        type: "POST",
        url: 'index.php?route=extension/module/autofeatured/ajaxGetProduct',
        data: dataSend
    }).done(function( data ){
        console.log('post: ', data);
        stopLoadingAnimation();

        if(isProductPage){
            $("#LoadMoreHere").append(data);
            return;
        }

        $(spawnBlock).append(data);
    }).fail(function() {
        console.log( "error" );
        stopLoadingAnimation();
    })

}

function customCallImgMatch(prodId = 0, productsLoaded = 0, spawnBlock = '.container .content-row') {
    window.onscroll = {};

    let dataSend = {
        //'settings' : settings,
        'prodId' : prodId,
        'productsLoaded' : productsLoaded
    };
    startLoadingAnimation();

    $.ajax({
        type: "POST",
        url: 'index.php?route=extension/module/autofeatured/ajaxGetImgMatched',
        data: dataSend
    }).done(function( data ){
        console.log('post: ', data);
        stopLoadingAnimation();

        if(isProductPage){
            $("#LoadMoreHere").append(data);
            return;
        }

        $(spawnBlock).append(data);
    }).fail(function() {
        console.log( "error" );
        stopLoadingAnimation();
    })

}