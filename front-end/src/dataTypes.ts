
export default interface productData {
        "product_id": number;
        "thumb": string;
        "name": string;
        "description": string;
        "price": string;
        "special": boolean;
        "tax": boolean;
        "rating": number;
        "href": string;
}

export const autofeatured_str = 'autofeatured';

export const autofeaturedIMGMatch_str = 'imgmatch';

export const autofeaturedURL = 'index.php?route=extension/module/autofeatured/ajaxGetProduct';

export const autofeaturedIMGMatchURL = 'index.php?route=extension/module/autofeatured/ajaxGetImgMatched';