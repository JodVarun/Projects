# 🏋️ FITFUEL — Your Personal Fitness Companion

<div align="center">

**A modern, dark-themed fitness tracking web application with OTP authentication, calorie tracking, diet planning, and AI-powered insights.**

[![React](https://img.shields.io/badge/React-18.3-61dafb?logo=react&logoColor=white)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.1-38bdf8?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Backend-3ecf8e?logo=supabase&logoColor=white)](https://supabase.com/)
[![Vite](https://img.shields.io/badge/Vite-6.3-646cff?logo=vite&logoColor=white)](https://vitejs.dev/)

</div>

---

## ✨ Features

### 🔐 Secure Authentication
- Phone number-based OTP login
- Session management with 30-day expiry
- Automatic fallback to local storage (works offline!)

### 🏠 Calorie Calculator
- Personalized daily calorie targets using the Mifflin-St Jeor equation
- Based on age, weight, height, and activity level
- Goal-based recommendations (lose / maintain / gain)

### 🍎 Diet Protocol
- Macro breakdown (Protein, Carbs, Fat) with visual pie chart
- Personalized meal plans by diet preference (Veg / Eggetarian / Non-veg)
- Foods to prefer/avoid guidance

### 💪 Training Matrix
- Calisthenics & weight training programs
- Exercise sets, reps, and cardio recommendations
- Recovery tips

### 📄 Medical Vault
- Upload and store medical reports
- AI-powered health insights and analysis

### 🤖 AI Chatbot
- Floating chat interface for instant fitness advice
- Personalized responses powered by Gemini AI

---

## 🎨 Design

| Property | Value |
|----------|-------|
| **Theme** | Dark mode with neon accents |
| **Primary Color** | Neon Green `#ccff00` |
| **Background** | Near-black `#050505` |
| **Style** | Modern, minimal, futuristic |
| **Responsive** | Desktop & Mobile |

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (or Bun)

### Installation

```bash
# Clone the repository
git clone https://github.com/JodVarun/Projects.git
cd Projects/Web-Apps/FitFuel

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and start tracking!

---

## 📁 Project Structure

```
FitFuel/
├── src/
│   ├── app/
│   │   ├── components/         # React components
│   │   │   ├── HomeTab.tsx     # Calorie calculator
│   │   │   ├── DietTab.tsx     # Diet planning
│   │   │   ├── WorkoutTab.tsx  # Training programs
│   │   │   ├── ReportsTab.tsx  # Medical vault
│   │   │   ├── AIChatBot.tsx   # AI chatbot
│   │   │   └── ui/            # Reusable UI components (Radix)
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── context/           # App-wide state
│   │   └── services/          # Firebase & Gemini
│   └── styles/                # CSS, theme, fonts
├── supabase/functions/        # Edge functions (backend)
├── utils/                     # Supabase config
├── package.json
└── vite.config.ts
```

---

## 🔌 Tech Stack

### Frontend
| Tech | Purpose |
|------|---------|
| **React 18** | UI library |
| **TypeScript** | Type safety |
| **React Router 7** | Navigation |
| **Tailwind CSS 4** | Styling |
| **Recharts** | Data visualization |
| **Radix UI** | Accessible component primitives |
| **Lucide React** | Icons |
| **Motion** | Animations |

### Backend
| Tech | Purpose |
|------|---------|
| **Supabase** | Backend as a Service |
| **Firebase** | Authentication |
| **Gemini AI** | AI chatbot & insights |
| **Deno** | Edge runtime |

### Build Tools
| Tech | Purpose |
|------|---------|
| **Vite** | Build tool |
| **PostCSS** | CSS processing |

---

## 🔐 Authentication Flow

```
User enters phone number
    → Backend generates 6-digit OTP (10 min expiry)
    → OTP sent via SMS (or shown on screen in test mode)
    → User enters OTP → Backend verifies
    → Session token created (30-day expiry)
    → User logged in ✓
```

---

## 🗄️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send-otp` | Send OTP to phone |
| POST | `/verify-otp` | Verify OTP & login |
| GET | `/user/:phone` | Get user profile |
| POST | `/user/:phone/profile` | Update profile |
| POST | `/user/:phone/workout` | Save workout |
| GET | `/user/:phone/workouts` | Get workout history |

---

## 🚀 Deployment

**Frontend** — Deploy to Vercel or Netlify:
```bash
vercel
# or
netlify deploy
```

**Backend** — Runs on Supabase Edge Functions (already deployed).

---

## 📄 License

This is a demo/prototype application. For production use, ensure GDPR/CCPA compliance and implement proper security measures.

---

<div align="center">

**FITFUEL — Transform Your Fitness Journey** 💪

Made by <a href="https://github.com/JodVarun">@JodVarun</a>

</div>
