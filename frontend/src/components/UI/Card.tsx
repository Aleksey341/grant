import React from 'react';
interface CP{children:React.ReactNode;className?:string;onClick?:()=>void;}
export function Card({children,className='',onClick}:CP){return <div className={`bg-white rounded-xl shadow-sm border border-gray-100 ${onClick?'cursor-pointer hover:shadow-md transition-shadow':''} ${className}`} onClick={onClick}>{children}</div>;}
