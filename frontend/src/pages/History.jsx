import { useEffect, useState } from "react";
import Card from "../components/Card";
import Alert from "../components/Alert";
import LoadingSpinner from "../components/LoadingSpinner";
import { getHistory } from "../services/api";
import { describeActivity, formatDateTime } from "../utils/format";
import "./History.css";

function History() {
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // Load the logged-in user's history from GET /api/history
  useEffect(() => {
    let cancelled = false;

    getHistory()
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="history-page">
      <h1 className="page-title">Health History</h1>
      <p className="page-subtitle">A record of your past symptom checks, conversations, and profile updates.</p>

      {isLoading && <LoadingSpinner label="Loading your history..." />}

      {error && <Alert variant="danger">{error}</Alert>}

      {!isLoading && !error && items.length === 0 && (
        <p className="history-empty">No history yet. Your activity will appear here.</p>
      )}

      {!isLoading && !error && items.length > 0 && (
        <div className="history-list">
          {items.map((item) => {
            const { label, icon } = describeActivity(item.activity_type);
            return (
              <Card key={item.id} className="history-item">
                <div className="history-icon" aria-hidden="true">{icon}</div>
                <div className="history-details">
                  <div className="history-top-row">
                    <span className="history-type">{label}</span>
                    <span className="history-date">{formatDateTime(item.created_at)}</span>
                  </div>
                  <p className="history-summary">{item.description}</p>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default History;
