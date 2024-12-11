// ===========================================Done=========================================================

import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import HelpPage from "./pages/Help and Privacy Policy/HelpPage";
import PrivacyPolicyPage from "./pages/Help and Privacy Policy/PrivacyPolicyPage";
import RegistrationPage from "./pages/RegistrationPage";
import LoginPage from "./pages/LoginPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import TryNowPage from "./pages/Try Now/TryNowPage";
import Dashboard from "./pages/Dashboard/Dashboard";
import Account from "./pages/Account";
import CartPage from "./pages/Dashboard/CartPage";
import axios from "axios";

// Helper function to validate the access token
const isAuthenticated = () => {
    const accessToken = localStorage.getItem("accessToken");
    const accessTokenExpiry = localStorage.getItem("accessTokenExpiry");
    const currentTime = new Date().getTime();

    return accessToken && accessTokenExpiry && currentTime < accessTokenExpiry;
};

// PrivateRoute component
const PrivateRoute = ({ element }) => {
    return isAuthenticated() ? element : <Navigate to="/signin" />;
};

function App() {
    const [cartItems, setCartItems] = useState([]);
    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

    // Fetch cart items when the app loads
    useEffect(() => {
        if (isAuthenticated()) {
            fetchCartItems();
        }
    }, []);

    const fetchCartItems = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/cart/`, {
                headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
            });
            setCartItems(response.data || []);
        } catch (error) {
            console.error("Error fetching cart items:", error);
        }
    };

    const handleRemoveFromCart = async (cartId) => {
        try {
            const response = await axios.delete(`${API_BASE_URL}/cart/remove/${cartId}/`, {
                headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` },
            });
            alert(response.data.message);
            fetchCartItems(); // Refresh cart items after removal
        } catch (error) {
            console.error("Error removing item from cart:", error);
            alert("Failed to remove product from cart. Please try again.");
        }
    };

    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/help" element={<HelpPage />} />
                <Route path="/privacy" element={<PrivacyPolicyPage />} />
                <Route path="/signup" element={<RegistrationPage />} />
                <Route path="/signin" element={<LoginPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route
                    path="/try-now"
                    element={<TryNowPage />}
                />
                <Route
                    path="/dashboard"
                    element={
                        <PrivateRoute
                            element={<Dashboard cartItems={cartItems} handleRemoveFromCart={handleRemoveFromCart} />}
                        />
                    }
                />
                <Route
                    path="/account"
                    element={
                        <PrivateRoute element={<Account />} />
                    }
                />
                <Route
                    path="/cart"
                    element={
                        <PrivateRoute
                            element={<CartPage cartItems={cartItems} handleRemoveFromCart={handleRemoveFromCart} />}
                        />
                    }
                />
            </Routes>
        </Router>
    );
}

export default App;
