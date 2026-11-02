import Card from "./Card";
import "./MedicineCard.css";

/**
 * Displays general information about one medicine, exactly as returned by
 * the backend (GET /api/medicines):
 * medicine: { name, common_uses, precautions, side_effects, warnings,
 *             seek_professional_advice }
 */
function MedicineCard({ medicine }) {
  return (
    <Card className="medicine-card">
      <h3 className="medicine-name">{medicine.name}</h3>

      <div className="medicine-section">
        <span className="medicine-label">Common uses</span>
        <p>{medicine.common_uses}</p>
      </div>

      <div className="medicine-section">
        <span className="medicine-label">Precautions</span>
        <p>{medicine.precautions}</p>
      </div>

      <div className="medicine-section">
        <span className="medicine-label">Common side effects</span>
        <p>{medicine.side_effects}</p>
      </div>

      <div className="medicine-section medicine-warning">
        <span className="medicine-label">Warnings</span>
        <p>{medicine.warnings}</p>
      </div>

      {medicine.seek_professional_advice && (
        <div className="medicine-section">
          <span className="medicine-label">When to see a doctor</span>
          <p>{medicine.seek_professional_advice}</p>
        </div>
      )}
    </Card>
  );
}

export default MedicineCard;
