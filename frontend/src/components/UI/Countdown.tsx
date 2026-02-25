import React from 'react';
import { useCountdown } from '../../hooks/useCountdown';
export function Countdown({targetDate,compact=false}:{targetDate:string|null;compact?:boolean}){
  const{days,hours,minutes,isExpired}=useCountdown(targetDate);
  if(!targetDate)return <span className="text-gray-400 text-sm">Нет дедлайна</span>;
  if(isExpired)return <span className="text-red-500 font-medium text-sm">Закрыт</span>;
  const c=days<=7?'text-red-600':days<=30?'text-yellow-600':'text-green-600';
  if(compact)return <span className={`font-semibold ${c}`}>{days}д</span>;
  return <div className="flex gap-2">{[{v:days,l:'дн'},{v:hours,l:'ч'},{v:minutes,l:'мин'}].map(({v,l})=><div key={l} className="text-center"><div className={`text-xl font-bold ${c}`}>{String(v).padStart(2,'0')}</div><div className="text-xs text-gray-400">{l}</div></div>)}</div>;
}
