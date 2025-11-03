export type ModelInfo = {
  model_id: string;
  name: string;
  description?: string;
};

export type RunCreatedResponse = {
  run_id: number;
};

export type RunStatusResponse = {
  run_id: number;
  status: string;
  started_at: string | null;
  finished_at: string | null;
};

export type RunResultsResponse = {
  summaryMetrics: Record<string, unknown>;
  table: Array<Record<string, unknown>>;
};
