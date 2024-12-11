// ===========================================Done=========================================================

import React, { useState, useEffect } from "react";
import axios from "axios";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import "./ForgotPasswordPage.css";

const ForgotPasswordPage = () => {
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState("");
    const [isError, setIsError] = useState(false);
    const [verificationCode, setVerificationCode] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [step, setStep] = useState(1);
    const [canResend, setCanResend] = useState(false);
    const [timer, setTimer] = useState(0);
    const [showResendVerificationLink, setShowResendVerificationLink] = useState(false);
    const [passwordValid, setPasswordValid] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false); // State for toggling new password visibility
    const [showConfirmPassword, setShowConfirmPassword] = useState(false); // State for toggling confirm password visibility

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${API_BASE_URL}/api/forgot-password/`, { email });
            setMessage("Verification code sent to your email.");
            setIsError(false);
            setCanResend(false);
            setTimer(120);
            setShowResendVerificationLink(false);
            goToNextStep();
        } catch (error) {
            if (error.response?.data?.resend_verification) {
                setMessage("Your email is not verified.");
                setShowResendVerificationLink(true);
            } else {
                setMessage(error.response?.data?.error || "Error sending verification code.");
            }
            setIsError(true);
        }
    };

    const handleResendCode = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/api/forgot-password/`, { email });
            setMessage("Verification code resent to your email.");
            setIsError(false);
            setCanResend(false);
            setTimer(120);
        } catch (error) {
            setMessage(error.response?.data?.error || "Error resending verification code.");
            setIsError(true);
        }
    };

    const handleResendVerificationEmail = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/api/resend-verification-email/`, { email });
            setMessage("Verification email resent. Please check your inbox.");
            setIsError(false);
            setShowResendVerificationLink(false);
        } catch (error) {
            setMessage(error.response?.data?.error || "Error resending verification email.");
            setIsError(true);
        }
    };

    useEffect(() => {
        if (timer > 0) {
            const countdown = setInterval(() => setTimer((prev) => prev - 1), 1000);
            return () => clearInterval(countdown);
        } else {
            setCanResend(true);
        }
    }, [timer]);

    const handleCodeSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${API_BASE_URL}/api/verify-code/`, {
                email,
                verification_code: verificationCode,
            });
            setMessage("Verification successful. Please enter a new password.");
            setIsError(false);
            goToNextStep();
        } catch (error) {
            setMessage("Invalid verification code.");
            setIsError(true);
        }
    };

    const handlePasswordReset = async (e) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            setMessage("Passwords do not match.");
            setIsError(true);
            return;
        }
        if (!passwordValid) {
            setMessage("Password does not meet the strength requirements.");
            setIsError(true);
            return;
        }
        try {
            const response = await axios.post(`${API_BASE_URL}/api/reset-password/`, {
                email,
                new_password: newPassword,
            });
            setMessage("Password reset successful. You can now ");
            setIsError(false);
            goToNextStep();
        } catch (error) {
            setMessage("Error resetting password.");
            setIsError(true);
        }
    };

    const goToNextStep = () => {
        setStep((prevStep) => prevStep + 1);
    };

    const validatePassword = (password) => {
        const minLength = 8;
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        if (password.length >= minLength && hasUppercase && hasLowercase && hasNumber && hasSpecialChar) {
            setPasswordValid(true);
        } else {
            setPasswordValid(false);
        }
    };

    const handlePasswordChange = (e) => {
        const password = e.target.value;
        setNewPassword(password);
        validatePassword(password);
    };

    const handleGoBack = () => {
        setStep((prevStep) => prevStep - 1);
    };

    return (
        <div className="forgot-password-page">
            <img src="./logo.png" alt="Company Logo" className="company-logo"/>
            <h2>Forgot Password</h2>
            <div className={`step-1 ${step === 1 ? 'active' : ''}`}>
                {step === 1 && (
                    <form onSubmit={handleEmailSubmit} className="form-slide email-step">
                        <input
                            id="email-input"
                            type="email"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <button id="send-code-button" type="submit">Send Code</button>
                        {showResendVerificationLink && (
                            <p id="resend-verification-link">
                                Your email is not verified.{" "}
                                <a href="#" onClick={handleResendVerificationEmail}>
                                    Resend Verification Email
                                </a>
                            </p>
                        )}
                    </form>
                )}
            </div>
            <div className={`step-2 ${step === 2 ? 'active' : ''}`}>
                {step === 2 && (
                    <form onSubmit={handleCodeSubmit} className="form-slide code-step">
                        <input
                            id="verification-code-input"
                            type="text"
                            placeholder="Enter verification code"
                            value={verificationCode}
                            onChange={(e) => setVerificationCode(e.target.value)}
                            required
                        />
                        <button id="verify-code-button" type="submit">Verify Code</button>
                        {canResend ? (
                            <p id="resend-code-link">
                                Didn't receive the code?{" "}
                                <a href="#" onClick={handleResendCode}>
                                    Resend Code
                                </a>
                            </p>
                        ) : (
                            <p id="resend-timer">Resend available in {timer} seconds</p>
                        )}
                    </form>
                )}
            </div>
            <div className={`step-3 ${step === 3 ? 'active' : ''}`}>
                {step === 3 && (
                    <form onSubmit={handlePasswordReset} className="form-slide reset-step">
                        <div className="password-field">
                            <input
                                id="new-password-input"
                                type={showNewPassword ? "text" : "password"} // Toggle type
                                placeholder="New Password"
                                value={newPassword}
                                onChange={handlePasswordChange}
                                required
                            />
                            <span
                                className="toggle-password-visibility"
                                onClick={() => setShowNewPassword(!showNewPassword)}
                            >
                                {showNewPassword ? <FaEyeSlash/> : <FaEye/>}
                            </span>
                        </div>
                        <div className="password-field">
                            <input
                                id="confirm-password-input"
                                type={showConfirmPassword ? "text" : "password"} // Toggle type
                                placeholder="Confirm New Password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                            <span
                                className="toggle-password-visibility"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            >
                                {showConfirmPassword ? <FaEyeSlash/> : <FaEye/>}
                            </span>
                        </div>
                        <button id="reset-password-button" type="submit">Reset Password</button>
                        <p className="password-requirements">
                            Password must be at least 8 characters and include an uppercase letter, lowercase letter,
                            number, and special character.
                        </p>
                        {!passwordValid && newPassword.length > 0 && (
                            <p style={{color: "red"}}>Password does not meet the requirements.</p>
                        )}
                    </form>
                )}
            </div>
            <div className={`step-4 ${step === 4 ? 'active' : ''}`}>
                {step === 4 && (
                    <div className="form-slide success-step">
                        <p id="success-message" style={{color: "green"}}>Password reset successful. You can now </p>
                        <a id="login-link" href="/signin">Login</a>
                    </div>
                )}
            </div>
            {step > 1 && step < 4 && (
                    <a href="#" onClick={handleGoBack} className="go-back-link">
                        Go Back
                    </a>
                )}
            <p id="status-message" style={{color: isError ? "red" : "green"}}>{message}</p>
        </div>
    );
};

export default ForgotPasswordPage;
