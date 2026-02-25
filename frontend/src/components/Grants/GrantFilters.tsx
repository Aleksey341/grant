import React,{useState} from 'react';
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
