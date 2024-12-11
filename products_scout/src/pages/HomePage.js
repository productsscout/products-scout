// ===========================================Done=========================================================

import React from "react";
import "./HomePage.css";
import CompanyLogo from "./assets/logo.png"; // Updated logo path
import ArrowIcon from "./assets/arrow-icon.svg"; // Ensure this file exists or replace with a font icon
import AiImg from "./assets/Ai-img.jpg";
import Xlogo from "./assets/x-logo.png"

const HomePage = () => {
    // Use environment variables for base paths
    const baseSignupPath = process.env.REACT_APP_SIGNUP_PATH || "/signup";
    const baseSigninPath = process.env.REACT_APP_SIGNIN_PATH || "/signin";
    const baseTryNowPath = process.env.REACT_APP_TRY_NOW_PATH || "/try-now";


    return (
        <div className="homepage">
            {/* Header */}
            <header className="homepage-header">
                <div className="logo">
                    <img src={CompanyLogo} alt="Company Logo" className="company-logo"/>
                </div>
                <h1 className="company-name">Products Scout</h1>
                <nav className="nav-bar">
                    <ul className="nav-links">
                        <li><a href="#about">About Us</a></li>
                        <li><a href={baseSignupPath}>Sign Up</a></li>
                        <li><a href={baseSigninPath}>Login</a></li>
                    </ul>
                </nav>
            </header>

            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <h2 className="dynamic-glow">Your perfect product is just a few clicks away</h2>
                    <p className="tagline">Explore now!</p>
                    <button className="try-now-btn" onClick={() => (window.location.href = baseTryNowPath)}>
                        Try PS
                        <img src={ArrowIcon} alt="Arrow Icon" className="arrow-icon"/>
                    </button>
                </div>
                <div className="hero-overlay"></div>
            </section>

            {/* About Section */}
            <section className="about-section" id="about">
                <div className="about-content">
                    <h2>About <span className="highlight">Products Scout</span></h2>
                    <p className="about-description">
                        Welcome to <span className="highlight">Products Scout</span>, your trusted partner in finding
                        the perfect
                        products.
                        We leverage cutting-edge AI and API integrations to provide you with fast, reliable, and
                        personalized
                        product as per your requirements.
                    </p>
                    <ul className="features-list">
                        <li>🌟 <span>Experience next-level AI technology for smarter product searches</span></li>
                        <li>⚡ <span>Find top-rated products in seconds, customized just for you</span></li>
                        <li>🌐 <span>Explore a world of products with global coverage and recommendations</span></li>
                    </ul>

                </div>
                <div className="about-image">
                    <img src={AiImg}
                         alt="AI Technology"/>
                </div>
            </section>

            {/* Why Choose Us Section */}
            <section id="why-choose-us">
                <h2>Why Choose <span className="highlight">Products Scout</span>?</h2>
                <div className="reasons-container">
                    <div className="reason">
                        <img src="https://cdn-icons-png.flaticon.com/512/3596/3596148.png"
                             alt="Personalized Recommendations"/>
                        <h3>Personalized Recommendations</h3>
                        <p>Get suggestions specifically tailored to your preferences and needs with our advanced AI
                            algorithms.</p>
                    </div>
                    <div className="reason">
                        <img src="https://cdn-icons-png.flaticon.com/512/833/833314.png" alt="Real-Time Search"/>
                        <h3>Real-Time Product Matching</h3>
                        <p>Find the best products instantly, using real-time search powered by reliable platforms like
                            Amazon.</p>
                    </div>

                    <div className="reason">
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                             alt="User-Friendly Interface"/>
                        <h3>Effortless Experience</h3>
                        <p>Navigate through an intuitive, visually stunning interface that prioritizes your ease of
                            use.</p>
                    </div>

                    <div className="reason">
                        <img src="https://cdn-icons-png.flaticon.com/512/1161/1161776.png" alt="Reliable Support"/>
                        <h3>Dedicated Support</h3>
                        <p>Our support team is available 24/7 to provide assistance and ensure a seamless
                            experience.</p>
                    </div>
                </div>
            </section>


            {/* Footer */}
            <footer className="homepage-footer">
                <div className="footer-content">
                    <p>
                        © {new Date().getFullYear()} Products Scout |
                        <a href="/help" className="footer-link">Help</a> |
                        <a href="/privacy" className="footer-link">Privacy Policy</a>
                    </p>
                    <div className="social-links">
                        <a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer"
                           className="social-icon">
                            <img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" alt="Instagram" style={{ marginTop:'8px'}} className="insta-logo"/>
                        </a>
                        <a href="https://www.twitter.com" target="_blank" rel="noopener noreferrer"
                           className="social-icon">
                            <img src={Xlogo} alt="X (Twitter)" className="x-logo" style={{ height: '50px', width: '50px'}}/>
                        </a>
                    </div>
                </div>
            </footer>


        </div>
    );
};

export default HomePage;
