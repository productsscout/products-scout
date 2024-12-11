// ===========================================Done=========================================================

import React, { useState, useEffect, useRef } from "react";
import "./TryNowPage.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { generateResponse } from "./generateResponse";
import findbtn from "../assets/ion.png";
import {useNavigate} from "react-router-dom";

const TryNowPage = ({ handleAddToCart }) => {
    const [queryStarted, setQueryStarted] = useState(false);
    const [isFading, setIsFading] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [userQuery, setUserQuery] = useState("");
    const [conversation, setConversation] = useState([]);
    const [popupVisible, setPopupVisible] = useState(false); // State for signup popup visibility
    const [cartPopupVisible, setCartPopupVisible] = useState(false); // State for cart popup visibility
    const [isQueryInProgress, setIsQueryInProgress] = useState(false); // Track if query is in progress

    const userPromptRef = useRef(null);
    const conversationContainerRef = useRef(null);
    const findButtonRef = useRef(null);

    const navigate = useNavigate();


    const queriesCount = parseInt(localStorage.getItem("queriesCount")) || 0;

    // Scroll to the bottom of the conversation container
    useEffect(() => {
        if (conversationContainerRef.current) {
            conversationContainerRef.current.scrollTop =
                conversationContainerRef.current.scrollHeight;
        }
    }, [conversation]);

    // Handle the "Find" button click
    const handleFind = async () => {
        const query = userQuery.trim();
        if (!query || isQueryInProgress) return;  // Don't proceed if query is in progress

        console.log("User Query:", query);
        setIsQueryInProgress(true); // Start query processing
        setIsFading(true);
        setTimeout(() => {
            setQueryStarted(true);
            setIsFading(false);
        }, 300);

        setConversation((prev) => [...prev, { type: "user", message: query }]);

        setIsLoading(true);
        setUserQuery("");
        userPromptRef.current.style.height = "40px";

        // Increase query count in localStorage
        let updatedQueriesCount = queriesCount + 1;
        localStorage.setItem("queriesCount", updatedQueriesCount);

        // Show popup after 3 queries
        if (updatedQueriesCount >= 4) {
            setPopupVisible(true);
        }

        try {
            const { generatedResponse, products } = await generateResponse(query);
            setConversation((prev) => [
                ...prev,
                { type: "bot", message: generatedResponse },
                {
                    type: "products",
                    products: {
                        recommended: products
                            .sort((a, b) => parseFloat(b.product_star_rating) - parseFloat(a.product_star_rating))
                            .slice(0, 15),
                    },
                },
            ]);
        } catch (error) {
            setConversation((prev) => [
                ...prev,
                { type: "bot", message: "An error occurred. Please try again." },
            ]);
        } finally {
            setIsQueryInProgress(false); // End query processing
            setIsLoading(false);
        }
    };

    const handleAddToCartClick = (product) => {
        // Show the add to cart popup if the user clicks the "Add to Cart" button
        setCartPopupVisible(true);
    };

    const closePopup = () => {
        setPopupVisible(false);
        setCartPopupVisible(false);
    };

    return (
        <div className={`try-main-content ${queryStarted ? "try-query-active" : ""}`}>
            {!queryStarted && (
                <div className={`try-greeting-section ${isFading ? "try-fade-out" : "try-fade-in"}`}>
                    <h1 className="try-h1">Welcome, User!</h1>
                    <p className="try-tagline">Find your best product now</p>
                </div>
            )}
            <div
                className={`try-prompt-section ${queryStarted ? "try-shifted-prompt" : ""} ${
                    isFading ? "try-fade-out" : "try-fade-in"
                }`}
            >
                <textarea
                    id="try-user-prompt1"
                    ref={userPromptRef}
                    placeholder="Ask me about any products..."
                    value={userQuery}
                    className={queryStarted ? "try-shifted-textarea" : "try-unsifted-textarea"}
                    onChange={(e) => setUserQuery(e.target.value)}
                ></textarea>
                <button
                    id="try-find-button-dashboard"
                    className={queryStarted ? "try-shifted-button" : "try-unsifted-button"}
                    onClick={handleFind}
                    ref={findButtonRef}
                    disabled={isQueryInProgress || userQuery.trim() === ""} // Disable the button while query is in progress or input is empty

                >
                    {queryStarted ? (
                        <img src={findbtn} alt="Search" className="try-button-icon" />
                    ) : (
                        "Find"
                    )}
                </button>
            </div>

            {/* Chat Section */}
            <div
                className={`${
                    queryStarted ? "try-shifted-conversation-container" : "try-conversation-container"
                }`}
                ref={conversationContainerRef}
            >
                {conversation.map((msg, index) => {
                    if (msg.type === "user" || msg.type === "bot") {
                        return (
                            <div
                                key={index}
                                className={`message ${
                                    msg.type === "user" ? "try-user-message" : "try-bot-message"
                                }`}
                            >
                                <ReactMarkdown
                                    children={msg.message}
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeRaw]}
                                />
                            </div>
                        );
                    } else if (msg.type === "products") {
                        return (
                            <div key={index} className="try-products-chat-container">
                                {msg.products.recommended.length > 0 && (
                                    <>
                                        <h3 className="try-section-title">Recommended</h3>
                                        <div className="try-recommended horizontal-scroll">
                                            <div className="try-product-list">
                                                {msg.products.recommended.map((product, index) => (
                                                    <div key={index} className="try-product-card">
                                                        <img
                                                            className="try-product-image"
                                                            src={product.product_photo}
                                                            alt={product.product_title}
                                                        />
                                                        <h4
                                                            className="try-product-title"
                                                            title={product.product_title}
                                                        >
                                                            {product.product_title}
                                                        </h4>
                                                        <p className="try-product-price">
                                                            Price: {product.product_price}
                                                        </p>
                                                        <p className="try-product-rating">
                                                            Rating: {product.product_star_rating}
                                                        </p>
                                                        <a
                                                            className="try-product-link"
                                                            href={product.product_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                        >
                                                            View on Amazon
                                                        </a>
                                                        <button
                                                            className="try-add-to-cart-button"
                                                            onClick={() => handleAddToCartClick(product)}
                                                        >
                                                            Add to Cart
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        );
                    }
                    return null;
                })}
                {isLoading && (
                    <div className="try-loading-indicator bot-message">
                        <div className="try-gradient-line1"></div>
                        <div className="try-gradient-line2"></div>
                        <div className="try-gradient-line3"></div>
                    </div>
                )}
            </div>

            {/* Popup for signup after 3 queries */}
            {popupVisible && (
                <div className="try-popup-overlay">
                    <div className="try-popup-content">
                        <h2>You've reached the maximum number of queries!</h2>
                        <p>Please sign up to continue exploring more products.</p>
                        <button className="try-signup-button" onClick={() => navigate("/signup")}>
                            Sign Up
                        </button>
                    </div>
                </div>
            )}

            {/* Popup for Add to Cart (Signup Required) */}
            {cartPopupVisible && (
                <div className="try-popup-overlay">
                    <div className="try-popup-content">
                        <h2>Login to add products to your cart!</h2>
                        <button className="try-signup-button" onClick={() => navigate("/signin")}>
                            Login
                        </button>
                        <button className="try-close-button" onClick={closePopup}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TryNowPage;
