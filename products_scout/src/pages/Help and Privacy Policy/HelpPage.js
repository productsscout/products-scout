// ===========================================Done=========================================================

import React from "react";
import "./HelpPage.css";

const HelpPage = () => {
    const SUPPORT_EMAIL = process.env.REACT_APP_SUPPORT_EMAIL || "support@productsscout.com";

    return (
        <div className="help-page">
            <h1>Help Center</h1>
            <p>
                Welcome to the <span className="highlight">Products Scout Help Center</span>. We're here to assist you with any questions or concerns you may have. Explore the sections below to find the help you need.
            </p>

            <h2>1. Getting Started</h2>
            <p>If you're new to <span className="highlight">Products Scout</span>, here's how you can get started:</p>
            <ul className="help-list">
                <li>
                    <strong>Sign Up:</strong> Create an account by visiting the <a href="/signup" className="help-link" aria-label="Go to Sign-Up page">Sign-Up</a> page. Provide your details to register.
                </li>
                <li>
                    <strong>Login:</strong> Use your email and password to log in via the <a href="/signin" className="help-link" aria-label="Go to Login page">Login</a> page.
                </li>
                <li>
                    <strong>Try Now:</strong> Not ready to sign up? Click the "Try PS" button on the homepage for a limited experience.
                </li>
            </ul>

            <h2>2. Product Recommendations</h2>
            <p>Here's how to get tailored product suggestions:</p>
            <ul className="help-list">
                <li>Enter a detailed description of what you're looking for in the prompt box.</li>
                <li>Click the <strong>"Find"</strong> button to see AI-powered recommendations.</li>
                <li>
                    View two sections of product results:
                    <ul className="nested-list">
                        <li><strong>Best for You:</strong> Exact or closely matching products.</li>
                        <li><strong>Also Preferred:</strong> Related or recommended products.</li>
                    </ul>
                </li>
            </ul>

            <h2>3. Account Management</h2>
            <p>Manage your account easily:</p>
            <ul className="help-list">
                <li>
                    <strong>Update Profile:</strong> Visit the "Account" section in the sidebar to update your profile details.
                </li>
                <li>
                    <strong>Reset Password:</strong> Forgot your password? Click on <a href="/forgot-password" className="help-link" aria-label="Reset Password">Forgot Password</a> on the login page to reset it.
                </li>
                <li>
                    <strong>View History:</strong> Access your previous chats and product searches from the "History" section in the sidebar.
                </li>
            </ul>

            <h2>4. Troubleshooting</h2>
            <p>If you encounter issues, here are some solutions:</p>
            <ul className="help-list">
                <li>
                    <strong>Can't Log In:</strong> Double-check your email and password. If you forgot your password, reset it <a href="/forgot-password" className="help-link" aria-label="Reset Password here">here</a>.
                </li>
                <li>
                    <strong>Products Not Loading:</strong> Ensure you have a stable internet connection and try refreshing the page.
                </li>
                <li>
                    <strong>Session Expired:</strong> Log in again to continue using the platform.
                </li>
            </ul>

            <h2>5. Frequently Asked Questions</h2>
            <ul className="help-list">
                <li>
                    <strong>What is Products Scout?</strong> Products Scout is an AI-powered platform that provides tailored product recommendations to make your shopping experience easier and faster.
                </li>
                <li>
                    <strong>Do I need an account?</strong> While you can explore our platform with the "Try PS" option, signing up provides a full experience, including saved searches and personalized recommendations.
                </li>
                <li>
                    <strong>How does the recommendation system work?</strong> We use advanced AI and real-time data from trusted platforms like Amazon to deliver the best product matches.
                </li>
            </ul>

            <h2>6. Contact Us</h2>
            <p>If you need further assistance, please reach out to us:</p>
            <ul className="contact-list">
                <li>
                    Email: <a href={`mailto:${SUPPORT_EMAIL}`} className="help-link" aria-label="Send an email to support">{SUPPORT_EMAIL}</a>
                </li>
                <li>Address: Dehradun, Uttarakhand (INDIA)</li>
            </ul>
        </div>
    );
};

export default HelpPage;
