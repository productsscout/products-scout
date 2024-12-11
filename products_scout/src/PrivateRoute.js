import React from "react";
import { Navigate } from "react-router-dom";

// PrivateRoute component to protect routes
const PrivateRoute = ({ element: Component, ...rest }) => {
    const isAuthenticated = localStorage.getItem("accessToken"); // Check if the user is authenticated

    // If authenticated, render the route's component; otherwise, redirect to login
    return isAuthenticated ? <Component {...rest} /> : <Navigate to="/signin" />;
};

export default PrivateRoute;
