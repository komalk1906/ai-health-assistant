/**
 * src/utils/format.js
 * ---------------------
 * Small display helpers shared by several pages.
 */

/**
 * The backend stores times in UTC but sends them without a "Z" suffix
 * (e.g. "2026-10-31T08:15:00"). JavaScript would treat that as LOCAL time and
 * show the wrong hour, so we add the "Z" first.
 */
export function formatDateTime(isoString) {
  if (!isoString) return "";
  const hasZone = /(Z|[+-]\d{2}:?\d{2})$/.test(isoString);
  const date = new Date(hasZone ? isoString : `${isoString}Z`);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

/** Label + icon for each activity_type stored in the backend history table. */
const ACTIVITY_TYPES = {
  chat: { label: "AI Chat", icon: "💬" },
  symptom_check: { label: "Symptom Check", icon: "🩺" },
  profile_update: { label: "Profile Update", icon: "📋" },
};

export function describeActivity(activityType) {
  return ACTIVITY_TYPES[activityType] || { label: "Activity", icon: "🕘" };
}
