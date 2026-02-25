import React from 'react';
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
