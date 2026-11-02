import "./HealthStatCard.css";

/**
 * Small stat tile used on the Dashboard's "Health summary" row,
 * e.g. Age, Weight, Blood Group, Allergies.
 */
function HealthStatCard({ label, value, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-icon" aria-hidden="true">{icon}</div>
      <div>
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
      </div>
    </div>
  );
}

export default HealthStatCard;
