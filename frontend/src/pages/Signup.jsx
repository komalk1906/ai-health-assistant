import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import Alert from "../components/Alert";
import { registerUser } from "../services/api";
import "./Auth.css";

const GENDER_OPTIONS = [
  { value: "", label: "Select gender" },
  { value: "female", label: "Female" },
  { value: "male", label: "Male" },
  { value: "other", label: "Other" },
  { value: "prefer_not_to_say", label: "Prefer not to say" },
];

function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    age: "",
    gender: "",
  });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const newErrors = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = "Full name is required.";
    } else if (formData.fullName.trim().length < 2) {
      newErrors.fullName = "Full name must be at least 2 characters.";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required.";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Enter a valid email address.";
    }

    if (!formData.password) {
      newErrors.password = "Password is required.";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters.";
    } else if (formData.password.length > 72) {
      newErrors.password = "Password must be 72 characters or fewer.";
    }

    if (formData.confirmPassword !== formData.password) {
      newErrors.confirmPassword = "Passwords do not match.";
    }

    if (!formData.age) {
      newErrors.age = "Age is required.";
    } else if (Number(formData.age) <= 0 || Number(formData.age) > 120) {
      newErrors.age = "Enter a valid age.";
    }

    if (!formData.gender) {
      newErrors.gender = "Please select a gender.";
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
      await registerUser({
        full_name: formData.fullName.trim(),
        email: formData.email.trim(),
        password: formData.password,
        age: Number(formData.age),
        gender: formData.gender,
      });
      // Account created: ask the user to log in (Login shows a success note)
      navigate("/login", { state: { registered: true } });
    } catch (err) {
      setFormError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <Card className="auth-card">
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Start tracking your health in a few minutes.</p>

        {formError && <Alert variant="danger">{formError}</Alert>}

        <form onSubmit={handleSubmit} noValidate>
          <Input
            id="fullName"
            name="fullName"
            type="text"
            label="Full Name"
            value={formData.fullName}
            onChange={handleChange}
            error={errors.fullName}
            autoComplete="name"
          />

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

          <div className="auth-row">
            <Input
              id="password"
              name="password"
              type="password"
              label="Password"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              autoComplete="new-password"
            />

            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              label="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              autoComplete="new-password"
            />
          </div>

          <div className="auth-row">
            <Input
              id="age"
              name="age"
              type="number"
              label="Age"
              value={formData.age}
              onChange={handleChange}
              error={errors.age}
              min="0"
              max="120"
            />

            <Input
              id="gender"
              name="gender"
              label="Gender"
              value={formData.gender}
              onChange={handleChange}
              error={errors.gender}
              options={GENDER_OPTIONS}
            />
          </div>

          <Button type="submit" fullWidth disabled={isSubmitting}>
            {isSubmitting ? "Creating account..." : "Sign Up"}
          </Button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </Card>
    </div>
  );
}

export default Signup;
