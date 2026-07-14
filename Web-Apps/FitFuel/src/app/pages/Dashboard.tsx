import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { Home, FileText, Utensils, Dumbbell, MessageCircle, LogOut, X } from "lucide-react";
import HomeTab from "../components/HomeTab";
import ReportsTab from "../components/ReportsTab";
import DietTab from "../components/DietTab";
import WorkoutTab from "../components/WorkoutTab";
import AIChatBot from "../components/AIChatBot";
import { AppContextProvider, useAppContext } from "../context/AppContext";

type Tab = "home" | "reports" | "diet" | "workout";

function DashboardContent() {
  const navigate = useNavigate();
  const { user, setUser, setUserProfile } = useAppContext();
  const [activeTab, setActiveTab] = useState<Tab>("home");
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    const sessionToken = localStorage.getItem("sessionToken");
    const userData = localStorage.getItem("user");

    if (!sessionToken || !userData) {
      navigate("/");
      return;
    }

    const parsed = JSON.parse(userData);
    setUser(parsed);
    if (parsed.profile) {
      setUserProfile({
        name: parsed.name,
        phoneNumber: parsed.phoneNumber,
        ...parsed.profile,
      });
    } else {
      setUserProfile({
        name: parsed.name,
        phoneNumber: parsed.phoneNumber,
        goal: null,
        gender: null,
        age: null,
        height: null,
        weight: null,
        activityLevel: null,
        dailyCalories: null,
      });
    }
  }, [navigate, setUser, setUserProfile]);

  const handleLogout = () => {
    localStorage.removeItem("sessionToken");
    localStorage.removeItem("user");
    navigate("/");
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#050505] flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[#0a0a0a] border-r border-gray-800 flex flex-col fixed h-screen">
        {/* Logo */}
        <div className="p-8 border-b border-gray-800">
          <h1 className="text-3xl font-bold">
            <span className="text-white">FIT</span>
            <span className="text-[#ccff00]">FUEL</span>
            <span className="text-white">.</span>
          </h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          <button
            onClick={() => setActiveTab("home")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
              activeTab === "home"
                ? "bg-[#ccff00] text-black"
                : "text-gray-400 hover:text-white hover:bg-[#18181b]"
            }`}
          >
            <Home className="w-5 h-5" />
            Home
          </button>

          <button
            onClick={() => setActiveTab("reports")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
              activeTab === "reports"
                ? "bg-[#ccff00] text-black"
                : "text-gray-400 hover:text-white hover:bg-[#18181b]"
            }`}
          >
            <FileText className="w-5 h-5" />
            Reports
          </button>

          <button
            onClick={() => setActiveTab("diet")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
              activeTab === "diet"
                ? "bg-[#ccff00] text-black"
                : "text-gray-400 hover:text-white hover:bg-[#18181b]"
            }`}
          >
            <Utensils className="w-5 h-5" />
            Diet
          </button>

          <button
            onClick={() => setActiveTab("workout")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
              activeTab === "workout"
                ? "bg-[#ccff00] text-black"
                : "text-gray-400 hover:text-white hover:bg-[#18181b]"
            }`}
          >
            <Dumbbell className="w-5 h-5" />
            Workout
          </button>
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-8">
          {/* Welcome Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">
              Welcome back, {user.name}! 👋
            </h2>
            <p className="text-gray-400">
              Track your fitness journey and achieve your goals
            </p>
          </div>

          {/* Tab Content */}
          {activeTab === "home" && <HomeTab />}
          {activeTab === "reports" && <ReportsTab />}
          {activeTab === "diet" && <DietTab />}
          {activeTab === "workout" && <WorkoutTab />}
        </div>
      </main>

      {/* AI Chat Button */}
      <button
        onClick={() => setChatOpen(!chatOpen)}
        className="fixed bottom-8 right-8 w-16 h-16 bg-[#ccff00] hover:bg-[#b8e600] rounded-full shadow-2xl flex items-center justify-center transition-all hover:scale-110 z-50"
      >
        {chatOpen ? (
          <X className="w-7 h-7 text-black" />
        ) : (
          <MessageCircle className="w-7 h-7 text-black" />
        )}
      </button>

      {/* AI Chat Window */}
      {chatOpen && <AIChatBot onClose={() => setChatOpen(false)} />}
    </div>
  );
}

export default function Dashboard() {
  return (
    <AppContextProvider>
      <DashboardContent />
    </AppContextProvider>
  );
}
