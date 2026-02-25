import React,{useEffect,useState} from 'react';
import { useParams,useNavigate } from 'react-router-dom';
import { grantsApi,applicationsApi } from '../services/api';
import { Grant } from '../types';
import { Button } from '../components/UI/Button';
import { DeadlineBadge } from '../components/UI/DeadlineBadge';
import { Countdown } from '../components/UI/Countdown';
import toast from 'react-hot-toast';

export function GrantDetailPage(){
  const{id}=useParams<{id:string}>();
  const nav=useNavigate();
  const[grant,setGrant]=useState<Grant|null>(null);
  const[loading,setLoading]=useState(true);

  useEffect(()=>{
    if(id)grantsApi.get(parseInt(id)).then(r=>{setGrant(r.data);setLoading(false);}).catch(()=>setLoading(false));
  },[id]);

  const subscribe=async()=>{
    if(!grant)return;
    try{await grantsApi.subscribe(grant.id);toast.success('Подписка оформлена!');}
    catch{toast.error('Требуется авторизация');}
  };

  const apply=async()=>{
    if(!grant)return;
    try{const r=await applicationsApi.create(grant.id);nav(`/applications/${r.data.id}`);}
    catch{toast.error('Ошибка создания заявки');}
  };

  if(loading)return <div className="max-w-4xl mx-auto px-4 py-8"><div className="animate-pulse h-64 bg-gray-100 rounded-xl"/></div>;
  if(!grant)return <div className="text-center py-16"><p>Грант не найден</p><Button onClick={()=>nav(-1)} className="mt-4">Назад</Button></div>;

  const deadline=grant.deadlines?.[0]?.deadline_date;

  return(
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Button variant="ghost" size="sm" onClick={()=>nav(-1)} className="mb-6">Назад</Button>
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-8 text-white">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold mb-1">{grant.source_name}</h1>
              {grant.source_url&&<a href={grant.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-200 text-sm hover:text-white">Официальный сайт</a>}
            </div>
            {deadline&&<div className="text-right shrink-0"><div className="text-blue-200 text-xs mb-1">До дедлайна</div><Countdown targetDate={deadline}/></div>}
          </div>
          <div className="mt-4 text-2xl font-bold">{grant.max_amount_text||(grant.max_amount?`${grant.max_amount.toLocaleString('ru-RU')} руб.`:'Сумма не указана')}</div>
        </div>
        <div className="p-8 grid md:grid-cols-2 gap-8">
          <div className="space-y-5">
            {grant.who_can_apply&&<IB title="Кто может подать" text={grant.who_can_apply}/>}
            {grant.age_restrictions&&<IB title="Возраст" text={grant.age_restrictions}/>}
            {grant.window_schedule&&<IB title="Окна подачи" text={grant.window_schedule}/>}
            {grant.submission_target&&<IB title="Куда подавать" text={grant.submission_target}/>}
          </div>
          <div className="space-y-5">
            {grant.typical_docs&&<IB title="Документы" text={grant.typical_docs}/>}
            {grant.reporting&&<IB title="Отчётность" text={grant.reporting}/>}
            {grant.critical_notes&&<IB title="Важно" text={grant.critical_notes}/>}
            {grant.deadlines.length>0&&(
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Дедлайны</h3>
                <div className="space-y-1">{grant.deadlines.map(d=><DeadlineBadge key={d.id} deadline={d.deadline_date} label={d.window_label}/>)}</div>
              </div>
            )}
          </div>
        </div>
        <div className="border-t border-gray-100 p-6 flex gap-3 flex-wrap">
          <Button size="lg" onClick={apply}>Создать заявку</Button>
          <Button variant="secondary" size="lg" onClick={subscribe}>Подписаться на уведомления</Button>
        </div>
      </div>
    </div>
  );
}

function IB({title,text}:{title:string;text:string}){
  return(
    <div>
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">{title}</h3>
      <p className="text-gray-700 text-sm leading-relaxed">{text}</p>
    </div>
  );
}
