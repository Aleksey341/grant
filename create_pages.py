import os

BASE = "C:/Users/cobra/grants-assistant/frontend"

def w(rel, content):
    full = os.path.join(BASE, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'OK: {rel}')

w('src/pages/HomePage.tsx', r"""import React,{useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/UI/Button';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export function HomePage(){
  const nav=useNavigate();
  const{login,register,user}=useAuth();
  const[mode,setMode]=useState<'login'|'register'>('login');
  const[email,setEmail]=useState('');
  const[password,setPassword]=useState('');
  const[name,setName]=useState('');
  const[loading,setLoading]=useState(false);

  if(user){nav('/dashboard');return null;}

  const submit=async(e:React.FormEvent)=>{
    e.preventDefault();setLoading(true);
    try{
      if(mode==='login')await login(email,password);
      else await register(email,password,name);
      nav('/dashboard');
      toast.success(mode==='login'?'Добро пожаловать!':'Аккаунт создан!');
    }catch(e:any){toast.error(e.response?.data?.detail||'Ошибка входа');}
    finally{setLoading(false);}
  };

  return(
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl grid lg:grid-cols-2 gap-12 items-center">
        <div className="text-white">
          <h1 className="text-4xl font-bold mb-4">GrantsAssistant</h1>
          <p className="text-blue-100 text-lg mb-6">Система управления грантами с AI-ассистентом</p>
          <div className="space-y-3 text-blue-200">
            <p>Отслеживание дедлайнов + Email/Telegram/Push уведомления</p>
            <p>AI-помощник (Claude) для заполнения заявок</p>
            <p>Генерация PDF и Word документов</p>
            <p>10 грантов в базе из Excel</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-2xl">
          <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
            {(['login','register'] as const).map(m=>(
              <button key={m} onClick={()=>setMode(m)}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${mode===m?'bg-white shadow-sm text-gray-900':'text-gray-500'}`}>
                {m==='login'?'Войти':'Регистрация'}
              </button>
            ))}
          </div>
          <form onSubmit={submit} className="space-y-4">
            {mode==='register'&&(
              <div><label className="label">Имя</label><input className="input" placeholder="Иван Иванов" value={name} onChange={e=>setName(e.target.value)}/></div>
            )}
            <div><label className="label">Email</label><input className="input" type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></div>
            <div><label className="label">Пароль</label><input className="input" type="password" required minLength={6} value={password} onChange={e=>setPassword(e.target.value)}/></div>
            <Button type="submit" className="w-full justify-center" loading={loading}>
              {mode==='login'?'Войти':'Создать аккаунт'}
            </Button>
          </form>
          <p className="text-center text-xs text-gray-400 mt-4">Демо: admin@grants.local / admin123</p>
        </div>
      </div>
    </div>
  );
}
""")

w('src/pages/DashboardPage.tsx', r"""import React,{useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useGrants } from '../hooks/useGrants';
import { GrantCard } from '../components/Grants/GrantCard';
import { GrantFilters } from '../components/Grants/GrantFilters';
import { Button } from '../components/UI/Button';

export function DashboardPage(){
  const{user,logout}=useAuth();
  const nav=useNavigate();
  const[filters,setFilters]=useState({});
  const{grants,loading}=useGrants(filters);
  return(
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <span className="font-bold text-gray-900 text-lg">GrantsAssistant</span>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={()=>nav('/applications')}>Заявки</Button>
            {user?.is_admin&&<Button variant="ghost" size="sm" onClick={()=>nav('/admin')}>Админ</Button>}
            <Button variant="ghost" size="sm" onClick={()=>nav('/profile')}>Профиль</Button>
            <Button variant="ghost" size="sm" onClick={()=>{logout();nav('/');}}>Выход</Button>
          </div>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Каталог грантов</h1>
          <span className="text-sm text-gray-400">{grants.length} грантов</span>
        </div>
        <div className="mb-6"><GrantFilters onFilter={setFilters}/></div>
        {loading?(
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1,2,3,4,5,6].map(i=><div key={i} className="h-40 bg-white rounded-xl border border-gray-100 animate-pulse"/>)}
          </div>
        ):grants.length===0?(
          <div className="text-center py-16 text-gray-400">
            <p className="text-5xl mb-4">search</p>
            <p className="text-lg font-medium">Гранты не найдены</p>
            <p className="text-sm">Измените фильтры или сбросьте поиск</p>
          </div>
        ):(
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {grants.map(g=><GrantCard key={g.id} grant={g}/>)}
          </div>
        )}
      </main>
    </div>
  );
}
""")

w('src/pages/GrantDetailPage.tsx', r"""import React,{useEffect,useState} from 'react';
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
""")

print("Homepage, Dashboard, GrantDetail done")
