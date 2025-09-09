#FRONT END
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './state/AuthContext'
import './styles.css'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import React, { createContext, useContext, useEffect, useState } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [tokens, setTokens] = useState(() => {
    const raw = localStorage.getItem('tokens')
    return raw ? JSON.parse(raw) : null
  })

  useEffect(() => {
    if (tokens) {
      localStorage.setItem('tokens', JSON.stringify(tokens))
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`
      axios.get(`${API}/api/me/`).then(res => setUser(res.data)).catch(() => setUser(null))
    } else {
      localStorage.removeItem('tokens')
      delete axios.defaults.headers.common['Authorization']
      setUser(null)
    }
  }, [tokens])

  const login = async (username, password) => {
    const res = await axios.post(`${API}/api/token/`, { username, password })
    setTokens(res.data)
  }

  const refresh = async () => {
    if (!tokens) return
    const res = await axios.post(`${API}/api/token/refresh/`, { refresh: tokens.refresh })
    setTokens({ ...tokens, access: res.data.access })
  }

  const logout = () => setTokens(null)

  const value = { user, tokens, setTokens, login, logout, refresh, API }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 }
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
)

#CSS
* { box-sizing: border-box; }
body { font-family: system-ui, Arial, sans-serif; margin: 0; color: #111; }
.container { max-width: 900px; margin: 0 auto; padding: 1rem; }
nav { display:flex; gap:1rem; padding: 1rem; border-bottom: 1px solid #eee; align-items:center; }
a { text-decoration: none; color: #0366d6; }
.btn { padding: .5rem .8rem; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9; cursor:pointer;}
.btn.primary { background:#0366d6; color:#fff; border-color:#0366d6; }
input, textarea { width: 100%; padding:.6rem; border:1px solid #ddd; border-radius:8px; margin:.4rem 0; }
.card { border:1px solid #eee; padding:1rem; border-radius:12px; margin:.6rem 0; background:#fff; }
.pagination { display:flex; gap:.5rem; margin-top:1rem; }
.tag { font-size:.85rem; color:#555; }


#BACK END

from pathlib import Path
from datetime import timedelta
import o
import os
from django.core.asgi import get_asgi_application
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from blog.views import MeView
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_wsgi_application()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('blog.urls')),
    path('api/me/', MeView.as_view(), name='me'),
]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_asgi_application()


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'dev-insecure-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'blog',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
