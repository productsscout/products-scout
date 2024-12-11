// ===========================================Done=========================================================

import React, { useState, useEffect, useRef } from "react";
import "./MainDashboard.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { generateResponseMain, fetchFeaturesAndProductsMain } from "./generateResponseMain";
import findbtn from "../assets/ion.png";

const MainDashboard = ({ userName, tagline, isTransitioning, setTagline, setIsTransitioning, handleAddToCart }) => {
    const [queryStarted, setQueryStarted] = useState(false);
    const [isQueryInProgress, setIsQueryInProgress] = useState(false);
    const [isFading, setIsFading] = useState(false);
    const [isButtonDisabled, setIsButtonDisabled] = useState(true);
    const [userQuery, setUserQuery] = useState("");
    const [conversation, setConversation] = useState([]);
    const [isLoadingBot, setIsLoadingBot] = useState(false);
    const [isLoadingProducts, setIsLoadingProducts] = useState(false);
    const userPromptRef = useRef(null);
    const conversationContainerRef = useRef(null);

    // Dynamically adjust textarea height
    const handleTextareaChange = (event) => {
        const textarea = event.target;
        textarea.style.height = "0px";
        const scrollHeight = textarea.scrollHeight;
        textarea.style.height = `${Math.min(scrollHeight, 75)}px`;

        setUserQuery(textarea.value);
        setIsButtonDisabled(textarea.value.trim() === "" || isQueryInProgress);
    };

    // Update tagline after 5 seconds
    useEffect(() => {
        const taglineTimer = setTimeout(() => {
            setIsTransitioning(true);
            setTimeout(() => {
                setTagline("Find your best product now");
                setIsTransitioning(false);
            }, 1000);
        }, 5000);

        return () => clearTimeout(taglineTimer);
    }, [setTagline, setIsTransitioning]);

    // Scroll to the bottom of the conversation container
    useEffect(() => {
        if (conversationContainerRef.current) {
            conversationContainerRef.current.scrollTop =
                conversationContainerRef.current.scrollHeight;
        }
    }, [conversation]);

    // Handle Enter key press to trigger "Find" button
    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            if (isQueryInProgress) {
                // Prevent submission while a query is in progress
                event.preventDefault();
                return;
            }
            event.preventDefault();
            handleFind();
        }
    };

    // Display response word by word
    const displayGeneratedResponse = (response, onComplete) => {
        const words = response.split(" ");
        let index = 0;

        // Add an empty bot message to the conversation initially
        setConversation((prev) => [
            ...prev,
            { type: "bot", message: "" }
        ]);

        // Interval for word-by-word rendering
        const intervalId = setInterval(() => {
            setConversation((prev) => {
                const updatedConversation = [...prev];
                // Update only the latest bot message
                updatedConversation[updatedConversation.length - 1].message = words
                    .slice(0, index + 1)
                    .join(" ");
                return updatedConversation;
            });

            index += 1;

            // Stop interval after the last word
            if (index >= words.length) {
                clearInterval(intervalId); // Ensure interval is cleared
                if (onComplete) onComplete(); // Notify when rendering is complete
            }
        }, 12); // Adjust speed (in ms) as needed
    };


    // Handle the find button
    const handleFind = async () => {
        const query = userQuery.trim();
        if (!query) return;

        setIsFading(true);
        setTimeout(() => {
            setQueryStarted(true);
            setIsFading(false);
        }, 300);

        setConversation((prev) => [...prev, { type: "user", message: query }]);
        setIsLoadingBot(true);
        setUserQuery("");
        userPromptRef.current.style.height = "40px";
        setIsQueryInProgress(true);

        try {
            const controller = new AbortController(); // Add timeout controller
            const timeoutId = setTimeout(() => controller.abort(), 10000); // Set timeout (10 seconds)

            // Step 1: Generate response
            const { generatedResponse } = await generateResponseMain(query, { signal: controller.signal });
            clearTimeout(timeoutId); // Clear timeout if operation completes

            // Display bot response word by word and wait until it's complete
            displayGeneratedResponse(generatedResponse, () => {
                // Step 2: Fetch products after response rendering is complete
                setIsLoadingProducts(true);

                fetchFeaturesAndProductsMain(query).then(({ products }) => {
                    if (products.length === 0) {
                        setConversation((prev) => [
                            ...prev,
                            { type: "bot", message: "No products found for your query. Please try another." },
                        ]);
                    } else {
                        setConversation((prev) => [
                            ...prev,
                            {
                                type: "products",
                                products: {
                                    bestForYou: products
                                        .sort((a, b) => parseFloat(b.product_star_rating) - parseFloat(a.product_star_rating))
                                        .slice(0, 8),
                                    alsoPreferred: products.sort(() => Math.random() - 0.5).slice(0, 12),
                                },
                            },
                        ]);
                    }
                    setIsLoadingProducts(false);
                }).catch((error) => {
                    setConversation((prev) => [
                        ...prev,
                        { type: "bot", message: "An error occurred while fetching products. Please try again." },
                    ]);
                    setIsLoadingProducts(false);
                });
            });

            setIsLoadingBot(false);
        } catch (error) {
            if (error.name === "AbortError") {
                setConversation((prev) => [
                    ...prev,
                    { type: "bot", message: "The request timed out. Please try again." },
                ]);
            } else {
                setConversation((prev) => [
                    ...prev,
                    { type: "bot", message: "An error occurred. Please try again." },
                ]);
            }
            setIsLoadingBot(false);
            setIsLoadingProducts(false);
        } finally {
            setIsQueryInProgress(false);
        }
    };


    return (
        <div className={`main-content ${queryStarted ? "query-active" : ""}`}>
            {!queryStarted && (
                <div className={`greeting-section ${isFading ? "fade-out" : "fade-in"}`}>
                    <h1>Welcome, {userName || "..."}</h1>
                    <p className={isTransitioning ? "tagline-transition" : "new-tagline"}>
                        {tagline}
                    </p>
                </div>
            )}
            <div
                className={`prompt-section ${queryStarted ? "shifted-prompt" : ""} ${
                    isFading ? "fade-out" : "fade-in"
                }`}
            >
                <textarea
                    id="user-prompt1"
                    ref={userPromptRef}
                    placeholder="Ask me about any products..."
                    onChange={handleTextareaChange}
                    onKeyDown={handleKeyDown}
                    value={userQuery}
                    className={queryStarted ? "shifted-textarea" : "unsifted-textarea"}
                ></textarea>
                <button
                    id="find-button-dashboard"
                    className={queryStarted ? "shifted-button" : "unsifted-button"}
                    onClick={handleFind}
                    disabled={isButtonDisabled}
                >
                    {queryStarted ? (
                        <img src={findbtn} alt="Search" className="button-icon" />
                    ) : (
                        "Find"
                    )}
                </button>
            </div>

            {/* Chat Section */}
            <div
                className={`${
                    queryStarted ? "shifted-conversation-container" : "conversation-container"
                }`}
                ref={conversationContainerRef}
            >
                {conversation.map((msg, index) => {
                    if (msg.type === "user" || msg.type === "bot") {
                        return (
                            <div
                                key={index}
                                className={`message ${
                                    msg.type === "user" ? "user-message" : "bot-message"
                                }`}
                            >
                                <ReactMarkdown
                                    children={msg.message}
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeRaw]}
                                    components={{
                                        h1: ({ node, ...props }) => {
                                            const content = props.children?.length > 0 ? props.children : " "; // Safe fallback for children
                                            return <h1 style={{ fontSize: "1.5em", margin: "10px 0", color: "#333" }} {...props}>{content}</h1>;
                                        },
                                        h2: ({ node, ...props }) => {
                                            const content = props.children?.length > 0 ? props.children : " "; // Safe fallback for children
                                            return <h2 style={{ fontSize: "1.2em", margin: "8px 0", color: "#555" }} {...props}>{content}</h2>;
                                        },
                                        h3: ({ node, ...props }) => {
                                            const content = props.children?.length > 0 ? props.children : " "; // Safe fallback for children
                                            return <h3 style={{ fontSize: "1em", margin: "6px 0", color: "#777" }} {...props}>{content}</h3>;
                                        },
                                        h4: ({ node, ...props }) => {
                                            const content = props.children?.length > 0 ? props.children : " "; // Safe fallback for children
                                            return <h4 style={{ fontSize: "0.9em", margin: "5px 0", color: "#999" }} {...props}>{content}</h4>;
                                        },
                                        h5: ({ node, ...props }) => {
                                            const content = props.children?.length > 0 ? props.children : " "; // Safe fallback for children
                                            return <h5 style={{ fontSize: "0.8em", margin: "4px 0", color: "#bbb" }} {...props}>{content}</h5>;
                                        },
                                        h6: ({ node, ...props }) => {
                                            const content = props.children?.length > 0 ? props.children : " "; // Safe fallback for children
                                            return <h6 style={{ fontSize: "0.7em", margin: "3px 0", color: "#ccc" }} {...props}>{content}</h6>;
                                        },
                                        p: ({ node, ...props }) => (
                                            <p style={{ margin: "10px 0", color: "#333" }} {...props}>
                                                {props.children || " "} {/* Safe fallback */}
                                            </p>
                                        ),
                                        ul: ({ node, ...props }) => (
                                            <ul style={{ paddingLeft: "20px", color: "#333" }} {...props}>
                                                {props.children || " "} {/* Safe fallback */}
                                            </ul>
                                        ),
                                        ol: ({ node, ...props }) => (
                                            <ol style={{ paddingLeft: "20px", color: "#333" }} {...props}>
                                                {props.children || " "} {/* Safe fallback */}
                                            </ol>
                                        ),
                                        li: ({ node, ...props }) => (
                                            <li style={{ margin: "5px 0", color: "#333" }} {...props}>
                                                {props.children || " "} {/* Safe fallback */}
                                            </li>
                                        ),
                                        blockquote: ({ node, ...props }) => (
                                            <blockquote
                                                style={{
                                                    padding: "10px",
                                                    margin: "10px 0",
                                                    borderLeft: "4px solid #ccc",
                                                    color: "#555",
                                                }}
                                                {...props}
                                            >
                                                {props.children || " "} {/* Safe fallback */}
                                            </blockquote>
                                        ),
                                        strong: ({ node, ...props }) => (
                                            <strong
                                                style={{
                                                    fontWeight: "bold",
                                                    color: "#000",
                                                    backgroundColor: "#f0f0f0",
                                                    padding: "0 5px",
                                                }}
                                                {...props}
                                            >
                                                {props.children || " "} {/* Safe fallback */}
                                            </strong>
                                        ),
                                        b: ({ node, ...props }) => (
                                            <b
                                                style={{
                                                    fontWeight: "bold",
                                                    color: "#000",
                                                    backgroundColor: "#f0f0f0",
                                                    padding: "0 5px",
                                                }}
                                                {...props}
                                            >
                                                {props.children || " "} {/* Safe fallback */}
                                            </b>
                                        ),
                                        em: ({ node, ...props }) => (
                                            <em style={{ fontStyle: "italic", color: "#555" }} {...props}>
                                                {props.children || " "} {/* Safe fallback */}
                                            </em>
                                        ),
                                        code: ({ node, inline, ...props }) => {
                                            const content = props.children || " "; // Safe fallback
                                            if (inline) {
                                                return (
                                                    <code
                                                        style={{
                                                            backgroundColor: "#f5f5f5",
                                                            padding: "2px 4px",
                                                            borderRadius: "4px",
                                                            fontSize: "0.9em",
                                                        }}
                                                        {...props}
                                                    >
                                                        {content}
                                                    </code>
                                                );
                                            }
                                            return (
                                                <pre
                                                    style={{
                                                        backgroundColor: "#f5f5f5",
                                                        padding: "10px",
                                                        borderRadius: "4px",
                                                        fontSize: "0.9em",
                                                    }}
                                                    {...props}
                                                >
                                                    {content}
                                                </pre>
                                            );
                                        },
                                        a: ({ node, ...props }) => (
                                            <a
                                                style={{
                                                    color: "#007bff",
                                                    textDecoration: "none",
                                                }}
                                                href={props.href}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                aria-label={props.children ? props.children : "Link"} // Provide an aria-label for accessibility
                                                {...props}
                                            >
                                                {props.children || "Link"} {/* Default to 'Link' if no content */}
                                            </a>
                                        ),
                                        img: ({ node, ...props }) => (
                                            <img
                                                style={{
                                                    maxWidth: "100%",
                                                    height: "auto",
                                                    borderRadius: "8px",
                                                    margin: "10px 0",
                                                }}
                                                alt={props.alt || "Image"} // Use alt prop for accessibility
                                                {...props}
                                            />
                                        ),
                                        br: ({ node, ...props }) => <br />,
                                    }}
                                />
                            </div>
                        );
                    }
                    if (msg.type === "products") {
                        const { bestForYou, alsoPreferred } = msg.products;

                    if (!bestForYou.length && !alsoPreferred.length) {
                          return (
                            <div key={index} className="fallback-message">
                              No products found for your query. Please try a different one.
                            </div>
                          );
                        }

                        return (
                            <div key={index} className="products-container">
                                {bestForYou.length > 0 && (
                                    <>
                                    <h3 className="section-title">Best for You</h3>
                                <div className="best-for-you horizontal-scroll">
                                    <div className="product-list">
                                        {msg.products.bestForYou.map((product, index) => (
                                            <div key={index} className="product-card">
                                                <img
                                                    className="product-image"
                                                    src={product.product_photo}
                                                    alt={product.product_title}
                                                />
                                                <h4
                                                    className="product-title"
                                                    title={product.product_title}
                                                >
                                                    {product.product_title}
                                                </h4>
                                                <p className="product-price">
                                                    Price: {product.product_price}
                                                </p>
                                                <p className="product-rating">
                                                    Rating: {product.product_star_rating}
                                                </p>
                                                <a
                                                    className="product-link"
                                                    href={product.product_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                >
                                                    View on Amazon
                                                </a>
                                                <button
                                                    className="add-to-cart-button"
                                                    onClick={() => handleAddToCart(product)} // Call add-to-cart function
                                                >
                                                    Add to Cart
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                            )}
                                {alsoPreferred.length > 0 && (
                                        <>
                                            <h3 className="section-title">Also Preferred</h3>
                                <div className="also-preferred horizontal-scroll">
                                    <div className="product-list">
                                        {msg.products.alsoPreferred.map((product, index) => (
                                            <div key={index} className="product-card">
                                                <img
                                                    className="product-image"
                                                    src={product.product_photo}
                                                    alt={product.product_title}
                                                />
                                                <h4
                                                    className="product-title"
                                                    title={product.product_title}
                                                >
                                                    {product.product_title}
                                                </h4>
                                                <p className="product-price">
                                                    Price: {product.product_price}
                                                </p>
                                                <p className="product-rating">
                                                    Rating: {product.product_star_rating}
                                                </p>
                                                <a
                                                    className="product-link"
                                                    href={product.product_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                >
                                                    View on Amazon
                                                </a>
                                                <button
                                                    className="add-to-cart-button"
                                                    onClick={() => handleAddToCart(product)} // Call add-to-cart function
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
                {isLoadingBot && (
                    <div className="loading-indicator bot-message">
                        <div className="gradient-line1"></div>
                        <div className="gradient-line2"></div>
                        <div className="gradient-line3"></div>
                    </div>
                )}
                {isLoadingProducts && (
                    <div className="loading-message">
                        <div className="loading-dotted-spinner">
                            {[...Array(8)].map((_, index) => (
                                <div key={index} className={`dot dot-${index + 1}`}></div>
                            ))}
                        </div>
                        <span className="loading-text">Loading products...</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MainDashboard;
