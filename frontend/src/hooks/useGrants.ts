import { useState, useEffect } from 'react';
import { Grant } from '../types';
import { grantsApi } from '../services/api';
export function useGrants(filters?: any) {
  const [grants, setGrants] = useState<Grant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);
  const fetch_ = async () => { try { setLoading(true); const r = await grantsApi.list(filters); setGrants(r.data); setError(null); } catch(e:any) { setError(e.message); } finally { setLoading(false); } };
  useEffect(()=>{ fetch_(); }, [JSON.stringify(filters)]);
  return { grants, loading, error, refetch: fetch_ };
}
