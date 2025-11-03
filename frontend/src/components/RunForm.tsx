import React from "react";
import { submitRun } from "../api";

type Props = {
  modelId: string;
  onRunStarted: (runId: number) => void;
  setError: (msg: string) => void;
};

export default function RunForm({ modelId, onRunStarted, setError }: Props) {
  // dropdown options for region
  const [regions, setRegions] = React.useState<string[]>([]);
  const [loadingRegions, setLoadingRegions] = React.useState<boolean>(false);

  // selected values
  const [region, setRegion] = React.useState<string>("");
  const [year, setYear] = React.useState<number>(2025);

  // submit button spinner
  const [submitting, setSubmitting] = React.useState<boolean>(false);

  // fetch region list from backend on mount
  React.useEffect(() => {
    const loadRegions = async () => {
      try {
        setLoadingRegions(true);
        const res = await fetch("/api/regions", {
          headers: {
            // even for regions, we enforce auth header to match the rest of the app
            "x-user-id": localStorage.getItem("userEmail") || "analyst@corteva.internal",
          },
        });
        if (!res.ok) {
          throw new Error(`Failed to load regions: ${res.status}`);
        }
        const data = await res.json();
        // expecting { regions: ["IA-North", "IA-South", ...] }
        setRegions(data.regions || []);
        // preselect first region if any
        if (data.regions && data.regions.length > 0) {
          setRegion(data.regions[0]);
        }
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Could not load regions");
      } finally {
        setLoadingRegions(false);
      }
    };

    loadRegions();
  }, [setError]);

  // handler for form submit
  const handleSubmit = async () => {
    if (!modelId) {
      setError("Please select a model first.");
      return;
    }
    if (!region) {
      setError("Please select a region.");
      return;
    }
    if (!year) {
      setError("Please enter a valid year.");
      return;
    }

    try {
      setSubmitting(true);

      const res = await submitRun({
        model_id: modelId,
        region,
        year,
      });

      onRunStarted(res.run_id);
    } catch (e: any) {
      setError(e.message || "Failed to submit run");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: "grid", gap: "0.75rem", maxWidth: "300px" }}>
      {/* Region dropdown */}
      <div>
        <label
          style={{
            display: "block",
            fontSize: "0.9rem",
            marginBottom: "0.25rem",
          }}
        >
          Region
        </label>

        {loadingRegions ? (
          <div style={{ fontSize: "0.85rem", color: "#666" }}>
            Loading regions...
          </div>
        ) : (
          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #ccc",
              borderRadius: "4px",
            }}
          >
            {regions.length === 0 && (
              <option value="">No regions available</option>
            )}
            {regions.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Year input */}
      <div>
        <label
          style={{
            display: "block",
            fontSize: "0.9rem",
            marginBottom: "0.25rem",
          }}
        >
          Year
        </label>
        <input
          type="number"
          value={year}
          onChange={(e) => {
            const val = Number(e.target.value);
            // basic safety: clamp year a little
            if (!Number.isNaN(val)) {
              setYear(val);
            }
          }}
          style={{
            width: "100%",
            padding: "0.5rem",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        <small style={{ color: "#666", fontSize: "0.75rem" }}>
          Example: 2025
        </small>
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={submitting || loadingRegions}
        style={{
          padding: "0.6rem 0.8rem",
          background: submitting ? "#999" : "#1976d2",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: submitting ? "default" : "pointer",
          fontWeight: 500,
          fontSize: "0.9rem",
        }}
      >
        {submitting ? "Submitting..." : "Run Model"}
      </button>
    </div>
  );
}
