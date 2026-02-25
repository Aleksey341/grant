import os

BASE = "C:/Users/cobra/grants-assistant/frontend"

def w(rel, content):
    full = os.path.join(BASE, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'OK: {rel}')

w('src/components/Grants/GrantCard.tsx', r"""import React from 'react';
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
""")

w('src/components/Grants/GrantFilters.tsx', r"""import React,{useState} from 'react';
import { Button } from '../UI/Button';
interface Filters{search?:string;category?:string;days_until_deadline?:number;}
export function GrantFilters({onFilter}:{onFilter:(f:Filters)=>void}){
  const[search,setSearch]=useState('');
  const[category,setCategory]=useState('');
  const[deadline,setDeadline]=useState('');
  const apply=()=>{const f:Filters={};if(search)f.search=search;if(category)f.category=category;if(deadline)f.days_until_deadline=parseInt(deadline);onFilter(f);};
  const reset=()=>{setSearch('');setCategory('');setDeadline('');onFilter({});};
  return(
    <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm flex flex-wrap gap-3">
      <input className="input flex-1 min-w-48" placeholder="Поиск..." value={search} onChange={e=>setSearch(e.target.value)} onKeyDown={e=>e.key==='Enter'&&apply()}/>
      <select className="input w-44" value={category} onChange={e=>setCategory(e.target.value)}>
        <option value="">Все категории</option>
        <option value="individual">Физ. лица</option>
        <option value="nko">НКО</option>
        <option value="business">Бизнес</option>
      </select>
      <select className="input w-44" value={deadline} onChange={e=>setDeadline(e.target.value)}>
        <option value="">Любой срок</option>
        <option value="7">До 7 дней</option>
        <option value="30">До 30 дней</option>
        <option value="90">До 90 дней</option>
      </select>
      <Button onClick={apply}>Найти</Button>
      <Button variant="secondary" onClick={reset}>Сброс</Button>
    </div>
  );
}
""")

w('src/components/Wizard/StepIndicator.tsx', r"""import React from 'react';
const STEPS=['О заявителе','Проект','Бюджет','Документы','Проверка'];
export function StepIndicator({currentStep,onStepClick}:{currentStep:number;onStepClick?:(s:number)=>void}){
  return(
    <div className="flex items-center justify-between mb-8">
      {STEPS.map((label,idx)=>{
        const n=idx+1,done=n<currentStep,cur=n===currentStep;
        return(
          <React.Fragment key={n}>
            <div className="flex flex-col items-center gap-1 cursor-pointer" onClick={()=>onStepClick&&n<=currentStep&&onStepClick(n)}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${done?'bg-primary-600 text-white':cur?'bg-primary-600 text-white ring-4 ring-primary-100':'bg-gray-100 text-gray-400'}`}>{done?'v':n}</div>
              <span className={`text-xs hidden sm:block ${cur?'text-primary-600 font-medium':'text-gray-400'}`}>{label}</span>
            </div>
            {idx<STEPS.length-1&&<div className={`flex-1 h-0.5 mx-1 ${done?'bg-primary-600':'bg-gray-200'}`}/>}
          </React.Fragment>
        );
      })}
    </div>
  );
}
""")

w('src/components/Wizard/AIHintPanel.tsx', r"""import React from 'react';
interface P{hint:string|null;loading:boolean;onRefresh:()=>void;onClose:()=>void;fieldName:string;}
export function AIHintPanel({hint,loading,onRefresh,onClose,fieldName}:P){
  return(
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-purple-700">AI-подсказка</span>
        <div className="flex gap-1">
          <button onClick={onRefresh} className="p-1 hover:bg-purple-100 rounded text-purple-500 text-xs">refresh</button>
          <button onClick={onClose} className="p-1 hover:bg-purple-100 rounded text-purple-500">X</button>
        </div>
      </div>
      {loading
        ?<div className="space-y-2">{[80,70,60].map(pct=><div key={pct} className="h-3 bg-purple-100 rounded animate-pulse" style={{width:`${pct}%`}}/>)}</div>
        :hint
          ?<div className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">{hint}</div>
          :<p className="text-sm text-purple-400">Нажмите на поле для AI-подсказки</p>
      }
    </div>
  );
}
""")

w('src/components/Notifications/NotificationSettings.tsx', r"""import React,{useState} from 'react';
import { Button } from '../UI/Button';
import { useAuth } from '../../context/AuthContext';
import { authApi, notificationsApi } from '../../services/api';
import toast from 'react-hot-toast';
export function NotificationSettings(){
  const{user}=useAuth();
  const[saving,setSaving]=useState(false);
  const[emailNotify,setEmailNotify]=useState(user?.notify_email??true);
  const[telegramNotify,setTelegramNotify]=useState(user?.notify_telegram??false);
  const[code,setCode]=useState('');
  const save=async()=>{
    setSaving(true);
    try{await authApi.updateMe({notify_email:emailNotify,notify_telegram:telegramNotify});toast.success('Сохранено');}
    catch{toast.error('Ошибка');}
    finally{setSaving(false);}
  };
  const getCode=async()=>{
    try{const r=await notificationsApi.getTelegramCode();setCode(r.data.link_code);}
    catch{toast.error('Ошибка получения кода');}
  };
  return(
    <div className="space-y-4">
      <h2 className="font-semibold text-lg">Уведомления</h2>
      <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
        <input type="checkbox" checked={emailNotify} onChange={e=>setEmailNotify(e.target.checked)} className="w-4 h-4"/>
        <div><div className="font-medium">Email</div><div className="text-sm text-gray-500">{user?.email}</div></div>
      </label>
      <div className="p-3 bg-gray-50 rounded-lg space-y-2">
        <label className="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" checked={telegramNotify} onChange={e=>setTelegramNotify(e.target.checked)} className="w-4 h-4"/>
          <div className="font-medium">Telegram</div>
        </label>
        <Button size="sm" variant="secondary" onClick={getCode}>Получить код привязки</Button>
        {code&&<p className="text-sm">Код: <code className="bg-gray-200 px-1 rounded">{code}</code></p>}
      </div>
      <Button onClick={save} loading={saving}>Сохранить</Button>
    </div>
  );
}
""")

print("Components done!")
