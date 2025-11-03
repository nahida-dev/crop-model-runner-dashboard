import React from 'react'
import { fetchModels } from '../api'
import { ModelInfo } from '../types'

type Props = {
  value: string;
  onChange: (modelId: string) => void;
};

export default function ModelSelector({ value, onChange }: Props) {
  const [models, setModels] = React.useState<ModelInfo[]>([]);
  const [error, setError] = React.useState<string>('');

  React.useEffect(() => {
    fetchModels()
      .then(setModels)
      .catch(err => setError(err.message));
  }, []);

  if (error) return <div style={{color:'red'}}>Failed to load models: {error}</div>;

  const current = models.find(m => m.model_id === value);

  return (
    <div style={{ display:'flex', flexDirection:'column' }}>
      <label style={{ fontSize:'0.9rem', marginBottom:'0.25rem' }}>
        Model
      </label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{ padding:'0.5rem' }}
      >
        <option value=''>-- select a model --</option>
        {models.map(m => (
          <option key={m.model_id} value={m.model_id}>
            {m.name}
          </option>
        ))}
      </select>
      <small style={{ color:'#666', marginTop:'0.25rem' }}>
        {current?.description}
      </small>
    </div>
  );
}
