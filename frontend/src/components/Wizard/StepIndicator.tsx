import React from 'react';
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
