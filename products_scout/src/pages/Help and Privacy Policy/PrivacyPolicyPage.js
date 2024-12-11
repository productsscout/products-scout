// ===========================================Done=========================================================

import React from "react";
import "./PrivacyPolicyPage.css";

const PrivacyPolicyPage = () => {
    const CONTACT_EMAIL = process.env.REACT_APP_CONTACT_EMAIL || "contact-us@productsscout.com";
    const PRIVACY_EMAIL = process.env.REACT_APP_PRIVACY_EMAIL || "privacy@productsscout.com";
    const LAST_UPDATED = "December 2024"; // Replace with dynamic logic if needed

    return (
        <div className="privacy-policy-page">
            <h1>Privacy Policy</h1>
            <p>
                At <span className="highlight">Products Scout</span>, your privacy is our top priority. This Privacy Policy outlines how we collect, use, and protect your information. By using our services, you agree to the terms outlined below.
            </p>

            <h2>1. Information We Collect</h2>
            <p>We collect the following types of information to enhance your experience and provide you with tailored product recommendations:</p>
            <ul className="policy-list">
                <li><strong>Personal Information:</strong> This includes your name, email address, and other details provided during registration or login.</li>
                <li><strong>Browsing Data:</strong> Information such as your search history, interaction with our platform, and usage patterns.</li>
                <li><strong>Device Information:</strong> Details about the device you use to access our platform, including browser type, IP address, and operating system.</li>
                <li><strong>Cookies:</strong> Small files stored on your device to enhance your browsing experience. See our "Cookies Policy" below for more information.</li>
            </ul>

            <h2>2. How We Use Your Information</h2>
            <p>We use your information to:</p>
            <ul className="policy-list">
                <li>Provide personalized product recommendations based on your preferences and search history.</li>
                <li>Enhance the functionality and usability of our platform.</li>
                <li>Communicate with you regarding updates, promotions, and customer support inquiries.</li>
                <li>Analyze platform performance to improve our services.</li>
                <li>Ensure compliance with legal obligations and prevent fraudulent activities.</li>
            </ul>

            <h2>3. Sharing Your Information</h2>
            <p>We do not sell or rent your personal information to third parties. However, we may share your data with:</p>
            <ul className="policy-list">
                <li><strong>Service Providers:</strong> Trusted third parties that help us operate our platform, such as payment processors and analytics tools.</li>
                <li><strong>Legal Authorities:</strong> When required by law or in response to valid legal requests.</li>
                <li><strong>Business Transfers:</strong> In case of a merger, acquisition, or sale of our assets, your data may be transferred as part of the transaction.</li>
            </ul>

            <h2>4. How We Protect Your Information</h2>
            <p>We implement robust security measures to safeguard your data, including:</p>
            <ul className="policy-list">
                <li>Encryption of sensitive information during transmission.</li>
                <li>Regular security audits and vulnerability assessments.</li>
                <li>Access controls to restrict unauthorized access to your data.</li>
            </ul>
            <p>While we take every precaution to protect your information, please note that no method of transmission over the internet is 100% secure.</p>

            <h2>5. Cookies Policy</h2>
            <p>Cookies are essential for the proper functioning of our website. They help us:</p>
            <ul className="policy-list">
                <li>Remember your preferences and settings.</li>
                <li>Analyze usage patterns to improve performance.</li>
                <li>Deliver personalized content and advertisements.</li>
            </ul>
            <p>You can manage your cookie preferences through your browser settings. Please note that disabling cookies may affect your user experience.</p>

            <h2>6. Your Privacy Rights</h2>
            <p>You have the right to:</p>
            <ul className="policy-list">
                <li>Access the personal data we hold about you.</li>
                <li>Request corrections or updates to your personal information.</li>
                <li>Delete your account and associated data (subject to certain legal and contractual obligations).</li>
                <li>Opt-out of receiving promotional communications.</li>
            </ul>
            <p>
                To exercise your rights, please contact us at <a href={`mailto:${CONTACT_EMAIL}`} className="email-link" aria-label="Contact email">{CONTACT_EMAIL}</a>.
            </p>

            <h2>7. Children's Privacy</h2>
            <p>Products Scout is not intended for children under the age of 13. We do not knowingly collect personal information from children. If you believe we have inadvertently collected data from a child, please contact us immediately.</p>

            <h2>8. Changes to This Privacy Policy</h2>
            <p>
                We may update this Privacy Policy from time to time to reflect changes in our practices or for other operational, legal, or regulatory reasons. Any updates will be posted on this page with the "Last Updated" date at the top.
            </p>
            <p><strong>Last Updated:</strong> {LAST_UPDATED}</p>

            <h2>9. Contact Us</h2>
            <p>If you have any questions or concerns about this Privacy Policy, please reach out to us:</p>
            <ul className="contact-list">
                <li>
                    Email: <a href={`mailto:${PRIVACY_EMAIL}`} className="email-link" aria-label="Privacy email">{PRIVACY_EMAIL}</a>
                </li>
                <li>Address: Dehradun, Uttarakhand (INDIA)</li>
            </ul>
        </div>
    );
};

export default PrivacyPolicyPage;
