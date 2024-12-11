// ===========================================Done=========================================================

import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Account.css";

const Account = () => {
    const [userDetails, setUserDetails] = useState({
        first_name: "",
        last_name: "",
        email: "",
    });
    const [loading, setLoading] = useState(true); // For fetching user details
    const [submitting, setSubmitting] = useState(false); // For form submission
    const [message, setMessage] = useState("");
    const [isError, setIsError] = useState(false);

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

    const getAuthHeaders = () => {
        const accessToken = localStorage.getItem("accessToken");
        return {
            Authorization: `Bearer ${accessToken}`,
        };
    };

    useEffect(() => {
        // Fetch user details on component mount
        axios
            .get(`${API_BASE_URL}/api/profile/`, {
                headers: getAuthHeaders(),
            })
            .then((response) => {
                setUserDetails(response.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching profile:", error);
                setMessage("Failed to fetch profile details. Please try again.");
                setIsError(true);
                setLoading(false);
            });
    }, [API_BASE_URL]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setUserDetails((prevDetails) => ({
            ...prevDetails,
            [name]: value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmitting(true);
        setMessage(""); // Clear any previous messages

        axios
            .put(
                `${API_BASE_URL}/api/profile-update/`,
                {
                    first_name: userDetails.first_name,
                    last_name: userDetails.last_name,
                },
                {
                    headers: {
                        ...getAuthHeaders(),
                        "Content-Type": "application/json",
                    },
                }
            )
            .then((response) => {
                setMessage(response.data.message || "Profile updated successfully!");
                setIsError(false);
            })
            .catch((error) => {
                console.error("Error updating profile:", error);
                setMessage(
                    error.response?.data?.error || "Failed to update profile. Please try again."
                );
                setIsError(true);
            })
            .finally(() => {
                setSubmitting(false);
            });
    };

    if (loading) {
        return (
            <div id="loading-container" className="loading">
                Loading account details...
            </div>
        );
    }

    return (
        <div id="account-page-container" className="account-page">
            <h2 id="account-title">Account Details</h2>
            <form id="account-form" onSubmit={handleSubmit}>
                <div className="form-group" id="first-name-group">
                    <label htmlFor="first_name">First Name</label>
                    <input
                        type="text"
                        id="first_name"
                        name="first_name"
                        className="input-field"
                        value={userDetails.first_name || ""}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group" id="last-name-group">
                    <label htmlFor="last_name">Last Name</label>
                    <input
                        type="text"
                        id="last_name"
                        name="last_name"
                        className="input-field"
                        value={userDetails.last_name || ""}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group" id="email-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        className="input-disabled"
                        value={userDetails.email || ""}
                        disabled
                    />
                </div>

                <button
                    type="submit"
                    id="terms-accept-button"
                    className="btn-primary"
                    disabled={submitting}
                >
                    {submitting ? "Updating..." : "Update Profile"}
                </button>
                <a href='./Dashboard' className="back-to-homepage-link">Back to dashboard</a>
            </form>

            {message && (
                <p
                    id="message-container"
                    className={`message ${isError ? "error" : "success"}`}
                >
                    {message}
                </p>
            )}
        </div>
    );
};

export default Account;
