
<div class="row autofeatured">
  <?php foreach ($products as $product) { ?>
  <div class="product-layout col-lg-3 col-md-3 col-sm-6 col-xs-12">
    <div class="product-thumb transition">
      <div class="image">
        <a href="<?php echo $product['href']; ?>">
          <div class="quick-view"><a onclick="get_oct_popup_product_view('<?php echo $product['product_id']; ?>');" class="current-link">Быстрый просмотр</a></div>
          <img src="/image/catalog/1lazy/oct_loader_product.gif" data-original="<?php echo $product['thumb']; ?>" alt="<?php echo $product['name']; ?>" title="<?php echo $product['name']; ?>" class="img-responsive lazy" />
        </a>
      </div>
      <div class="caption">
        <h4><a href="<?php echo $product['href']; ?>"><?php echo $product['name']; ?></a></h4>
        <p><?php echo $product['description']; ?></p>
        <?php if ($product['rating']) { ?>
        <div class="rating">
          <?php for ($i = 1; $i <= 5; $i++) { ?>
          <?php if ($product['rating'] < $i) { ?>
          <span class="fa fa-stack"><i class="fa fa-star-o fa-stack-2x"></i></span>
          <?php } else { ?>
          <span class="fa fa-stack"><i class="fa fa-star fa-stack-2x"></i><i class="fa fa-star-o fa-stack-2x"></i></span>
          <?php } ?>
          <?php } ?>
        </div>
        <?php } ?>
        <?php if ($product['price']) { ?>
        <p class="price">
          <?php if (!$product['special']) { ?>
          <?php echo $product['price']; ?>
          <?php } else { ?>
          <span class="price-new"><?php echo $product['special']; ?></span> <span class="price-old"><?php echo $product['price']; ?></span>
          <?php } ?>
          <?php if ($product['tax']) { ?>
          <span class="price-tax"><?php echo $text_tax; ?> <?php echo $product['tax']; ?></span>
          <?php } ?>
        </p>
        <?php } ?>
        <button id="autofeaturedWishlist" class="cbutton cbutton--effect-nikola" type="button" data-toggle="tooltip" title="<?php echo $button_wishlist; ?>" onclick="get_oct_popup_add_to_wishlist('<?php echo $product['product_id']; ?>');"><i class="fa fa-heart"></i></button>
      </div>
    </div>
  </div>
  <?php } ?>
  <script type="text/javascript">

      setTimeout( ()=> {
          $("img.lazy").lazyload();﻿﻿
      }, 2000);

  </script>



</div>
