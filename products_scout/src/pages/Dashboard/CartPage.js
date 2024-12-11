// ===========================================Done=========================================================

import React from "react";
import "./CartPage.css";

const CartPage = ({ cartItems, handleRemoveFromCart }) => {
    return (
        <div className="cart-page">
            <h1>Your Cart</h1>
            {cartItems.length > 0 ? (
                <ul className="cart-list">
                    {cartItems.map((item) => (
                        <li key={item.id} className="cart-item">
                            <img
                                src={item.product_photo || "https://via.placeholder.com/150"}
                                alt={item.product_name || "Product image"}
                                className="cart-item-photo"
                            />
                            <div className="cart-item-details">
                                <h4 title={item.product_name || "Unknown Product"}>
                                    {item.product_name || "Product name unavailable"}
                                </h4>
                                <p>
                                    Price: {item.product_price || "N/A"}
                                </p>
                                <a
                                    href={item.product_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="view-on-amazon-link"
                                    aria-label={`View ${item.product_name || "this product"} on Amazon`}
                                >
                                    View on Amazon
                                </a>
                                <button
                                    onClick={() => handleRemoveFromCart(item.id)}
                                    className="remove-from-cart-button"
                                    aria-label={`Remove ${item.product_name || "this product"} from cart`}
                                >
                                    Remove
                                </button>
                            </div>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="empty-cart-message">Your cart is empty. Start adding your favorite products!</p>
            )}
        </div>
    );
};

export default CartPage;
