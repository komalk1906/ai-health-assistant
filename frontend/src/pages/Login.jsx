import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import Alert from "../components/Alert";
import { loginUser, saveSession } from "../services/api";
import "./Auth.css";

/**
 * Login page. Validates the form, then calls POST /api/auth/login.
 * On success the JWT token is saved (services/api.js) and the user is sent
 * to the dashboard.
 */
function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const justRegistered = Boolean(location.state?.registered);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const newErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = "Email is required.";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Enter a valid email address.";
    }

    if (!formData.password) {
      newErrors.password = "Password is required.";
    }

    return newErrors;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError("");

    const validationErrors = validate();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setIsSubmitting(true);
    try {
      const data = await loginUser({
        email: formData.email.trim(),
        password: formData.password,
      });
      saveSession(data);
      navigate("/dashboard");
    } catch (err) {
      setFormError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <Card className="auth-card">
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Log in to continue to your health assistant.</p>

        {justRegistered && !formError && (
          <Alert variant="success">Account created successfully. Please log in.</Alert>
        )}
        {formError && <Alert variant="danger">{formError}</Alert>}

        <form onSubmit={handleSubmit} noValidate>
          <Input
            id="email"
            name="email"
            type="email"
            label="Email"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            autoComplete="email"
          />

          <Input
            id="password"
            name="password"
            type="password"
            label="Password"
            value={formData.password}
            onChange={handleChange}
            error={errors.password}
            autoComplete="current-password"
          />

          <Button type="submit" fullWidth disabled={isSubmitting}>
            {isSubmitting ? "Logging in..." : "Login"}
          </Button>
        </form>

        <p className="auth-switch">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </Card>
    </div>
  );
}

export default Login;
