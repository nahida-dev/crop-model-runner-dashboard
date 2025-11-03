import React from 'react'
import { setUserEmail, getUserEmail } from '../api'

const USERS = [
  'analyst@corteva.internal',
  'scientist@corteva.internal',
  'viewer@corteva.internal'
];

export default function UserSelector() {
  const [val, setVal] = React.useState(getUserEmail());

  const onChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setVal(e.target.value);
    setUserEmail(e.target.value);
  };

  return (
    <div style={{ display:'flex', gap:'0.5rem', alignItems:'center' }}>
      <span style={{ fontSize:'0.8rem', color:'#555' }}>User:</span>
      <select value={val} onChange={onChange}>
        {USERS.map(u => (
          <option key={u} value={u}>{u}</option>
        ))}
      </select>
    </div>
  );
}
