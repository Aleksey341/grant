import React,{useState} from 'react';
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
