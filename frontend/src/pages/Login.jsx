import React, {
  useState,
} from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  login,
  getErrorMessage,
} from "../services/api";

import {
  AUTH_KEY,
} from "../constants";

export default function Login() {
  const navigate =
    useNavigate();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSubmit(
    event
  ) {
    event.preventDefault();

    setError("");

    if (
      !email.trim() ||
      !password
    ) {
      setError(
        "Please enter your email and password."
      );

      return;
    }

    try {
      setLoading(true);

      const data =
        await login(
          email.trim(),
          password
        );

      const user =
        data?.user || data;

      if (!user?.id) {
        throw new Error(
          "Login succeeded but user information was not returned."
        );
      }

      localStorage.setItem(
        AUTH_KEY,
        JSON.stringify(user)
      );

      navigate(
        "/dashboard",
        { replace: true }
      );
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Login failed."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-decoration decoration-one" />
      <div className="auth-decoration decoration-two" />

      <div className="auth-layout">
        <section className="auth-hero">
          <div className="auth-logo">
            🌱
          </div>

          <p className="eyebrow">
            SMART AGRICULTURE AI
          </p>

          <h1>
            AI Driven Crop
            <span>
              Classification &
              Yield Prediction
            </span>
          </h1>

          <p className="auth-description">
            Analyze location-based
            environmental data, classify
            crops, estimate yield and
            receive crop-level fertilizer
            guidance from one platform.
          </p>

          <div className="hero-points">
            <div>
              <span>✓</span>
              Automatic location analysis
            </div>

            <div>
              <span>✓</span>
              Machine learning predictions
            </div>

            <div>
              <span>✓</span>
              Prediction history
            </div>
          </div>
        </section>

        <section className="auth-card">
          <div className="auth-card-header">
            <p className="eyebrow">
              WELCOME BACK
            </p>

            <h2>
              Sign in
            </h2>

            <p>
              Continue to your agriculture
              intelligence dashboard.
            </p>
          </div>

          {error && (
            <div className="error-box">
              {error}
            </div>
          )}

          <form
            onSubmit={
              handleSubmit
            }
            className="auth-form"
          >
            <label>
              Email

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(
                    event.target.value
                  )
                }
                placeholder="you@example.com"
              />
            </label>

            <label>
              Password

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value
                  )
                }
                placeholder="Enter your password"
              />
            </label>

            <button
              className="primary-button"
              disabled={loading}
              type="submit"
            >
              {loading
                ? "Signing in..."
                : "Sign in"}
            </button>
          </form>

          <div className="auth-footer">
            Don't have an account?

            <Link to="/signup">
              Create account
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}