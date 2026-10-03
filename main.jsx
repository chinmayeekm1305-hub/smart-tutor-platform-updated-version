import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './index.css'
import { AuthProvider, useAuth } from './auth'
import Layout from './components/Layout'
import Login from './pages/Login'
import StudentDashboard from './pages/student/Dashboard'
import Learn from './pages/student/Learn'
import TopicPage from './pages/student/Topic'
import Quiz from './pages/student/Quiz'
import QuizResult from './pages/student/QuizResult'
import Tutor from './pages/student/Tutor'
import Progress from './pages/student/Progress'
import Overview from './pages/teacher/Overview'
import StudentDetail from './pages/teacher/StudentDetail'
import QuestionBank from './pages/teacher/QuestionBank'
import Content from './pages/teacher/Content'
import Doubts from './pages/teacher/Doubts'
import ModelInfo from './pages/teacher/ModelInfo'

function Protected({ role, children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to={`/${user.role}`} replace />
  return children
}

function Home() {
  const { user } = useAuth()
  return <Navigate to={user ? `/${user.role}` : '/login'} replace />
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/student" element={<Protected role="student"><Layout /></Protected>}>
            <Route index element={<StudentDashboard />} />
            <Route path="learn" element={<Learn />} />
            <Route path="topic/:id" element={<TopicPage />} />
            <Route path="quiz/:topicId" element={<Quiz />} />
            <Route path="result/:sessionId" element={<QuizResult />} />
            <Route path="tutor" element={<Tutor />} />
            <Route path="progress" element={<Progress />} />
          </Route>
          <Route path="/teacher" element={<Protected role="teacher"><Layout /></Protected>}>
            <Route index element={<Overview />} />
            <Route path="students/:id" element={<StudentDetail />} />
            <Route path="questions" element={<QuestionBank />} />
            <Route path="content" element={<Content />} />
            <Route path="doubts" element={<Doubts />} />
            <Route path="model" element={<ModelInfo />} />
          </Route>
          <Route path="*" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
)
