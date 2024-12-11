// ===========================================Done=========================================================

import React, { useState } from "react";
import axios from "axios";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import "./RegistrationPage.css";

const RegistrationPage = () => {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        confirmPassword: "",
        firstName: "",
        lastName: "",
        dateOfBirth: "",
        termsAccepted: false, // NEW: Add this to the form state
    });
    const [message, setMessage] = useState("");
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [showTermsModal, setShowTermsModal] = useState(false); // NEW: State for Terms & Conditions modal

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    const validatePassword = (password) =>
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);
    const validateDate = (date) => {
        const dateRegex = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
        if (!dateRegex.test(date)) return false;
        const [year, month, day] = date.split("-");
        const parsedDate = new Date(year, month - 1, day); // Months are 0-indexed
        return (
            parsedDate.getFullYear() === parseInt(year, 10) &&
            parsedDate.getMonth() === parseInt(month, 10) - 1 &&
            parsedDate.getDate() === parseInt(day, 10)
        );
    };

    const handleSubmitEmail = async (e) => {
        e.preventDefault();
        if (!validateEmail(formData.email)) {
            setMessage("Please enter a valid email address.");
            setIsError(true);
            return;
        }

        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/check-email/`, { email: formData.email });
            setMessage("Email is valid. Complete the next step.");
            setIsError(false);
            setStep(2);
        } catch (error) {
            setMessage("This email is already registered.");
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitPassword = (e) => {
        e.preventDefault();
        if (!validatePassword(formData.password)) {
            setMessage("Password must be at least 8 characters, including uppercase, lowercase, number, and special character.");
            setIsError(true);
            return;
        }
        if (formData.password !== formData.confirmPassword) {
            setMessage("Passwords do not match.");
            setIsError(true);
            return;
        }
        setMessage("");
        setIsError(false);
        setStep(3);
    };

    const handleSubmitDetails = async (e) => {
        e.preventDefault();
        if (!formData.firstName) {
            setMessage("First name is required.");
            setIsError(true);
            return;
        }
        if (!validateDate(formData.dateOfBirth)) {
            setMessage("Date of Birth must be in the format YYYY-MM-DD and must be valid.");
            setIsError(true);
            return;
        }

        if (!formData.termsAccepted) { // NEW: Check if terms are accepted
            setMessage("You must accept the terms and conditions.");
            setIsError(true);
            return;
        }

        setLoading(true);
        try {
            const payload = {
                first_name: formData.firstName,
                last_name: formData.lastName,
                email: formData.email,
                date_of_birth: formData.dateOfBirth,
                password: formData.password,
                terms_accepted: formData.termsAccepted, // NEW: Include termsAccepted in the payload
            };
            await axios.post(`${API_BASE_URL}/api/register/`, payload);
            setMessage("Registration successful! Check your email to verify your account.");
            setIsError(false);
            setStep(4);
        } catch (error) {
            setMessage(
                error.response?.data?.error || "Please enter valid details."
            );
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    const handleTermsClick = () => {
        setShowTermsModal(true); // NEW: Show Terms & Conditions modal
    };

    const handleCloseTermsModal = () => {
        setShowTermsModal(false);
        setFormData({ ...formData, termsAccepted: true }); // NEW: Check the checkbox after closing modal
    };

    const handleGoBack = () => {
        setStep((prevStep) => prevStep - 1);
    };

    return (
        <div className="registration-page">
            <img src="./logo.png" alt="Company Logo" className="company-logo" />
            <h2>Create an Account</h2>
            <div className="form-container">
                {step === 1 && (
                    <form onSubmit={handleSubmitEmail}>
                        <div className="form-group">
                            <div className="email-container">
                                <input
                                    id="email-input"
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder=" "
                                    required
                                />
                                <span className="email-label">Email address *</span>
                            </div>
                        </div>
                        <button id="email-submit-btn" className='submit-btn' type="submit" disabled={loading}>
                            {loading ? "Checking..." : "Continue"}
                        </button>
                        <p className="login-link">
                            Already have an account? <a href="/signin">Log in</a>
                        </p>
                        <a href='/' className="go-back-link">Back to HomePage </a>
                    </form>
                )}

                {step === 2 && (
                    <form onSubmit={handleSubmitPassword}>
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
                        <div className="form-group-password">
                            <div className="password-container">
                                <input
                                    id="confirm-password-input"
                                    type={showConfirmPassword ? "text" : "password"}
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    placeholder=" "
                                    required
                                />
                                <span className="password-label">Confirm Password *</span>
                                <span
                                    className="toggle-password"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                >
                                {showConfirmPassword ? <FaEyeSlash/> : <FaEye/>}
                            </span>
                            </div>
                        </div>

                            <button id="password-submit-btn" className='submit-btn' type="submit" disabled={loading}
                                    style={{marginBottom: "20px"}}>
                                {loading ? "Validating..." : "Continue"}
                            </button>
                    </form>
                    )}

                {step === 3 && (
                    <form onSubmit={handleSubmitDetails}>
                        <div className="form-group">
                            <input
                                id="first-name-input"
                                type="text"
                                name="firstName"
                                value={formData.firstName}
                                onChange={handleChange}
                                placeholder=" "
                                required
                            />
                            <span className="details-field">First Name *</span>
                        </div>
                        <div className="form-group">
                            <input
                                id="last-name-input"
                                type="text"
                                name="lastName"
                                value={formData.lastName}
                                onChange={handleChange}
                                placeholder=" "
                                required
                            />
                            <span className="details-field">Last Name *</span>
                        </div>
                        <div className="form-group">
                            <input
                                id="dob-input"
                                type="date"
                                name="dateOfBirth"
                                value={formData.dateOfBirth}
                                onChange={handleChange}
                                placeholder=" "
                                required
                            />
                            <span className="details-field">Date of Birth *</span>
                        </div>

                        {/* NEW: Terms & Conditions Checkbox */}
                        <div className="form-group terms-conditions">
                            <input
                                type="checkbox"
                                id="terms-checkbox"
                                name="termsAccepted"
                                checked={formData.termsAccepted}
                                onChange={(e) => setFormData({...formData, termsAccepted: e.target.checked})}
                                disabled={!formData.termsAccepted} // Disabled until the modal is closed
                            />
                            <label htmlFor="terms-checkbox">
                                I accept{" "}
                                <a
                                    href="#"
                                    className="terms-link"
                                    onClick={handleTermsClick}
                                >
                                    Terms & Conditions
                                </a>
                            </label>
                        </div>
                        <button id="details-submit-btn" className="submit-btn" type="submit" disabled={loading}>
                            {loading ? "Submitting..." : "Continue"}
                        </button>
                    </form>
                )}

                {step > 1 && step < 4 && (
                    <a href="#" onClick={handleGoBack} className="go-back-link">
                        Go Back
                    </a>
                )}

                <p id="status-message" style={{color: isError ? "red" : "green"}}>{message}</p>
            </div>

            {/* NEW: Terms & Conditions Modal */}
            {showTermsModal && (
                <div className="terms-modal" id="terms-modal">
                    <div className="terms-modal-content" id="terms-modal-content">
                        <h3 id="terms-title">Terms & Conditions</h3>
                        <div className="terms-content" id="terms-content">
                            <h4 id="terms-intro-title">1. Introduction</h4>
                            <p id="terms-intro-text">
                                Welcome to Products Scout! By using our services, you agree to comply with and be bound
                                by these Terms & Conditions. Please read these terms carefully. If you do not agree to
                                any part of these terms, you must not use our services.
                            </p>

                            <h4 id="terms-services-title">2. Services Provided</h4>
                            <p id="terms-services-text">
                                Products Scout is an AI-driven platform designed to provide product recommendations
                                based on user input. We use APIs, including third-party APIs such as Amazon, and
                                artificial intelligence tools to suggest products that match your preferences.
                            </p>

                            <h4 id="terms-accounts-title">3. User Accounts</h4>
                            <ul id="terms-accounts-list">
                                <li id="terms-accounts-registration">
                                    <strong>Registration:</strong> To access certain features, users must register by
                                    providing accurate and complete information, including a valid email address.
                                </li>
                                <li id="terms-accounts-responsibility">
                                    <strong>Account Responsibility:</strong> Users are responsible for maintaining the
                                    confidentiality of their account credentials. Products Scout is not liable for any
                                    unauthorized access due to user negligence.
                                </li>
                                <li id="terms-accounts-social">
                                    <strong>Social Login:</strong> Users may access our platform using social login
                                    methods (e.g., Google, Microsoft). By doing so, you agree to share your basic
                                    profile information with us.
                                </li>
                            </ul>

                            <h4 id="terms-platform-title">4. Use of the Platform</h4>
                            <ul id="terms-platform-list">
                                <li id="terms-platform-permitted">
                                    <strong>Permitted Use:</strong> Users may use the platform solely for personal,
                                    non-commercial purposes to obtain product recommendations.
                                </li>
                                <li id="terms-platform-prohibited">
                                    <strong>Prohibited Use:</strong>
                                    <ul id="terms-platform-prohibited-list">
                                        <li id="terms-platform-scraping">Scraping, data mining, or automated queries.
                                        </li>
                                        <li id="terms-platform-malicious">Uploading malicious software or engaging in
                                            activities that compromise the platform's integrity.
                                        </li>
                                        <li id="terms-platform-sharing">Sharing or disseminating proprietary algorithms,
                                            APIs, or other intellectual property.
                                        </li>
                                    </ul>
                                </li>
                            </ul>

                            <h4 id="terms-ai-title">5. AI Recommendations</h4>
                            <p id="terms-ai-text">
                                While our AI engine strives to provide accurate recommendations, Products Scout does not
                                guarantee that the recommended products will fully meet your needs or expectations.
                                Recommendations include third-party products (e.g., Amazon). We do not own, sell, or
                                guarantee the quality, availability, or accuracy of these products or their
                                descriptions.
                            </p>

                            <h4 id="terms-privacy-title">6. Privacy Policy</h4>
                            <p id="terms-privacy-text">
                                Our use of personal data is governed by our Privacy Policy. By using Products Scout, you
                                consent to the collection, use, and sharing of your data as described in our Privacy
                                Policy.
                            </p>

                            <h4 id="terms-third-party-title">7. Third-Party APIs</h4>
                            <p id="terms-third-party-text">
                                Products Scout integrates third-party APIs, including Amazon's API and OpenAI tools. We
                                are not responsible for the availability, accuracy, or reliability of third-party
                                services. Users agree to comply with the terms of these third-party providers.
                            </p>

                            <h4 id="terms-ip-title">8. Intellectual Property</h4>
                            <p id="terms-ip-text">
                                All platform content, including logos, code, and AI models, is owned by Products Scout
                                or its licensors. Users may not replicate, distribute, or reverse-engineer any part of
                                the platform without prior written consent.
                            </p>

                            <h4 id="terms-liability-title">9. Liability Disclaimer</h4>
                            <p id="terms-liability-text">
                                Products Scout is provided "as is" without warranties of any kind. We do not guarantee
                                uninterrupted or error-free services. Products Scout is not liable for indirect,
                                incidental, or consequential damages or losses resulting from reliance on AI
                                recommendations or third-party products.
                            </p>

                            <h4 id="terms-termination-title">10. Termination</h4>
                            <p id="terms-termination-text">
                                Products Scout reserves the right to suspend or terminate user accounts at its
                                discretion, including but not limited to violations of these terms. Users may terminate
                                their account by contacting support.
                            </p>

                            <h4 id="terms-contact-title">11. Contact Us</h4>
                            <p id="terms-contact-text">
                                For questions or concerns regarding these Terms & Conditions, contact us at:
                            </p>
                            <ul id="terms-contact-list">
                                <li id="terms-contact-email">Email: <a href="mailto:reachout@productsscout.com"
                                              className="help-link">reachout@productsscout.com</a></li>
                                <li id="terms-contact-address">Address: Dehradun, Uttarakhand, INDIA</li>
                            </ul>
                        </div>
                        <button id="terms-accept-button" onClick={handleCloseTermsModal}>Accept</button>
                    </div>
                </div>

            )}


            {/* Temporarily hide social login */}
            {/*
            <div className="social-login">
                <button
                    id="google-login-btn"
                    onClick={() => window.location.href = `${API_BASE_URL}/accounts/google/login/`}
                >
                    <img src="./google-logo.svg" alt="Google Logo" className="google-img" />
                    Continue with Google
                </button>
                <button
                    id="microsoft-login-btn"
                    onClick={() => window.location.href = `${API_BASE_URL}/accounts/microsoft/login/`}
                >
                    <img src="./microsoft-logo.svg" alt="Microsoft Logo" />
                    Continue with Microsoft
                </button>
            </div>
            */}
        </div>
    );
};

export default RegistrationPage;
