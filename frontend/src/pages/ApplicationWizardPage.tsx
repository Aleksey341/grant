import React,{useState,useEffect,useRef} from 'react';
import { useParams,useNavigate } from 'react-router-dom';
import { applicationsApi,grantsApi,documentsApi,aiApi } from '../services/api';
import { Application,Grant } from '../types';
import { StepIndicator } from '../components/Wizard/StepIndicator';
import { AIHintPanel } from '../components/Wizard/AIHintPanel';
import { Button } from '../components/UI/Button';
import toast from 'react-hot-toast';

export function ApplicationWizardPage(){
  const{id}=useParams<{id:string}>();
  const nav=useNavigate();
  const[app,setApp]=useState<Application|null>(null);
  const[grant,setGrant]=useState<Grant|null>(null);
  const[step,setStep]=useState(1);
  const[data,setData]=useState<Record<string,any>>({});
  const[hint,setHint]=useState<string|null>(null);
  const[hintLoading,setHintLoading]=useState(false);
  const[activeField,setActiveField]=useState<string|null>(null);
  const[showHint,setShowHint]=useState(false);
  const autoSaveRef=useRef<any>();

  useEffect(()=>{
    if(!id)return;
    applicationsApi.get(parseInt(id)).then(r=>{
      setApp(r.data);setStep(r.data.current_step);setData(r.data.wizard_data||{});
      return grantsApi.get(r.data.grant_id);
    }).then(r=>setGrant(r.data));
  },[id]);

  useEffect(()=>{
    autoSaveRef.current=setInterval(save,30000);
    return()=>clearInterval(autoSaveRef.current);
  },[data,step]);

  const save=async()=>{
    if(!app)return;
    try{await applicationsApi.update(app.id,{wizard_data:data,current_step:step});}catch{}
  };

  const upd=(key:string,val:any)=>{
    setData(p=>({...p,[`step${step}`]:{...(p[`step${step}`]||{}),[key]:val}}));
  };

  const stepData=data[`step${step}`]||{};

  const getHint=async(field:string)=>{
    if(!app||!grant)return;
    setHintLoading(true);setShowHint(true);setActiveField(field);
    try{
      const r=await aiApi.hint({application_id:app.id,field_name:field,current_value:stepData[field]||'',grant_id:grant.id});
      setHint(r.data.hint);
    }catch{setHint('AI недоступен. Проверьте ANTHROPIC_API_KEY.');}
    finally{setHintLoading(false);}
  };

  const next=async()=>{await save();if(step<5)setStep(s=>s+1);};
  const prev=()=>{if(step>1)setStep(s=>s-1);};

  const download=async(type:'pdf'|'docx')=>{
    if(!app)return;
    try{
      await save();
      if(type==='pdf')await documentsApi.generatePdf(app.id);
      else await documentsApi.generateDocx(app.id);
      window.open(documentsApi.downloadUrl(app.id,type),'_blank');
      toast.success(`${type.toUpperCase()} готов!`);
    }catch{toast.error('Ошибка генерации документа');}
  };

  if(!app)return <div className="max-w-5xl mx-auto px-4 py-8"><div className="animate-pulse h-96 bg-gray-100 rounded-xl"/></div>;

  return(
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Button variant="ghost" size="sm" onClick={()=>nav(-1)}>Назад</Button>
        <div>
          <h1 className="text-xl font-bold">Заявка #{app.id}</h1>
          {grant&&<p className="text-sm text-gray-500">{grant.source_name}</p>}
        </div>
      </div>
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <StepIndicator currentStep={step} onStepClick={setStep}/>
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
            {step===1&&<Step1 data={stepData} upd={upd} hint={getHint}/>}
            {step===2&&<Step2 data={stepData} upd={upd} hint={getHint} grant={grant} appId={app.id}/>}
            {step===3&&<Step3 data={stepData} upd={upd}/>}
            {step===4&&<Step4 data={stepData} upd={upd} grant={grant}/>}
            {step===5&&<Step5 data={data} grant={grant} onDownload={download}/>}
            <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
              <Button variant="secondary" onClick={prev} disabled={step===1}>Назад</Button>
              {step<5?<Button onClick={next}>Далее</Button>:<Button variant="secondary" onClick={save}>Сохранить</Button>}
            </div>
          </div>
        </div>
        <div className="space-y-4">
          {showHint
            ?<AIHintPanel hint={hint} loading={hintLoading} onRefresh={()=>activeField&&getHint(activeField)} onClose={()=>setShowHint(false)} fieldName={activeField||''}/>
            :<div className="bg-purple-50 border border-purple-100 rounded-xl p-4 text-center"><p className="text-3xl mb-2">AI</p><p className="text-sm text-purple-600 font-medium">Нажмите на поле</p><p className="text-xs text-purple-400">для AI-подсказки Claude</p></div>
          }
          {grant&&(
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-xs space-y-1">
              <p className="font-semibold text-blue-700 mb-2">Требования</p>
              {grant.who_can_apply&&<p><b>Кто:</b> {grant.who_can_apply}</p>}
              {grant.max_amount_text&&<p><b>Сумма:</b> {grant.max_amount_text}</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function F({label,name,value,upd,hint,type='text',multi=false,ph=''}:any){
  return(
    <div>
      <label className="label">{label}</label>
      {multi
        ?<textarea className="input min-h-[90px] resize-y" value={value||''} onChange={e=>upd(name,e.target.value)} onFocus={()=>hint&&hint(name)} placeholder={ph}/>
        :<input className="input" type={type} value={value||''} onChange={e=>upd(name,e.target.value)} onFocus={()=>hint&&hint(name)} placeholder={ph}/>
      }
    </div>
  );
}

function Step1({data,upd,hint}:any){
  return(
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">1. О заявителе</h2>
      <div className="grid sm:grid-cols-2 gap-4">
        <F label="ФИО *" name="full_name" value={data.full_name} upd={upd} hint={hint} ph="Иванов Иван Иванович"/>
        <F label="Возраст" name="age" value={data.age} upd={upd} hint={hint} type="number" ph="25"/>
        <F label="Организация" name="organization" value={data.organization} upd={upd} hint={hint}/>
        <F label="ИНН" name="inn" value={data.inn} upd={upd} hint={hint}/>
        <F label="ОГРН" name="ogrn" value={data.ogrn} upd={upd} hint={hint}/>
        <F label="Регион" name="region" value={data.region} upd={upd} hint={hint} ph="Москва"/>
        <F label="Email" name="email" value={data.email} upd={upd} hint={hint} type="email"/>
        <F label="Телефон" name="phone" value={data.phone} upd={upd} hint={hint} ph="+7 (999) 000-00-00"/>
      </div>
    </div>
  );
}

function Step2({data,upd,hint,grant,appId}:any){
  const[gen,setGen]=useState(false);
  const generate=async()=>{
    setGen(true);
    try{
      const r=await aiApi.generateSection({section_name:'Описание проекта',project_topic:data.project_name||'Проект',target_audience:data.target_audience||'Широкая аудитория',applicant_data:data,grant_id:grant?.id||1});
      upd('description',r.data.text);
      toast.success('AI написал описание!');
    }catch{toast.error('Ошибка AI');}finally{setGen(false);}
  };
  return(
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">2. Проект</h2>
      <F label="Название проекта *" name="project_name" value={data.project_name} upd={upd} hint={hint} ph="Название проекта"/>
      <F label="Целевая аудитория" name="target_audience" value={data.target_audience} upd={upd} hint={hint}/>
      <div>
        <div className="flex justify-between mb-1">
          <label className="label mb-0">Описание *</label>
          <Button size="sm" variant="ghost" onClick={generate} loading={gen}>AI: написать</Button>
        </div>
        <textarea className="input min-h-[120px] resize-y" value={data.description||''} onChange={e=>upd('description',e.target.value)} onFocus={()=>hint('description')}/>
      </div>
      <F label="Цели" name="goals" value={data.goals} upd={upd} hint={hint} multi ph="1. Цель..."/>
      <F label="Ожидаемые результаты" name="expected_results" value={data.expected_results} upd={upd} hint={hint} multi/>
    </div>
  );
}

function Step3({data,upd}:any){
  const items:any[]=data.items||[];
  const addItem=()=>upd('items',[...items,{category:'',description:'',amount:''}]);
  const updItem=(i:number,f:string,v:any)=>{const a=[...items];a[i]={...a[i],[f]:v};upd('items',a);};
  const del=(i:number)=>upd('items',items.filter((_:any,j:number)=>j!==i));
  const total=items.reduce((s:number,i:any)=>s+(parseFloat(i.amount)||0),0);
  return(
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">3. Бюджет</h2>
      {items.map((item:any,i:number)=>(
        <div key={i} className="flex gap-2">
          <input className="input flex-1" placeholder="Категория" value={item.category} onChange={e=>updItem(i,'category',e.target.value)}/>
          <input className="input flex-2" placeholder="Описание" value={item.description} onChange={e=>updItem(i,'description',e.target.value)}/>
          <input className="input w-28" type="number" placeholder="Сумма" value={item.amount} onChange={e=>updItem(i,'amount',e.target.value)}/>
          <button onClick={()=>del(i)} className="text-red-400 hover:text-red-600 px-2">X</button>
        </div>
      ))}
      <Button variant="secondary" size="sm" onClick={addItem}>+ Статья</Button>
      {items.length>0&&<div className="bg-gray-50 rounded p-3 text-right font-semibold">Итого: {total.toLocaleString('ru-RU')} руб.</div>}
    </div>
  );
}

function Step4({data,upd,grant}:any){
  const docs=(grant?.typical_docs||'Паспорт,ИНН,СНИЛС,Описание проекта,Смета').split(/[,;\n]/).map((d:string)=>d.trim()).filter(Boolean);
  return(
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">4. Документы</h2>
      {docs.map((doc:string,i:number)=>(
        <label key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
          <input type="checkbox" checked={data[`doc_${i}`]||false} onChange={e=>upd(`doc_${i}`,e.target.checked)} className="w-4 h-4"/>
          <span className="text-sm">{doc}</span>
        </label>
      ))}
    </div>
  );
}

function Step5({data,grant,onDownload}:any){
  const s1=data.step1||{},s2=data.step2||{},s3=data.step3||{};
  const total=(s3.items||[]).reduce((s:number,i:any)=>s+(parseFloat(i.amount)||0),0);
  return(
    <div className="space-y-5">
      <h2 className="text-lg font-semibold">5. Проверка и экспорт</h2>
      <div className="bg-gray-50 rounded-xl p-4 text-sm space-y-1">
        <p><b>Грант:</b> {grant?.source_name||'—'}</p>
        <p><b>Заявитель:</b> {s1.full_name||'—'}</p>
        <p><b>Email:</b> {s1.email||'—'}</p>
        <p><b>Проект:</b> {s2.project_name||'—'}</p>
        {total>0&&<p><b>Бюджет:</b> {total.toLocaleString('ru-RU')} руб.</p>}
      </div>
      <div className="flex gap-3">
        <Button size="lg" onClick={()=>onDownload('pdf')}>Скачать PDF</Button>
        <Button variant="secondary" size="lg" onClick={()=>onDownload('docx')}>Скачать DOCX</Button>
      </div>
    </div>
  );
}
