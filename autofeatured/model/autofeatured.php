<?php

class ModelExtensionModuleAutoFeatured extends Model {
	
	public function getProductAutoFeatured($product_id,$limit,$attributesset,$categoriesset_source,$categoriesset,$sortby,$in_stock,$one_cat) {

		$this->load->model('catalog/product');
		$product_data['products'] = array();
		$temp_text = array();
		$product_data['text'] = '';
		$product_data['text'] = ' (';
		$attributes = $attributesset;
		
		$sql = "SELECT IF(t1.cprice>t1.price,1,-1)*(t1.cprice-t1.price),min(t1.rnd),t1.product_id,name,text,t2.attribute_id FROM (SELECT RAND() as rnd,";
		$sql .= "pa2.product_id,pr.price,cpr.price as cprice,count(pa2.attribute_id) as quan FROM " . DB_PREFIX . "product_attribute pa1 INNER JOIN " . DB_PREFIX . "product_attribute pa2 ON (pa1.attribute_id = pa2.attribute_id and pa1.text = pa2.text";
		if($product_id){
			$sql .= " and pa2.product_id <> pa1.product_id";
		}
		$sql .= " and pa1.language_id = pa2.language_id) INNER JOIN " . DB_PREFIX . "product pr ON (pa2.product_id = pr.product_id and pr.status = 1) LEFT JOIN " . DB_PREFIX . "product cpr ON (pa1.product_id = cpr.product_id) 
			INNER JOIN " . DB_PREFIX . "product_to_category cat_source on(pa1.product_id = cat_source.product_id) INNER JOIN " . DB_PREFIX . "product_to_category cat on(pa2.product_id = cat.product_id";
		if (isset($one_cat) && $one_cat == 1) {
			$sql .= " AND cat.category_id = cat_source.category_id";
		}
		$sql .= ")";
		if($product_id){
			$sql .= " WHERE pa1.product_id = '" . (int)$product_id . "'";
		}
		else {
			$sql .= " WHERE 0 = 0";
		}
		$sql .= " AND pa1.language_id = '" . (int)$this->config->get('config_language_id') . "'";
		if (!empty($attributesset)) {	
			$sql .= " AND (";
			$num = 0;
			foreach ($attributes as $attribute_id) {
				if ($num != 0) {
					$sql .= ' OR ';
				}
				$num++;
				$sql .= "pa2.attribute_id = '" . (int)$attribute_id . "'";
			}
			$sql .= ")";
		}
		else {
			if (isset($categoriesset_source) && $categoriesset_source !='') {
				$sql .= " AND cat_source.category_id IN (" . implode(',',$categoriesset_source) . ")";
			}
			if (isset($categoriesset) && $categoriesset !='') {
				$sql .= " AND cat.category_id IN (" . implode(',',$categoriesset) . ")";
			}
			$sql .= " GROUP BY cpr.product_id,pr.price,cpr.price UNION ALL SELECT  RAND() as rnd,cpr.product_id,cpr.price,pr.price as cprice, 1 as quan FROM " . DB_PREFIX . "product pr LEFT JOIN " . DB_PREFIX . "product cpr ON (pr.product_id <> cpr.product_id and cpr.status = 1) 
				INNER JOIN " . DB_PREFIX . "product_to_category cat_source ON (pr.product_id = cat_source.product_id) INNER JOIN " . DB_PREFIX . "product_to_category cat ON (cpr.product_id = cat.product_id";
			if (isset($one_cat) && $one_cat == 1) {
				$sql .= " AND cat.category_id = cat_source.category_id";
			}
			$sql .= ")";
			if ($product_id) {
				$sql .= " WHERE pr.product_id = '" . (int)$product_id . "'";
			}
		}

		
		if (isset($categoriesset_source) && $categoriesset_source !='') {
			$sql .= " AND cat_source.category_id IN (" . implode(',',$categoriesset_source) . ")";
		}
		if (isset($categoriesset) && $categoriesset !='') {
				$sql .= " AND cat.category_id IN (" . implode(',',$categoriesset) . ")";
		}
		if (isset($in_stock) && $in_stock == 1) {
			if (!empty($attributesset)) {
				$sql .= " AND pr.quantity > 0";
			}
			else {
				$sql .= " AND cpr.quantity > 0";	
			}
		}
		if (!empty($attributesset)) {
			$sql .= " GROUP BY pa2.product_id,pr.price,cpr.price having quan >= " . count($attributes) . ")";
		}
		else {
			$sql .= " GROUP BY cpr.product_id,pr.price,cpr.price order by quan desc)";
		} 
		$sql .=  " t1 INNER JOIN " . DB_PREFIX . "product_to_category cat on(t1.product_id = cat.product_id)";
		if (!empty($attributesset)) {
			$sql .= " LEFT JOIN " . DB_PREFIX . "product_attribute t2 ON (t2.product_id = t1.product_id) LEFT JOIN " . DB_PREFIX . "attribute_description ad ON (ad.attribute_id = t2.attribute_id)";
		}
		
		if (!empty($attributesset)) {
			$sql .= " WHERE (0=1"; 
			foreach ($attributes as $attribute_id) {
				$sql .= " OR t2.attribute_id = '" . (int)$attribute_id . "'";
			}
			$sql .= ")";
		}
		else {
			$sql .= " LEFT JOIN (select '' as name, '' as text, 0 as attribute_id) as t2 on (0=0) WHERE 0=0";	
		}
		if (isset($categoriesset) && $categoriesset !='') {
			$sql .= " AND cat.category_id IN (" . implode(',',$categoriesset) . ")";
		}
		if (!empty($attributesset)) {
			$sql .= " AND";
			$sql .= " t2.language_id = '" . (int)$this->config->get('config_language_id') . "'"; 
		}
		$sql .= " GROUP BY IF(t1.cprice>t1.price,1,-1)*(t1.cprice-t1.price),product_id,name,text,attribute_id";
		if ($sortby == "random") {
			$sql .= " ORDER BY t1.rnd, t1.product_id";
		}
		elseif ($sortby == "price") {
			$sql .= " ORDER BY IF(t1.cprice>t1.price,1,-1)*(t1.cprice-t1.price), t1.product_id";
		}
		elseif ($sortby == "attribute") {
			$sql .= " ORDER BY t1.quan desc, t1.product_id";
		}
		else {
			$sql .= " ORDER BY t1.product_id";
		}
		//echo $sql . "</br>";
		if (!empty($attributesset)) {
			$query = $this->db->query($sql . " LIMIT " .(int)$limit*count($attributes));
		}
		else {
			$query = $this->db->query($sql . " LIMIT " .(int)$limit);
		}
		
		foreach ($query->rows as $result) {
			$product_data['products'][$result['product_id']] = $result['product_id'];
			$temp_text[$result['attribute_id']] = $result['name'] . " - " . $result['text'];
		}
		$num = 0;
		foreach ($temp_text as $text) {
			if ($num != 0) {
				$product_data['text'] .= ', ';
			}
			$num++;
			$product_data['text'] .= $text;
		}
		$product_data['text'] .= ')';
		return $product_data;
	}

    public function getProductImgMatch($product_sku)
    {
        $sql = "SELECT product_id, sku FROM " . DB_PREFIX . "product WHERE sku = '000'";

        foreach ($product_sku as $sku)
        {
            $sql .= " OR sku = '" . $sku . "'";
        }


        $query = $this->db->query($sql);

        $product_data = array();

        foreach ($query->rows as $result) {
            $product_data[$result['sku']] = $result['product_id'];
        }

        return $product_data;

    }
    public function getProductSkuFromId($product_id)
    {
        $sql = "SELECT sku FROM " . DB_PREFIX . "product WHERE product_id ='" . $product_id . "'";

        $query = $this->db->query($sql);

        foreach ($query->rows as $result) {
            return $result['sku'];
        }
    }
	
}