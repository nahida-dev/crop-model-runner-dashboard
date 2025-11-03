const getUser = () => {
  const v = localStorage.getItem('userEmail');
  return v || 'analyst@corteva.internal';
};

async function apiGet(path: string) {
  const res = await fetch(path, {
    headers: { 'x-user-id': getUser() },
  });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function apiPost(path: string, body: any) {
  const res = await fetch(path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-user-id': getUser(),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json();
}

export const fetchModels = () => apiGet('/api/models');

export const submitRun = (payload: {
  model_id: string;
  region: string;
  year: number;  
}) => apiPost('/api/runs', payload);

export const fetchRunStatus = (runId: number) =>
  apiGet(`/api/runs/${runId}/status`);

export const fetchRunResults = (runId: number) =>
  apiGet(`/api/runs/${runId}/results`);

export const setUserEmail = (email: string) => {
  localStorage.setItem('userEmail', email);
};
export const getUserEmail = getUser;
