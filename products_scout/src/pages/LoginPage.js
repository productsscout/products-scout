// ===========================================Done=========================================================

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import ReCAPTCHA from "react-google-recaptcha";
import "./LoginPage.css";

const LoginPage = () => {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [message, setMessage] = useState("");
    const [isError, setIsError] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [captchaToken, setCaptchaToken] = useState(null);
    const [showResendVerificationLink, setShowResendVerificationLink] = useState(false);

    const navigate = useNavigate();

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;


    // Redirect to CAPTCHA verification after social login
    useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const stepParam = params.get("step");
    const emailParam = params.get("email");

    if (stepParam === "3") {
        setStep(3); // Redirect to CAPTCHA verification step
        if (emailParam) {
            setFormData((prev) => ({ ...prev, email: emailParam })); // Prefill email if available
        } else {
            setMessage("Email is missing. Please log in again.");
            setIsError(true);
        }
    }
}, []);


    const handleCaptchaChange = (token) => {
        setCaptchaToken(token);
    };

    useEffect(() => {
        const accessToken = localStorage.getItem("accessToken");
        const accessTokenExpiry = localStorage.getItem("accessTokenExpiry");

        if (accessToken && accessTokenExpiry) {
            const currentTime = new Date().getTime();

            if (currentTime > accessTokenExpiry) {
                // Token expired
                localStorage.clear();
                navigate("/signin");
            }
        }
    }, [navigate]);


    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };


    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage("");
        setIsError(false);

        try {
            const response = await axios.post(
                `${API_BASE_URL}/api/check-user/`,
                { email: formData.email },
                { headers: { "Content-Type": "application/json" } }
            );

            if (response.data.exists) {
                if (response.data.is_active) {
                    setStep(2); // Proceed to the next step
                    setMessage("");
                    setIsError(false);
                } else {
                    // User exists but is not active
                    setMessage("This email is registered but not verified. Please verify your email.");
                    setShowResendVerificationLink(true); // Show the resend link
                    setIsError(true);
                }
            } else {
                // User does not exist
                setMessage("This email is not registered. Please sign up.");
                setIsError(true);
            }
        } catch (error) {
            setMessage(
                error.response?.data?.error || "No user found with this email. Please sign up."
            );
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    const handleResendVerificationEmail = async () => {
        setLoading(true);
        setMessage("");
        setIsError(false);

        try {
            await axios.post(`${API_BASE_URL}/api/resend-verification-email/`, {
                email: formData.email,
            });
            setMessage("Verification email resent. Please check your inbox.");
            setShowResendVerificationLink(false); // Hide the link after resending
            setIsError(false);
        } catch (error) {
            setMessage(error.response?.data?.error || "Error resending verification email.");
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage("");
        setIsError(false);

        try {
            const response = await axios.post(
                `${API_BASE_URL}/api/check-password/`,
                { email: formData.email, password: formData.password },
                { headers: { "Content-Type": "application/json" } }
            );

            if (response.data.valid) {
                setStep(3); // Proceed to CAPTCHA step if the password is valid
                setMessage("");
                setIsError(false);
            } else {
                setMessage("Invalid password. Please try again.");
                setIsError(true);
            }
        } catch (error) {
            setMessage(
                error.response?.data?.error || "Error validating password. Please try again."
            );
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    const handleCaptchaSubmit = async (e) => {
    e.preventDefault();
    if (!captchaToken) {
        setMessage("Please complete the CAPTCHA.");
        setIsError(true);
        return;
    }

    if (!formData.email) {
        setMessage("Email is missing. Please log in again.");
        setIsError(true);
        return;
    }

    setLoading(true);
    setMessage("");
    setIsError(false);

    try {
        const response = await axios.post(
            `${API_BASE_URL}/api/generate-tokens/`,
            { email: formData.email },
            { headers: { "Content-Type": "application/json" } }
        );

        const { access_token, refresh_token, expires_in, user } = response.data;

        // Store tokens and user details securely
        const expiryDate = new Date().getTime() + expires_in * 1000;
        localStorage.setItem("accessToken", access_token);
        localStorage.setItem("refreshToken", refresh_token);
        localStorage.setItem("accessTokenExpiry", expiryDate);
        localStorage.setItem("user", JSON.stringify(user));

        setMessage("Login successful!");
        setIsError(false);

        // Redirect to the dashboard
        navigate("/dashboard");
    } catch (error) {
        setMessage(
            error.response?.data?.error || "CAPTCHA verification failed. Please try again."
        );
        setIsError(true);
    } finally {
        setLoading(false);
    }
};


// Handle tokens when redirected back to React
useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");
    const expiresIn = params.get("expires_in");

    if (accessToken && refreshToken && expiresIn) {
        localStorage.setItem("accessToken", accessToken);
        localStorage.setItem("refreshToken", refreshToken);
        const expiryDate = new Date().getTime() + parseInt(expiresIn) * 1000;
        localStorage.setItem("accessTokenExpiry", expiryDate);

        // Redirect to the dashboard
        navigate("/dashboard");
    } else {
        console.error("Social login failed. Tokens are missing.");
        // setMessage("Social login failed. Please try again.");
        setIsError(true);
    }
}, [navigate]);

    // const handleSocialLogin = (provider) => {
    // const socialLoginUrl = `http://127.0.0.1:8000/accounts/${provider}/login/`; // Can be moved to a config file
    // window.location.href = socialLoginUrl;
    // };


    // Validate token expiry
    const storeTokens = (accessToken, refreshToken, expiresIn) => {
    const expiryDate = new Date().getTime() + parseInt(expiresIn) * 1000;
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
    localStorage.setItem("accessTokenExpiry", expiryDate);
};

const validateTokenExpiry = () => {
    const accessToken = localStorage.getItem("accessToken");
    const accessTokenExpiry = localStorage.getItem("accessTokenExpiry");

    if (accessToken && accessTokenExpiry) {
        const currentTime = new Date().getTime();
        if (currentTime > accessTokenExpiry) {
            localStorage.clear();
            alert("Your session has expired. Please log in again.");
            navigate("/signin");
        }
    } else {
        localStorage.clear();
        navigate("/signin");
    }
};

useEffect(() => {
    validateTokenExpiry();
}, [navigate]);





    const handleGoBack = () => {
        setStep((prevStep) => prevStep - 1);
    };

    return (
        <div className="login-page">
            <img src="./logo.png" alt="Company Logo" className="company-logo"/>
            <h2>Welcome Back</h2>
            <div className="form-container">
                {step === 1 && (
                    <form onSubmit={handleEmailSubmit}>
                        <div className="form-group">
                            <input
                                id="email-input"
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder=" "
                                required
                            />
                            <span>Email address *</span>
                            {showResendVerificationLink && (
                                <p id="resend-verification-link">
                                    Your email is not verified.{" "}
                                    <a href="#" onClick={handleResendVerificationEmail}>
                                        Resend Verification Email
                                    </a>
                                </p>
                            )}
                        </div>
                        <button
                            id="email-submit-btn"
                            className="submit-btn"
                            type="submit"
                            disabled={loading}
                        >
                            {loading ? "Validating..." : "Continue"}
                        </button>
                        <p
                            id="status-message"
                            style={{color: isError ? "red" : "green"}}
                        >
                            {message}
                        </p>
                        <p className="login-link">
                            Don't have an account? <a href="/signup">Sign Up</a>
                        </p>
                        <a href='/' className="go-back-link">Back to HomePage </a>
                    </form>
                )}

                {step === 2 && (
                    <form onSubmit={handlePasswordSubmit}>
                        <div className="form-group">
                            <input
                                id="email-display"
                                type="email"
                                name="email"
                                value={formData.email}
                                readOnly
                                placeholder=" "
                            />
                            <span>Email address *</span>
                        </div>
                        <div className="form-group-password">
                            <div className="password-container">
                                <input
                                    id="password-input"
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder=" "
                                    required
                                />
                                <span className="password-label">Password *</span>
                                <span
                                    className="toggle-password"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                {showPassword ? <FaEyeSlash/> : <FaEye/>}
                            </span>
                            </div>
                        </div>
                        <button
                            id="password-submit-btn"
                            className="submit-btn"
                            type="submit"
                            disabled={loading}
                        >
                            {loading ? "Validating..." : "Continue"}
                        </button>
                        <p
                            id="status-message"
                            style={{color: isError ? "red" : "green"}}
                        >
                            {message}
                        </p>
                        <p className="forgot-password-link">
                            <a href="/forgot-password">Forgot Password?</a>
                        </p>
                    </form>
                )}

                {step === 3 && (
                    <form onSubmit={handleCaptchaSubmit}>
                        <ReCAPTCHA
                            sitekey="6Le47pYqAAAAAKRcrIISes3pFYSv7WuussAU6Q0E"
                            onChange={handleCaptchaChange}
                        />
                        <button
                            id="captcha-submit-btn"
                            className="submit-btn"
                            type="submit"
                            disabled={loading}
                        >
                            {loading ? "Logging in..." : "Login"}
                        </button>
                        <p
                            id="status-message"
                            style={{color: isError ? "red" : "green"}}
                        >
                            {message}
                        </p>
                    </form>
                )}
            </div>
            {step > 1 && step < 4 && (
                <a href="#" onClick={handleGoBack} className="go-back-link">
                    Go Back
                </a>
            )}
            {/* Temporarily hide social login */}
            {/*
            <div className="social-login">
                <button
                    id="google-login-btn"
                    onClick={() => handleSocialLogin("google")}
                >
                    <img src="./google-logo.svg" alt="Google Logo" className="google-img"/>
                    Continue with Google
                </button>
                <button
                    id="microsoft-login-btn"
                    onClick={() => handleSocialLogin("microsoft")}
                >
                    <img src="./microsoft-logo.svg" alt="Microsoft Logo"/>
                    Continue with Microsoft
                </button>
            </div>
            */}
        </div>
    );
};

export default LoginPage;
