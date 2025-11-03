import React from 'react'
import { fetchRunStatus } from '../api'
import { RunStatusResponse } from '../types'

type Props = {
  runId: number | null;
  onComplete: () => void;
  setError: (msg: string) => void;
  status: RunStatusResponse | null;
  setStatus: (s: RunStatusResponse | null) => void;
};

export default function RunStatus({
  runId,
  onComplete,
  setError,
  status,
  setStatus
}: Props) {

  React.useEffect(() => {
    if (!runId) return;
    let cancelled = false;

    const poll = async () => {
      try {
        const res = await fetchRunStatus(runId);
        if (!cancelled) {
          setStatus(res);
          if (res.status === 'succeeded' || res.status === 'failed') {
            onComplete();
          } else {
            setTimeout(poll, 2000);
          }
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e.message || 'Status poll failed');
        }
      }
    };

    poll();
    return () => { cancelled = true; };
  }, [runId]);

  if (!runId) return null;
  if (!status) return <div>Checking status...</div>;

  // pick a chip color by status
  const bg =
    status.status === 'succeeded' ? '#ccffcc' :
    status.status === 'failed'    ? '#ffcccc' :
    status.status === 'running'   ? 'yellow' :
                                    'transparent';

  return (
    <div style={{ marginTop:'1rem' }}>
      <strong>Run #{status.run_id}</strong><br/>
      Status:{' '}
      <code style={{
        backgroundColor: bg,
        color: 'black',
        padding: '2px 6px',
        borderRadius: 4
      }}>
        {status.status}
      </code>
      <br/>
      Started:{' '}
      {status?.started_at
        ? new Date(status.started_at).toLocaleString()
        : '—'}
      <br />
      Finished:{' '}
      {status.finished_at
        ? new Date(status.finished_at).toLocaleString()
        : '—'}
    </div>
  );
}
