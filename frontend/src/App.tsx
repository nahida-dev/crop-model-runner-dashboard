import React from 'react'
import UserSelector from './components/UserSelector'
import ModelSelector from './components/ModelSelector'
import RunForm from './components/RunForm'
import RunStatus from './components/RunStatus'
import RunResults from './components/RunResults'
import ErrorBanner from './components/ErrorBanner'
import { RunStatusResponse } from './types'

export default function App() {
  const [modelId, setModelId] = React.useState('');
  const [runId, setRunId] = React.useState<number | null>(null);
  const [error, setError] = React.useState('');
  const [status, setStatus] = React.useState<RunStatusResponse | null>(null);
  const [done, setDone] = React.useState(false);

  const handleRunStarted = (rid: number) => {
    setRunId(rid);
    setStatus(null);
    setDone(false);
    setError('');
  };

  const handleComplete = () => {
    setDone(true);
  };

  return (
    <div style={{ fontFamily:'sans-serif', padding:'1rem', maxWidth:'900px', margin:'0 auto' }}>
      <header style={{
        display:'flex',
        justifyContent:'space-between',
        alignItems:'center',
        marginBottom:'1rem'
      }}>
        <h2 style={{ margin:0 }}>Model Runner Dashboard</h2>
        <UserSelector />
      </header>

      <ErrorBanner message={error} />

      <section style={{
        display:'grid',
        gridTemplateColumns:'1fr 1fr',
        gap:'2rem',
        alignItems:'start',
        marginBottom:'2rem'
      }}>
        <div style={{ border:'1px solid #ccc', borderRadius:'6px', padding:'1rem' }}>
          <h3 style={{ marginTop:0 }}>1. Select Model</h3>
          <ModelSelector value={modelId} onChange={setModelId} />
        </div>

        <div style={{ border:'1px solid #ccc', borderRadius:'6px', padding:'1rem' }}>
          <h3 style={{ marginTop:0 }}>2. Configure & Run</h3>
          <RunForm
            modelId={modelId}
            onRunStarted={handleRunStarted}
            setError={setError}
          />
        </div>
      </section>

      <section style={{
        border:'1px solid #ccc',
        borderRadius:'6px',
        padding:'1rem',
        marginBottom:'2rem'
      }}>
        <h3 style={{ marginTop:0 }}>3. Run Status</h3>
        <RunStatus
          runId={runId}
          status={status}
          setStatus={setStatus}
          setError={setError}
          onComplete={handleComplete}
        />
      </section>

      <section style={{
        border:'1px solid #ccc',
        borderRadius:'6px',
        padding:'1rem',
        marginBottom:'4rem'
      }}>
        <h3 style={{ marginTop:0 }}>4. Results</h3>
        <RunResults
          runId={runId}
          ready={done}
          setError={setError}
        />
      </section>
    </div>
  );
}
