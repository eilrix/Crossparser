import React from 'react';
import productData from './dataTypes';

interface Props {
    data: productData;
}
interface State {

}

class Product extends React.Component<Props, State> {


    render() {

        let data = this.props.data;

        let price;
        if (!data.special) {
            price = <div>{data.price}</div>
        }
        else {
            price = <div>
                <span className="price-new">{data.special}</span>
                <span className="price-old">{data.price}</span>
            </div>
        }

        return (
            <div className="product-layout col-lg-3 col-md-3 col-sm-6 col-xs-12">
                <div className="product-thumb transition">
                    <div className="image">
                        <a>
                            <div className="quick-view">
                                <div onClick={(event) => {
                                    event.stopPropagation();
                                    (window as any).get_oct_popup_product_view(data.product_id)
                                }}
                                    className="current-link">Быстрый просмотр</div>
                            </div>
                            <img src="/image/catalog/1lazy/oct_loader_product.gif"
                                data-original={data.thumb}
                                alt={data.name}
                                title={data.name}
                                className="img-responsive lazy" />
                        </a>
                    </div>
                    <div className="caption">
                        <h4><a href={data.href}>{data.name}</a></h4>

                        <p className="price">{price}</p>
                        <button id="autofeaturedWishlist"
                            className="cbutton cbutton--effect-nikola"
                            type="button"
                            data-toggle="tooltip"
                            onClick={() => { (window as any).get_oct_popup_add_to_wishlist(data.product_id) }}>
                            <i className="fa fa-heart"></i>
                        </button>
                    </div>
                </div>
            </div>
        )
    }

}

export default Product;