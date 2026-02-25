import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Grant } from '../../types';
import { Card } from '../UI/Card';
import { DeadlineBadge } from '../UI/DeadlineBadge';
import { Countdown } from '../UI/Countdown';

const CATS: Record<string,{label:string;color:string}> = {
  individual:{label:'Физ. лица',color:'bg-blue-50 text-blue-700'},
  nko:{label:'НКО',color:'bg-purple-50 text-purple-700'},
  business:{label:'Бизнес',color:'bg-green-50 text-green-700'},
};
export function GrantCard({grant}:{grant:Grant}){
  const nav=useNavigate();
  const cat=CATS[grant.category]||CATS.individual;
  const amount=grant.max_amount_text||(grant.max_amount?`${grant.max_amount.toLocaleString('ru-RU')} ₽`:'Сумма не указана');
  return(
    <Card className="p-5 hover:border-blue-200 transition-colors" onClick={()=>nav(`/grants/${grant.id}`)}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cat.color}`}>{cat.label}</span>
        {grant.nearest_deadline&&<Countdown targetDate={grant.nearest_deadline} compact/>}
      </div>
      <h3 className="font-semibold text-gray-900 line-clamp-2 text-sm mb-2 leading-tight">{grant.source_name}</h3>
      {grant.who_can_apply&&<p className="text-xs text-gray-400 line-clamp-1 mb-2">{grant.who_can_apply}</p>}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span className="text-primary-600 font-semibold text-sm">{amount}</span>
        <DeadlineBadge deadline={grant.nearest_deadline} label={grant.deadline_label}/>
      </div>
    </Card>
  );
}
