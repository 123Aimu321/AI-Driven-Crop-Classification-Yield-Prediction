import React from "react";
import {
  NavLink,
  useNavigate,
} from "react-router-dom";

import {
  AUTH_KEY,
  CROP_KEY,
  LOCATION_KEY,
  getStoredUser,
} from "../constants";

export default function Header() {
  const navigate =
    useNavigate();

  const user =
    getStoredUser();

  function logout() {
    localStorage.removeItem(
      AUTH_KEY
    );

    localStorage.removeItem(
      LOCATION_KEY
    );

    localStorage.removeItem(
      CROP_KEY
    );

    navigate(
      "/login",
      { replace: true }
    );
  }

  const navClass = ({
    isActive,
  }) =>
    isActive
      ? "nav-link active"
      : "nav-link";

  return (
    <header className="app-header">
      <div className="header-inner">
        <NavLink
          to="/dashboard"
          className="brand"
        >
          <div className="brand-mark">
            🌱
          </div>

          <div>
            <div className="brand-title">
              AI Crop Intelligence
            </div>

            <div className="brand-subtitle">
              Smart agriculture platform
            </div>
          </div>
        </NavLink>

        <nav className="main-nav">
          <NavLink
            to="/dashboard"
            className={navClass}
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/crop-prediction"
            className={navClass}
          >
            Crop
          </NavLink>

          <NavLink
            to="/yield-prediction"
            className={navClass}
          >
            Yield
          </NavLink>

          <NavLink
            to="/fertilizer"
            className={navClass}
          >
            Fertilizer
          </NavLink>

          <NavLink
            to="/history"
            className={navClass}
          >
            History
          </NavLink>
        </nav>

        <div className="header-user">
          <div className="user-avatar">
            {user?.name
              ?.charAt(0)
              ?.toUpperCase() || "U"}
          </div>

          <span>
            {user?.name ||
              "User"}
          </span>

          <button
            className="logout-button"
            onClick={logout}
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}