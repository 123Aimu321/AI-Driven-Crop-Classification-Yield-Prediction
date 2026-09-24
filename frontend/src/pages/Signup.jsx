import React, {
  useState,
} from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  signup,
  getErrorMessage,
} from "../services/api";

export default function Signup() {
  const navigate =
    useNavigate();

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  async function handleSubmit(
    event
  ) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (
      !name.trim() ||
      !email.trim() ||
      !password
    ) {
      setError(
        "Please fill in all fields."
      );

      return;
    }

    if (password.length < 6) {
      setError(
        "Password should contain at least 6 characters."
      );

      return;
    }

    try {
      setLoading(true);

      await signup(
        name.trim(),
        email.trim(),
        password
      );

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Could not create the account."
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
            🌾
          </div>

          <p className="eyebrow">
            AI AGRICULTURE PLATFORM
          </p>

          <h1>
            Smarter decisions
            <span>
              for every field.
            </span>
          </h1>

          <p className="auth-description">
            Create your account and start
            analyzing crops, environmental
            conditions, predicted yield and
            fertilizer guidance.
          </p>
        </section>

        <section className="auth-card">
          <div className="auth-card-header">
            <p className="eyebrow">
              GET STARTED
            </p>

            <h2>
              Create account
            </h2>

            <p>
              Set up your personal
              agriculture dashboard.
            </p>
          </div>

          {error && (
            <div className="error-box">
              {error}
            </div>
          )}

          {success && (
            <div className="success-box">
              {success}
            </div>
          )}

          <form
            onSubmit={
              handleSubmit
            }
            className="auth-form"
          >
            <label>
              Full name

              <input
                type="text"
                value={name}
                onChange={(event) =>
                  setName(
                    event.target.value
                  )
                }
                placeholder="Your name"
              />
            </label>

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
                placeholder="Minimum 6 characters"
              />
            </label>

            <button
              className="primary-button"
              disabled={loading}
              type="submit"
            >
              {loading
                ? "Creating account..."
                : "Create account"}
            </button>
          </form>

          <div className="auth-footer">
            Already have an account?

            <Link to="/login">
              Sign in
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}