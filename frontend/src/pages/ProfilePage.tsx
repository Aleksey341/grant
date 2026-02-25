import React,{useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';
import { NotificationSettings } from '../components/Notifications/NotificationSettings';
import { Button } from '../components/UI/Button';
import toast from 'react-hot-toast';

export function ProfilePage(){
  const{user,logout}=useAuth();
  const nav=useNavigate();
  const[name,setName]=useState(user?.full_name||'');
  const[saving,setSaving]=useState(false);

  const save=async()=>{
    setSaving(true);
    try{await authApi.updateMe({full_name:name});toast.success('Сохранено');}
    catch{toast.error('Ошибка');}finally{setSaving(false);}
  };

  return(
    <div className="max-w-2xl mx-auto px-4 py-8">
      <Button variant="ghost" size="sm" onClick={()=>nav('/dashboard')} className="mb-6">К каталогу</Button>
      <h1 className="text-2xl font-bold mb-8">Профиль</h1>
      <div className="space-y-6">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
          <h2 className="font-semibold text-lg">Личные данные</h2>
          <div><label className="label">Email</label><input className="input bg-gray-50" value={user?.email||''} readOnly/></div>
          <div><label className="label">Имя</label><input className="input" value={name} onChange={e=>setName(e.target.value)}/></div>
          <Button onClick={save} loading={saving}>Сохранить</Button>
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <NotificationSettings/>
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h2 className="font-semibold text-lg text-red-600 mb-4">Выход</h2>
          <Button variant="danger" onClick={()=>{logout();nav('/');}}>Выйти из аккаунта</Button>
        </div>
      </div>
    </div>
  );
}
