
export function initMegafilterOnWideScreen() {

    $('.pagination').before('<script src="//code.jquery.com/ui/1.12.1/jquery-ui.js"></script>');
    
    this.$items = $("#mfilter-box-1 .mfilter-filter-item");

    $("#mfilter-box-1").detach().appendTo("#content .row.sort-row");
    $("#column-left").css({'width': '15%'});
    $("#column-left + #content").css({'width': '85%'});

    // Set auto closing for PC:

    // Avoid fantom click on #grid-view
    var grid_view = $('#grid-view');

    
    let close_focused_item = ()=> {
        this.$focused_item.find('> .mfilter-content-opts').slideUp('normal');
        var heading = this.$focused_item.find('> .mfilter-heading');
        heading.addClass('mfilter-collapsed');
    }

    $('body').click( ( event )  => {

        var $clicked_elem = $(event.target);
        //console.log('$clicked_elem', $clicked_elem)


        if ((this.$items.has($clicked_elem).length == 0) && ($clicked_elem[0] != grid_view[0])) {
            //Click outside mf
            if (this.$focused_item != '') {
                // Close focused
                close_focused_item();
                this.$focused_item = '';
            }
            return;
        }
        if (this.$items.has($clicked_elem).length > 0) {
            // Click on mf
            // Find focus item
            var $new_focused_item;
            this.$items.each(  (i) => {
                if ($(this.$items[i]).has($clicked_elem).length != 0 ) {
                    $new_focused_item = $(this.$items[i]);
                    //console.log('new foc item', $new_focused_item);
                }
            });
            if (this.$focused_item == '') {
                this.$focused_item = $new_focused_item;
            }
            if ($new_focused_item[0] != this.$focused_item[0]) {
                //console.log('update foc item for', $focused_item, $new_focused_item);
                close_focused_item();

                this.$focused_item = $new_focused_item;
            }

        }

    });


    // Attach mf and categories to top:
    this.is_mf_attached = false;
};

export function fixMegafilterPagination() {

    var $paginationBottom = $('#res-products .text-center .pagination li a');
    this.$paginationBottom = $paginationBottom;

    if ($paginationBottom.length != 0)
    {
        $paginationBottom.each(  (i) => {
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


export function attachMFandCategs() {

    var max_height = $('#res-products').height() + $('#res-products').offset().top - 700;
    
    if ($("#sstore-3-level").hasClass('column-left-attached')) {
        this.is_mf_attached = true;
    }
    else {
        this.is_mf_attached = false;
    }

    $('.sort-row-wrapper').height()
    //console.log(window.pageYOffset);
    if ((window.pageYOffset > 520) && (window.pageYOffset < max_height)) {
        // Attach
        if (!this.is_mf_attached) {
            this.is_mf_attached = true;
            console.log();
            console.log('attach!');
            console.log('window.pageYOffset', window.pageYOffset);
            console.log('max_height', max_height);

            var $height_wrapper = $('.sort-row-wrapper').height();
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
        if (this.is_mf_attached) {
            //console.log();
            //console.log('detach!');
            //console.log('window.pageYOffset', window.pageYOffset);
            //console.log('max_height', max_height);

            $("#content .row.sort-row").css({'top': '0'})
            $("#content .row.sort-row").removeClass('sortrow-attached');

            $("#sstore-3-level").removeClass('column-left-attached');

            this.is_mf_attached = false;
        }
    }
/*
    setTimeout( ()=>{
        attach_mf_cats();
        }, 1000);*/
}
