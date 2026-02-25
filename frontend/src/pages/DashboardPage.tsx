import React,{useState} from 'react';
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
