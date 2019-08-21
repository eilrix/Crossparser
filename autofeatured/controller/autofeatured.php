<?php
class ControllerExtensionModuleAutoFeatured extends Controller {


	public function index($setting , $productId = 0, $productsLoaded = 40) {

	    $out = '<div id="autofeatured_settings" style="display: none;">' . json_encode($setting) . '</div>';

        return $out;

		$this->load->language('extension/module/autofeatured');


		$data['text_tax'] = $this->language->get('text_tax');

		$data['button_cart'] = $this->language->get('button_cart');
		$data['button_wishlist'] = $this->language->get('button_wishlist');
		$data['button_compare'] = $this->language->get('button_compare');

		$this->load->model('catalog/product');

		$this->load->model('tool/image');

		$data['products'] = array();
		$data['settings'] = $setting['limit'];

		if (!$setting['limit']) {
			$setting['limit'] = 4;
		}
		$this->load->model('extension/module/autofeatured');

		$product_id = isset($this->request->get['product_id']) ? $this->request->get['product_id'] : 0;
		if ($product_id < 1){
            $product_id = $productId;
            $setting['limit'] = $productsLoaded + 40;
        }
        if ($product_id < 1){
            return 0;
        }
        //error_log( $product_id );
        //error_log( $productsLoaded );
       // error_log( $setting['limit'] );


        $results = $this->model_extension_module_autofeatured->getProductAutoFeatured($product_id,$setting['limit'],$setting['attribute'],$setting['category_source'],$setting['category'],$setting['sortby'],$setting['in_stock'],$setting['one_cat']);

        $results['products'] = array_slice($results['products'], $productsLoaded, $productsLoaded + 40);

		//$data['heading_title'] = $setting['titleview'] ? $setting['name'] . $results['text'] : $setting['name'];

        //error_log(json_encode($results));
      // error_log(json_encode($setting));


		foreach ($results['products'] as $product_id) {
			$product_info = $this->model_catalog_product->getProduct($product_id);

			if ($product_info) {
				if ($product_info['image']) {
					$image = $this->model_tool_image->resize($product_info['image'], $setting['width'], $setting['height']);
				} else {
					$image = $this->model_tool_image->resize('placeholder.png', $setting['width'], $setting['height']);
				}

                if ($this->customer->isLogged() || !$this->config->get('config_customer_price')) {
                    $price = $this->currency->format($this->tax->calculate($product_info['price'], $product_info['tax_class_id'], $this->config->get('config_tax')), $this->session->data['currency']);
				} else {
					$price = false;
				}

				if ((float)$product_info['special']) {
					$special = $this->currency->format($this->tax->calculate($product_info['special'], $product_info['tax_class_id'], $this->config->get('config_tax')), $this->session->data['currency']);
				} else {
					$special = false;
				}


                $tax = false;


				if ($this->config->get('config_review_status')) {
					$rating = $product_info['rating'];
				} else {
					$rating = false;
				}

				$data['products'][] = array(
					'product_id'  => $product_info['product_id'],
					'thumb'       => $image,
					'name'        => $product_info['name'],
					'description' => utf8_substr(strip_tags(html_entity_decode($product_info['description'], ENT_QUOTES, 'UTF-8')), 0, $this->config->get('config_product_description_length')) . '..',
					'price'       => $price,
					'special'     => $special,
					'tax'         => $tax,
					'rating'      => $rating,
					'href'        => $this->url->link('product/product', 'product_id=' . $product_info['product_id']),
                    'settings'    => json_encode($setting)
				);
			}
		}

		if ($data['products']) {
			if (file_exists(DIR_TEMPLATE . $this->config->get('config_template') . '/template/extension/module/autofeatured.tpl')) {
				return $this->load->view($this->config->get('config_template') . '/template/extension/module/autofeatured.tpl', $data);
			} elseif (file_exists(DIR_TEMPLATE . $this->config->get('config_template') . '/template/extension/module/featured.tpl')) {
				return $this->load->view($this->config->get('config_template') . '/template/extension/module/featured.tpl', $data);
			} else {
				return $this->load->view('/extension/module/autofeatured.tpl', $data);
			}
		}
	}


    public function get_prods_forId($setting , $productId = 0, $productsLoaded = 40) {



        if (!$setting['limit']) {
            $setting['limit'] = 4;
        }
        $this->load->model('extension/module/autofeatured');


        $product_id = $productId;
        $setting['limit'] = $productsLoaded + 40;

        if ($product_id < 1){
            return 0;
        }
        //error_log( $product_id );
        //error_log( $productsLoaded );
        // error_log( $setting['limit'] );


        $results = $this->model_extension_module_autofeatured->getProductAutoFeatured($product_id,$setting['limit'],$setting['attribute'],$setting['category_source'],$setting['category'],$setting['sortby'],$setting['in_stock'],$setting['one_cat']);

        $results['products'] = array_slice($results['products'], $productsLoaded, $productsLoaded + 40);

        //$data['heading_title'] = $setting['titleview'] ? $setting['name'] . $results['text'] : $setting['name'];

        //error_log(json_encode($results));
        // error_log(json_encode($setting));
        return $this->getFeaturedTemplate($results['products'], $setting);


    }

    public function getFeaturedTemplate($results, $setting)
    {
        $data['products'] = array();
        $data['settings'] = $setting['limit'];

        $this->load->language('extension/module/autofeatured');


        $data['text_tax'] = $this->language->get('text_tax');

        $data['button_cart'] = $this->language->get('button_cart');
        $data['button_wishlist'] = $this->language->get('button_wishlist');
        $data['button_compare'] = $this->language->get('button_compare');

        $this->load->model('catalog/product');

        $this->load->model('tool/image');


        foreach ($results as $product_id) {
            $product_info = $this->model_catalog_product->getProduct($product_id);

            if ($product_info) {
                if ($product_info['image']) {
                    $image = $this->model_tool_image->resize($product_info['image'], $setting['width'], $setting['height']);
                    //$image = $this->resize($product_info['image'], $setting['width'], $setting['height']);
                    //$image = json_encode($setting);
                } else {
                    $image = $this->model_tool_image->resize('placeholder.png', $setting['width'], $setting['height']);
                }

                if ($this->customer->isLogged() || !$this->config->get('config_customer_price')) {
                    $price = $this->currency->format($this->tax->calculate($product_info['price'], $product_info['tax_class_id'], $this->config->get('config_tax')), $this->session->data['currency']);
                } else {
                    $price = false;
                }

                if ((float)$product_info['special']) {
                    $special = $this->currency->format($this->tax->calculate($product_info['special'], $product_info['tax_class_id'], $this->config->get('config_tax')), $this->session->data['currency']);
                } else {
                    $special = false;
                }


                $tax = false;


                if ($this->config->get('config_review_status')) {
                    $rating = $product_info['rating'];
                } else {
                    $rating = false;
                }

                $data['products'][] = array(
                    'product_id'  => $product_info['product_id'],
                    'thumb'       => $image,
                    'name'        => $product_info['name'],
                    'description' => utf8_substr(strip_tags(html_entity_decode($product_info['description'], ENT_QUOTES, 'UTF-8')), 0, $this->config->get('config_product_description_length')) . '..',
                    'price'       => $price,
                    'special'     => $special,
                    'tax'         => $tax,
                    'rating'      => $rating,
                    'href'        => $this->url->link('product/product', 'product_id=' . $product_info['product_id']),
                    'settings'    => json_encode($setting)
                );
            }
        }

        if ($data['products']) {
            if (file_exists(DIR_TEMPLATE . $this->config->get('config_template') . '/template/extension/module/autofeatured.tpl')) {
                return $this->load->view($this->config->get('config_template') . '/template/extension/module/autofeatured.tpl', $data);
            } elseif (file_exists(DIR_TEMPLATE . $this->config->get('config_template') . '/template/extension/module/featured.tpl')) {
                return $this->load->view($this->config->get('config_template') . '/template/extension/module/featured.tpl', $data);
            } else {
                return $this->load->view('/extension/module/autofeatured.tpl', $data);
            }
        }

    }



    public function ajaxGetProduct() {

        $settings  = json_decode($_POST['autof_settings'], true);
        $productId = json_decode($_POST['prodId']);
        $productsLoaded = json_decode($_POST['productsLoaded']);

        $settingsJson = '{"name":"\u041f\u043e\u0445\u043e\u0436\u0438\u0435 \u0442\u043e\u0432\u0430\u0440\u044b","titleview":"0","attribute":["19","17"],"category_source":"","category":"","one_cat":"1","in_stock":"1","limit":"30","width":"300","height":"300","sortby":"attribute","status":"1","position":"content_bottom"}';
        //$settings = json_decode($settingsJson, true);


        //$settings['limit'] = 40;
        //$settings['attribute'] = array();
        //$settings['sortby'] = "attribute";
        //$settings['one_cat'] = "0";

        //$this->response->setOutput(json_encode($settings['name']));

        $this->response->setOutput($this->get_prods_forId($settings, $productId, $productsLoaded));


    }


    public function ajaxGetImgMatched() {

        $productId = $_POST['prodId'];
        $settings  = json_decode($_POST['autof_settings'], true);

        $scrip_path = '/var/www/html/boots-market/ImageMatch/test_match.py';
        $command = escapeshellcmd("python3 $scrip_path $productId");
        $py_output = shell_exec($command);

        $products = json_decode($py_output, true);

        $products_id = array();

        foreach ($products as $product)
        {
            $products_id[] = $product["prod_id"];
        }

        $this->load->model('extension/module/autofeatured');

        $results = $this->model_extension_module_autofeatured->getProductImgMatch($products_id);

        $index = 0;
        foreach ($products_id as $prod) {
            $products_id[$index] = $results[$prod];

            $index += 1;
        }
        //echo json_encode($products_id);
        //$this->response->setOutput($this->getFeaturedTemplate($results, $settings));
        echo $this->getFeaturedTemplate($products_id, $settings);

        //$results['products'] = array_slice($results['products'], $productsLoaded, $productsLoaded + 40);
        //return $this->getFeaturedTemplate($results['products'], $setting);
    }



}

