import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Card from "../components/Card";
import HealthStatCard from "../components/HealthStatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { getCurrentUser, getHealthProfile, getHistory, getStoredUser } from "../services/api";
import { describeActivity, formatDateTime } from "../utils/format";
import "./Dashboard.css";

const QUICK_ACTIONS = [
  { to: "/chat", icon: "💬", title: "AI Health Chat", description: "Ask a health question" },
  { to: "/symptoms", icon: "🩺", title: "Symptom Checker", description: "Check your symptoms" },
  { to: "/profile", icon: "📋", title: "Health Profile", description: "View or edit your profile" },
  { to: "/medicines", icon: "💊", title: "Medicine Information", description: "Look up a medicine" },
];

/** Show "-" when a value has not been filled in yet. */
const orDash = (value, suffix = "") =>
  value === null || value === undefined || value === "" ? "-" : `${value}${suffix}`;

function Dashboard() {
  const [user, setUser] = useState(getStoredUser());
  const [profile, setProfile] = useState(null);
  const [recent, setRecent] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load real data: account (GET /api/auth/me), health profile
  // (GET /api/health/profile) and the latest activity (GET /api/history).
  // allSettled means one failing request (e.g. no profile yet = 404) does not
  // stop the rest of the dashboard from showing.
  useEffect(() => {
    let cancelled = false;

    Promise.allSettled([getCurrentUser(), getHealthProfile(), getHistory()]).then(
      ([userResult, profileResult, historyResult]) => {
        if (cancelled) return;
        if (userResult.status === "fulfilled") setUser(userResult.value);
        if (profileResult.status === "fulfilled") setProfile(profileResult.value);
        if (historyResult.status === "fulfilled") setRecent(historyResult.value.slice(0, 3));
        setIsLoading(false);
      }
    );

    return () => {
      cancelled = true;
    };
  }, []);

  const firstName = user?.full_name ? user.full_name.split(" ")[0] : "";

  const healthSummary = [
    { label: "Age", value: orDash(user?.age, " yrs"), icon: "🎂" },
    { label: "Weight", value: orDash(profile?.weight_kg, " kg"), icon: "⚖️" },
    { label: "Blood Group", value: orDash(profile?.blood_group), icon: "🩸" },
    { label: "Allergies", value: orDash(profile?.allergies), icon: "⚠️" },
  ];

  return (
    <div className="dashboard">
      <h1 className="dashboard-welcome">Welcome back{firstName ? `, ${firstName}` : ""} 👋</h1>
      <p className="dashboard-subtitle">Here's a quick overview of your health assistant.</p>

      <section className="dashboard-section">
        <h2 className="dashboard-section-title">Quick actions</h2>
        <div className="quick-actions-grid">
          {QUICK_ACTIONS.map((action) => (
            <Link to={action.to} key={action.to} className="quick-action-link">
              <Card className="quick-action-card">
                <div className="quick-action-icon" aria-hidden="true">{action.icon}</div>
                <h3>{action.title}</h3>
                <p>{action.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <section className="dashboard-section">
        <h2 className="dashboard-section-title">Health summary</h2>
        <div className="stats-row">
          {healthSummary.map((stat) => (
            <HealthStatCard key={stat.label} {...stat} />
          ))}
        </div>
      </section>

      <section className="dashboard-section">
        <h2 className="dashboard-section-title">Recent activity</h2>
        <Card>
          {isLoading ? (
            <LoadingSpinner label="Loading activity..." />
          ) : recent.length === 0 ? (
            <p className="activity-summary">
              No activity yet. Try the AI chat or the symptom checker to get started.
            </p>
          ) : (
            <ul className="activity-list">
              {recent.map((item) => (
                <li key={item.id} className="activity-item">
                  <div>
                    <p className="activity-type">{describeActivity(item.activity_type).label}</p>
                    <p className="activity-summary">{item.description}</p>
                  </div>
                  <span className="activity-date">{formatDateTime(item.created_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </section>
    </div>
  );
}

export default Dashboard;
