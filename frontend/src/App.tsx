import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Auth from './pages/Auth'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Lessons from './pages/Lessons'
import LessonDetail from './pages/LessonDetail'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/lessons" element={<Lessons />} />
        <Route path="/lessons/:id" element={<LessonDetail />} />
        {/* Placeholder routes - to be implemented */}
        <Route path="/practice" element={<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50"><div className="text-center"><h1 className="text-4xl font-bold text-gray-900 mb-4" style={{fontFamily: "'Baloo 2', cursive"}}>Practice Page</h1><p className="text-gray-600" style={{fontFamily: "'Comic Neue', cursive"}}>Coming soon...</p></div></div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
