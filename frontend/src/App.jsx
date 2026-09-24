import React from "react";

import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import {
  getStoredUser,
} from "./constants";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import CropPrediction from "./pages/CropPrediction";
import YieldPrediction from "./pages/YieldPrediction";
import Fertilizer from "./pages/Fertilizer";
import History from "./pages/History";

function ProtectedRoute({
  children,
}) {
  const user =
    getStoredUser();

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/crop-prediction"
          element={
            <ProtectedRoute>
              <CropPrediction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/yield-prediction"
          element={
            <ProtectedRoute>
              <YieldPrediction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/fertilizer"
          element={
            <ProtectedRoute>
              <Fertilizer />
            </ProtectedRoute>
          }
        />

        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}