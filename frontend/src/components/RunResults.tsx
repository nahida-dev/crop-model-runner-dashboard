import React from 'react'
import { fetchRunResults } from '../api'
import { RunResultsResponse } from '../types'

type Props = {
  runId: number | null;
  ready: boolean;
  setError: (msg: string) => void;
};

export default function RunResults({ runId, ready, setError }: Props) {
  const [results, setResults] = React.useState<RunResultsResponse | null>(null);

  React.useEffect(() => {
    if (!ready || !runId) return;
    fetchRunResults(runId)
      .then(setResults)
      .catch(e => setError(e.message || 'Failed to load results'));
  }, [ready, runId]);

  if (!ready) return null;
  if (!results) return <div>Loading results…</div>;

  return (
    <div style={{ marginTop:'1rem' }}>
      <h3>Summary Metrics</h3>
      <pre style={{
        background:'#f5f5f5',
        padding:'0.5rem',
        borderRadius:'4px',
        overflowX:'auto'
      }}>
        {JSON.stringify(results.summaryMetrics, null, 2)}
      </pre>

      <h3>Result Table</h3>
      <div style={{
        overflowX:'auto',
        border:'1px solid #ccc',
        borderRadius:'4px'
      }}>
        <table style={{ borderCollapse:'collapse', width:'100%' }}>
          <thead>
            <tr>
              {Object.keys(results.table[0] || {}).map((col) => (
                <th
                  key={col}
                  style={{
                    textAlign:'left',
                    borderBottom:'1px solid #ccc',
                    padding:'0.5rem',
                    background:'#fafafa'
                  }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.table.map((row, i) => (
              <tr key={i}>
                {Object.keys(row).map((col) => (
                  <td
                    key={col}
                    style={{
                      borderBottom:'1px solid #eee',
                      padding:'0.5rem',
                      fontSize:'0.9rem'
                    }}
                  >
                    {String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
