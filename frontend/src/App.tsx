import React from 'react';
import { BrowserRouter,Routes,Route,Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider,useAuth } from './context/AuthContext';
import { HomePage } from './pages/HomePage';
import { DashboardPage } from './pages/DashboardPage';
import { GrantDetailPage } from './pages/GrantDetailPage';
import { ApplicationWizardPage } from './pages/ApplicationWizardPage';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminPage } from './pages/AdminPage';

function Protected({children}:{children:React.ReactNode}){
  const{user,isLoading}=useAuth();
  if(isLoading)return <div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"/></div>;
  if(!user)return <Navigate to="/" replace/>;
  return <>{children}</>;
}
function Admin({children}:{children:React.ReactNode}){
  const{user}=useAuth();
  if(!user?.is_admin)return <Navigate to="/dashboard" replace/>;
  return <>{children}</>;
}
function AppRoutes(){
  return(
    <Routes>
      <Route path="/" element={<HomePage/>}/>
      <Route path="/dashboard" element={<Protected><DashboardPage/></Protected>}/>
      <Route path="/grants/:id" element={<Protected><GrantDetailPage/></Protected>}/>
      <Route path="/applications" element={<Protected><ApplicationsPage/></Protected>}/>
      <Route path="/applications/:id" element={<Protected><ApplicationWizardPage/></Protected>}/>
      <Route path="/profile" element={<Protected><ProfilePage/></Protected>}/>
      <Route path="/admin" element={<Protected><Admin><AdminPage/></Admin></Protected>}/>
      <Route path="*" element={<Navigate to="/" replace/>}/>
    </Routes>
  );
}
export default function App(){
  return(
    <BrowserRouter basename="/grant">
      <AuthProvider>
        <AppRoutes/>
        <Toaster position="top-right"/>
      </AuthProvider>
    </BrowserRouter>
  );
}
