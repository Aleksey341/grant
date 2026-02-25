import React,{useState} from 'react';
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
