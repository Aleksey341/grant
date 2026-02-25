import React from 'react';
interface BP extends React.ButtonHTMLAttributes<HTMLButtonElement> { variant?:'primary'|'secondary'|'danger'|'ghost'; size?:'sm'|'md'|'lg'; loading?:boolean; leftIcon?:React.ReactNode; }
export function Button({children,variant='primary',size='md',loading=false,leftIcon,className='',disabled,...p}:BP) {
  const v={primary:'bg-primary-600 text-white hover:bg-primary-700',secondary:'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',danger:'bg-red-600 text-white hover:bg-red-700',ghost:'text-gray-600 hover:bg-gray-100'};
  const s={sm:'px-3 py-1.5 text-sm',md:'px-4 py-2',lg:'px-6 py-3 text-lg'};
  return <button className={`inline-flex items-center gap-2 font-medium rounded-lg transition-colors focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed ${v[variant]} ${s[size]} ${className}`} disabled={disabled||loading} {...p}>{loading?<span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"/>:leftIcon}{children}</button>;
}
