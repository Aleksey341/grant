import { useState, useEffect } from 'react';
interface CR { days:number;hours:number;minutes:number;seconds:number;isExpired:boolean;total:number; }
export function useCountdown(targetDate: string | null): CR {
  const calc = (): CR => {
    if (!targetDate) return {days:0,hours:0,minutes:0,seconds:0,isExpired:true,total:0};
    const d = new Date(targetDate).getTime() - Date.now();
    if (d <= 0) return {days:0,hours:0,minutes:0,seconds:0,isExpired:true,total:0};
    return { days:Math.floor(d/86400000), hours:Math.floor((d%86400000)/3600000), minutes:Math.floor((d%3600000)/60000), seconds:Math.floor((d%60000)/1000), isExpired:false, total:d };
  };
  const [t, setT] = useState(calc);
  useEffect(() => { if (!targetDate) return; const id = setInterval(()=>setT(calc()),1000); return ()=>clearInterval(id); }, [targetDate]);
  return t;
}
