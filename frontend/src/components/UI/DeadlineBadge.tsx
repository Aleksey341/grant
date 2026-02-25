import React from 'react';
export function DeadlineBadge({deadline,label}:{deadline?:string|null;label?:string|null}){
  if(!deadline)return <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">Нет дедлайна</span>;
  const d=new Date(deadline);
  const days=Math.ceil((d.getTime()-Date.now())/86400000);
  const c=days<=0?'bg-red-100 text-red-700':days<=7?'bg-orange-100 text-orange-700':days<=30?'bg-yellow-100 text-yellow-700':'bg-green-100 text-green-700';
  return <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${c}`}>{days<=0?'Истёк':`${days} дн.`} — {d.toLocaleDateString('ru-RU')}{label?` (${label})`:''}</span>;
}
