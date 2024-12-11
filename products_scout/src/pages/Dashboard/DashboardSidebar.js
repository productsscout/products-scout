// ===========================================Done=========================================================

import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CartIcon from "../assets/cart.png";
import NewChatIcon from "../assets/new-chat.png";
import ProfileIcon from "../assets/logo.png";
import InfoIcon from "../assets/info.png";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";
import "./DashboardSidebar.css";

const DashboardSidebar = ({ handleLogout, isSidebarVisible, setIsSidebarVisible }) => {
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const [showInfo, setShowInfo] = useState(false);
    const profileMenuRef = useRef(null);
    const sidebarRef = useRef(null);

    const navigate = useNavigate();

    // Close the profile menu when clicking outside of it
    useEffect(() => {
         // Hide the sidebar by default on page load
        setIsSidebarVisible(false);
        const handleOutsideClick = (event) => {
            if (
                profileMenuRef.current &&
                !profileMenuRef.current.contains(event.target) &&
                sidebarRef.current &&
                !sidebarRef.current.contains(event.target)
            ) {
                setShowProfileMenu(false);
            }
        };

        document.addEventListener("mousedown", handleOutsideClick);
        return () => {
            document.removeEventListener("mousedown", handleOutsideClick);
        };
    }, []);


    return (
        <div
            style={{display: "flex", position: "relative"}}
            onMouseEnter={() => setIsSidebarVisible(true)} // Show sidebar on hover
            onMouseLeave={() => setIsSidebarVisible(false)} // Hide sidebar when cursor moves out
        >
            {/* Sidebar */}
            <div className={`sidebar ${isSidebarVisible ? "visible" : "hidden"}`}>
                {/* Profile Menu */}
                {showProfileMenu && (
                    <div className="profile-menu" ref={profileMenuRef}>
                        <button
                            className="profile-option"
                            onClick={() => {
                                setShowProfileMenu(false);
                                navigate("/account");
                            }}
                        >
                            Account
                        </button>
                        <button className="profile-option" onClick={handleLogout}>
                            Logout
                        </button>
                    </div>
                )}

                {/* Sidebar Content */}
                <div className="sidebar-header">
                    <div className="icon-row">
                        <div
                            className="icon clickable cart-icon"
                            onClick={() => navigate("/cart")}
                        >
                            <img src={CartIcon} alt="Cart" className="sidebar-icon"/>
                            <div className="tooltip">Cart</div>
                        </div>
                        <div
                            className="icon clickable new-chat-icon"
                            onClick={() => {
                                // Replace page refresh with a smoother state reset if required
                                window.location.reload();
                            }}
                        >
                            <img src={NewChatIcon} alt="New Chat" className="sidebar-icon"/>
                            <div className="tooltip">New Chat</div>
                        </div>
                    </div>
                </div>
                <div className="sidebar-body">
                    <h3>
                        History
                        <img
                            src={InfoIcon}
                            alt="Info"
                            className="info-icon"
                            onMouseEnter={() => setShowInfo(true)}
                            onMouseLeave={() => setShowInfo(false)}
                        />
                        {showInfo && (
                            <div className="info-tooltip">
                                Currently we are not storing your history.
                            </div>
                        )}
                    </h3>
                    <p className="history-notification">Currently Unavailable...</p>
                </div>
                <div className="sidebar-footer">
                    <div
                        className="icon clickable"
                        onClick={() => setShowProfileMenu(!showProfileMenu)}
                    >
                        <img src={ProfileIcon} alt="Profile" className="profile-icon"/>
                        <div className="tooltip">Profile</div>
                    </div>
                </div>
            </div>

            {/* Sidebar Toggle Button */}
            <button
                className="sidebar-toggle"
                onClick={() => setIsSidebarVisible(!isSidebarVisible)}
                style={{
                    position: "absolute",
                    top: "50%",
                    left: isSidebarVisible ? "250px" : "10px",
                    transform: "translateY(-50%)",
                    zIndex: 10,
                }}
            >
                {isSidebarVisible ? <FaChevronLeft/> : <FaChevronRight/>}
            </button>
        </div>
    );
};

export default DashboardSidebar;
