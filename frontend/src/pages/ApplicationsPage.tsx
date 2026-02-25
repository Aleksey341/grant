import React,{useEffect,useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { applicationsApi } from '../services/api';
import { Application } from '../types';
import { Button } from '../components/UI/Button';
import toast from 'react-hot-toast';

const STATUS_LABELS:Record<string,string>={draft:'Черновик',in_progress:'В работе',complete:'Завершена'};

export function ApplicationsPage(){
  const nav=useNavigate();
  const[apps,setApps]=useState<Application[]>([]);
  const[loading,setLoading]=useState(true);

  useEffect(()=>{
    applicationsApi.list().then(r=>{setApps(r.data);setLoading(false);}).catch(()=>setLoading(false));
  },[]);

  const del=async(id:number)=>{
    if(!confirm('Удалить заявку?'))return;
    try{await applicationsApi.delete(id);setApps(p=>p.filter(a=>a.id!==id));toast.success('Удалено');}
    catch{toast.error('Ошибка');}
  };

  return(
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Button variant="ghost" size="sm" onClick={()=>nav('/dashboard')} className="mb-6">К каталогу</Button>
      <h1 className="text-2xl font-bold mb-6">Мои заявки</h1>
      {loading?(
        <div className="space-y-3">{[1,2,3].map(i=><div key={i} className="h-20 bg-gray-100 rounded-xl animate-pulse"/>)}</div>
      ):apps.length===0?(
        <div className="text-center py-16 text-gray-400">
          <p className="text-5xl mb-3">clipboard</p>
          <p className="font-medium">Заявок нет</p>
          <Button className="mt-4" onClick={()=>nav('/dashboard')}>Выбрать грант</Button>
        </div>
      ):(
        <div className="space-y-3">
          {apps.map(a=>(
            <div key={a.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between hover:border-blue-200 cursor-pointer" onClick={()=>nav(`/applications/${a.id}`)}>
              <div>
                <div className="font-medium">Заявка #{a.id}</div>
                <div className="text-sm text-gray-500">{STATUS_LABELS[a.status]||a.status} — Шаг {a.current_step}/5</div>
                <div className="text-xs text-gray-400">{new Date(a.updated_at||a.created_at).toLocaleDateString('ru-RU')}</div>
              </div>
              <div className="flex gap-2" onClick={e=>e.stopPropagation()}>
                <Button size="sm" onClick={()=>nav(`/applications/${a.id}`)}>Продолжить</Button>
                <Button size="sm" variant="ghost" onClick={()=>del(a.id)}>Удалить</Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
