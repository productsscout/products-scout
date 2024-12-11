// ===========================================Done=========================================================

import React, { useState, useEffect } from "react";
import axios from "axios";
import "./MainDashboard.css";
import DashboardSidebar from "./DashboardSidebar";
import MainDashboard from "./MainDashboard";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
    const [userName, setUserName] = useState("");
    const [tagline, setTagline] = useState("Don't test, only best");
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [isSidebarVisible, setIsSidebarVisible] = useState(true);
    const [cartItems, setCartItems] = useState([]);

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
    const navigate = useNavigate();

    useEffect(() => {
        validateAccessToken();
        const tokenValidationInterval = setInterval(validateAccessToken, 5 * 60 * 1000); // Check every 5 minutes
        fetchUserName();
        fetchCartItems();

        return () => clearInterval(tokenValidationInterval); // Cleanup on unmount
    }, []);

    const fetchUserName = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/user-first-name/`, {
                headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
            });
            if (response.data?.first_name) {
                setUserName(response.data.first_name);
            }
        } catch (error) {
            console.error("Error fetching username:", error);
            alert("Failed to fetch username. Please try again.");
        }
    };

    const fetchCartItems = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/cart/`, {
                headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
            });
            setCartItems(response.data || []);
        } catch (error) {
            console.error("Error fetching cart items:", error);
            alert("Failed to fetch cart items. Please try again.");
        }
    };

    const handleAddToCart = async (product) => {
        try {
            const response = await axios.post(
                `${API_BASE_URL}/cart/add/`,
                {
                    product_name: product.product_title,
                    product_price: parseFloat(product.product_price.replace(/[^0-9.]/g, "")), // Extract numeric value
                    product_quantity: 1,
                    product_star_rating: product.product_star_rating,
                    product_photo: product.product_photo,
                    product_url: product.product_url,
                },
                {
                    headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
                }
            );
            alert(response.data.message);
            fetchCartItems();
        } catch (error) {
            console.error("Error adding to cart:", error);
            alert("You cannot add products to the cart if the price is unavailable.");
        }
    };

    const handleRemoveFromCart = async (cartId) => {
        try {
            const response = await axios.delete(`${API_BASE_URL}/cart/remove/${cartId}/`, {
                headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
            });
            alert(response.data.message);
            fetchCartItems();
        } catch (error) {
            console.error("Error removing from cart:", error);
            alert("Failed to remove product from cart. Please try again.");
        }
    };

    const validateAccessToken = () => {
        const accessToken = localStorage.getItem("accessToken");
        const accessTokenExpiry = localStorage.getItem("accessTokenExpiry");

        if (!accessToken || !accessTokenExpiry) {
            alert("No valid session found. Please log in.");
            localStorage.clear();
            navigate("/signin");
            return;
        }

        const currentTime = new Date().getTime();
        if (currentTime > accessTokenExpiry) {
            alert("Your session has expired. Please log in again.");
            localStorage.clear();
            navigate("/signin");
        }
    };

    const handleLogout = async () => {
        try {
            const refreshToken = localStorage.getItem("refreshToken");
            await axios.post(`${API_BASE_URL}/logout/`, { refresh_token: refreshToken });
            localStorage.clear();
            navigate("/signin");
        } catch (error) {
            console.error("Error logging out:", error);
            alert("Failed to log out. Please try again.");
        }
    };

    return (
        <div className={`dashboard ${isSidebarVisible ? "with-sidebar" : "without-sidebar"}`}>
            <DashboardSidebar
                cartItems={cartItems}
                handleRemoveFromCart={handleRemoveFromCart}
                handleLogout={handleLogout}
                isSidebarVisible={isSidebarVisible}
                setIsSidebarVisible={setIsSidebarVisible}
            />
            <MainDashboard
                userName={userName}
                tagline={tagline}
                isTransitioning={isTransitioning}
                setTagline={setTagline}
                setIsTransitioning={setIsTransitioning}
                isSidebarVisible={isSidebarVisible}
                cartItems={cartItems}
                handleAddToCart={handleAddToCart}
                handleRemoveFromCart={handleRemoveFromCart}
            />
        </div>
    );
};

export default Dashboard;
