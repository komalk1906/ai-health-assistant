import { useEffect, useState } from "react";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import Alert from "../components/Alert";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  getCurrentUser,
  getHealthProfile,
  createHealthProfile,
  updateHealthProfile,
} from "../services/api";
import "./Profile.css";

// Form values are strings (what <input> gives us). The backend uses
// snake_case names and numbers, so toForm()/toPayload() convert between them.
const EMPTY_PROFILE = {
  height: "",
  weight: "",
  bloodGroup: "",
  allergies: "",
  existingConditions: "",
  currentMedications: "",
  emergencyContact: "",
};

const GENDER_OPTIONS = [
  { value: "", label: "-" },
  { value: "female", label: "Female" },
  { value: "male", label: "Male" },
  { value: "other", label: "Other" },
  { value: "prefer_not_to_say", label: "Prefer not to say" },
];

/** Backend profile -> form values */
function toForm(p) {
  return {
    height: p.height_cm ?? "",
    weight: p.weight_kg ?? "",
    bloodGroup: p.blood_group ?? "",
    allergies: p.allergies ?? "",
    existingConditions: p.existing_conditions ?? "",
    currentMedications: p.current_medications ?? "",
    emergencyContact: p.emergency_contact ?? "",
  };
}

/** Form values -> backend payload (empty text becomes null) */
function toPayload(f) {
  const text = (value) => (String(value).trim() === "" ? null : String(value).trim());
  const number = (value) => (String(value).trim() === "" ? null : Number(value));
  return {
    height_cm: number(f.height),
    weight_kg: number(f.weight),
    blood_group: text(f.bloodGroup),
    allergies: text(f.allergies),
    existing_conditions: text(f.existingConditions),
    current_medications: text(f.currentMedications),
    emergency_contact: text(f.emergencyContact),
  };
}

function validate(f) {
  if (f.height !== "" && (Number(f.height) <= 0 || Number(f.height) > 300)) {
    return "Height must be between 1 and 300 cm.";
  }
  if (f.weight !== "" && (Number(f.weight) <= 0 || Number(f.weight) > 500)) {
    return "Weight must be between 1 and 500 kg.";
  }
  return "";
}

function Profile() {
  const [account, setAccount] = useState({ fullName: "", age: "", gender: "" });
  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [draft, setDraft] = useState(EMPTY_PROFILE);
  const [hasProfile, setHasProfile] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Load the account details (GET /api/auth/me) and the health profile
  // (GET /api/health/profile). A 404 just means no profile was created yet.
  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const user = await getCurrentUser();
        let savedProfile = null;
        try {
          savedProfile = await getHealthProfile();
        } catch (err) {
          if (err.status !== 404) throw err;
        }
        if (cancelled) return;

        setAccount({
          fullName: user.full_name ?? "",
          age: user.age ?? "",
          gender: (user.gender ?? "").toLowerCase(),
        });
        if (savedProfile) {
          const form = toForm(savedProfile);
          setProfile(form);
          setDraft(form);
          setHasProfile(true);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setDraft((prev) => ({ ...prev, [name]: value }));
  }

  function handleEdit() {
    setDraft(profile);
    setError("");
    setSuccess("");
    setIsEditing(true);
  }

  function handleCancel() {
    setDraft(profile);
    setError("");
    setIsEditing(false);
  }

  async function handleSave(e) {
    e.preventDefault();
    setError("");
    setSuccess("");

    const validationMessage = validate(draft);
    if (validationMessage) {
      setError(validationMessage);
      return;
    }

    setIsSaving(true);
    try {
      // First save creates the profile (POST); later saves update it (PUT).
      const saved = hasProfile
        ? await updateHealthProfile(toPayload(draft))
        : await createHealthProfile(toPayload(draft));
      const form = toForm(saved);
      setProfile(form);
      setDraft(form);
      setHasProfile(true);
      setIsEditing(false);
      setSuccess("Your health profile was saved.");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSaving(false);
    }
  }

  const data = isEditing ? draft : profile;

  if (isLoading) {
    return (
      <div className="profile-page">
        <LoadingSpinner label="Loading your profile..." />
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <div>
          <h1 className="page-title">Health Profile</h1>
          <p className="page-subtitle">Keep your health details accurate and up to date.</p>
        </div>
        {!isEditing && <Button onClick={handleEdit}>{hasProfile ? "Edit" : "Add details"}</Button>}
      </div>

      {!hasProfile && !isEditing && (
        <Alert variant="info">
          You haven't added your health details yet. Click "Add details" to create your profile.
        </Alert>
      )}
      {success && <Alert variant="success">{success}</Alert>}
      {error && <Alert variant="danger">{error}</Alert>}

      <form onSubmit={handleSave}>
        <Card className="profile-section">
          <h2 className="profile-section-title">Personal Information</h2>
          <div className="profile-grid">
            <Input
              id="fullName"
              name="fullName"
              label="Full Name"
              value={account.fullName}
              readOnly
              disabled
            />
            <Input
              id="age"
              name="age"
              type="number"
              label="Age"
              value={account.age}
              readOnly
              disabled
            />
            <Input
              id="gender"
              name="gender"
              label="Gender"
              value={account.gender}
              options={GENDER_OPTIONS}
              disabled
            />
          </div>
        </Card>

        <Card className="profile-section">
          <h2 className="profile-section-title">Health Information</h2>
          <div className="profile-grid">
            <Input
              id="height"
              name="height"
              type="number"
              label="Height (cm)"
              min="1"
              max="300"
              step="any"
              value={data.height}
              onChange={handleChange}
              disabled={!isEditing}
            />
            <Input
              id="weight"
              name="weight"
              type="number"
              label="Weight (kg)"
              min="1"
              max="500"
              step="any"
              value={data.weight}
              onChange={handleChange}
              disabled={!isEditing}
            />
            <Input
              id="bloodGroup"
              name="bloodGroup"
              label="Blood Group"
              maxLength={10}
              value={data.bloodGroup}
              onChange={handleChange}
              disabled={!isEditing}
            />
            <Input
              id="allergies"
              name="allergies"
              label="Allergies"
              value={data.allergies}
              onChange={handleChange}
              disabled={!isEditing}
            />
            <Input
              id="existingConditions"
              name="existingConditions"
              label="Existing Conditions"
              value={data.existingConditions}
              onChange={handleChange}
              disabled={!isEditing}
            />
            <Input
              id="currentMedications"
              name="currentMedications"
              label="Current Medications"
              value={data.currentMedications}
              onChange={handleChange}
              disabled={!isEditing}
            />
          </div>
        </Card>

        <Card className="profile-section">
          <h2 className="profile-section-title">Emergency Contact</h2>
          <div className="profile-grid">
            <Input
              id="emergencyContact"
              name="emergencyContact"
              label="Emergency Contact"
              maxLength={100}
              value={data.emergencyContact}
              onChange={handleChange}
              disabled={!isEditing}
            />
          </div>
        </Card>

        {isEditing && (
          <div className="profile-actions">
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "Saving..." : "Save"}
            </Button>
            <Button type="button" variant="ghost" onClick={handleCancel}>
              Cancel
            </Button>
          </div>
        )}
      </form>
    </div>
  );
}

export default Profile;
