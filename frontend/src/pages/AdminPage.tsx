import React,{useEffect,useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { adminApi } from '../services/api';
import { Button } from '../components/UI/Button';
import toast from 'react-hot-toast';

export function AdminPage(){
  const nav=useNavigate();
  const[stats,setStats]=useState<any>(null);
  const[users,setUsers]=useState<any[]>([]);
  const[scraping,setScraping]=useState(false);
  const[results,setResults]=useState<any[]>([]);

  useEffect(()=>{
    adminApi.stats().then(r=>setStats(r.data));
    adminApi.users().then(r=>setUsers(r.data));
  },[]);

  const runScrape=async()=>{
    setScraping(true);
    try{
      await adminApi.runScrape();
      toast.success('Парсинг запущен...');
      const interval=setInterval(async()=>{
        const r=await adminApi.scrapeStatus();
        setResults(r.data.results||[]);
        if(!r.data.running){clearInterval(interval);setScraping(false);toast.success('Парсинг завершён');}
      },2000);
    }catch{toast.error('Ошибка');setScraping(false);}
  };

  return(
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Button variant="ghost" size="sm" onClick={()=>nav('/dashboard')} className="mb-6">К каталогу</Button>
      <h1 className="text-2xl font-bold mb-8">Администратор</h1>
      {stats&&(
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[['Грантов',stats.grants],['Пользователей',stats.users],['Заявок',stats.applications],['Уведомлений',stats.notifications_sent]].map(([l,v])=>(
            <div key={String(l)} className="bg-white rounded-xl border border-gray-100 p-4 text-center">
              <div className="text-2xl font-bold">{v}</div>
              <div className="text-sm text-gray-500">{l}</div>
            </div>
          ))}
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h2 className="font-semibold text-lg mb-3">Парсинг грантов</h2>
          <p className="text-sm text-gray-500 mb-4">Обновление данных всех грантов (httpx + Playwright + Claude AI)</p>
          <Button onClick={runScrape} loading={scraping}>{scraping?'Парсинг...':'Запустить парсинг'}</Button>
          {results.length>0&&(
            <div className="mt-4 text-xs space-y-1">
              {results.slice(-5).map((r:any,i:number)=>(
                <div key={i} className={r.success?'text-green-600':'text-red-500'}>{r.success?'OK':'ERR'} {r.grant}</div>
              ))}
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h2 className="font-semibold text-lg mb-3">Пользователи ({users.length})</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {users.map((u:any)=>(
              <div key={u.id} className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-medium">{u.email}</span>
                  {u.is_admin&&<span className="ml-2 text-xs bg-blue-100 text-blue-700 px-1 rounded">admin</span>}
                </div>
                <span className="text-gray-400 text-xs">{new Date(u.created_at).toLocaleDateString('ru-RU')}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
