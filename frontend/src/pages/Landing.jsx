import { Link } from "react-router-dom";
import Card from "../components/Card";
import Button from "../components/Button";
import "./Landing.css";

const FEATURES = [
  {
    icon: "💬",
    title: "AI Health Chat",
    description: "Ask general health questions and get clear, easy-to-understand information any time.",
  },
  {
    icon: "🩺",
    title: "Symptom Checker",
    description: "List your symptoms and get a general sense of possible causes and next steps.",
  },
  {
    icon: "📋",
    title: "Health Profile",
    description: "Keep your key health details in one place - allergies, conditions, and medications.",
  },
  {
    icon: "💊",
    title: "Medicine Information",
    description: "Look up common uses, precautions, and side effects for everyday medicines.",
  },
];

function Landing() {
  return (
    <div>
      <section className="hero">
        <div className="container hero-inner">
          <h1 className="hero-title">Your everyday health questions, answered clearly.</h1>
          <p className="hero-subtitle">
            AI Health Assistant gives you general health information, a symptom checker, and a
            place to keep track of your health - all in one simple app.
          </p>
          <div className="hero-actions">
            <Link to="/signup">
              <Button variant="primary">Get Started</Button>
            </Link>
            <Link to="/login">
              <Button variant="ghost">Login</Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="container features-section">
        <h2 className="features-heading">What you can do</h2>
        <div className="features-grid">
          {FEATURES.map((feature) => (
            <Card key={feature.title} className="feature-card">
              <div className="feature-icon" aria-hidden="true">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <footer className="footer">
        <div className="container footer-inner">
          <p>AI Health Assistant provides general health information and is not a substitute for professional medical advice.</p>
          <p className="footer-copyright">Built as a TYBSc Computer Science mini project.</p>
        </div>
      </footer>
    </div>
  );
}

export default Landing;
