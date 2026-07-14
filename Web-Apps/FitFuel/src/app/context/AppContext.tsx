import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

// ---- Types ----

export interface UserProfile {
  name: string;
  phoneNumber: string;
  goal: string | null;
  gender: string | null;
  age: number | null;
  height: number | null;
  weight: number | null;
  activityLevel: string | null;
  dailyCalories: number | null;
}

export interface MealItem {
  name: string;
  quantity: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface MealPlan {
  breakfast: MealItem[];
  lunch: MealItem[];
  snacks: MealItem[];
  dinner: MealItem[];
}

export interface Macros {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface WorkoutExercise {
  name: string;
  sets: number;
  reps: string;
  category: string;
  notes?: string;
}

export interface WorkoutPlan {
  exercises: WorkoutExercise[];
  cardio: string[];
  recovery: string[];
  notes: string;
}

export interface AppContextType {
  // User
  user: any;
  setUser: (u: any) => void;
  userProfile: UserProfile | null;
  setUserProfile: (p: UserProfile | null) => void;

  // Reports
  reportData: string;
  setReportData: (d: string) => void;
  reportFileName: string;
  setReportFileName: (n: string) => void;

  // Diet
  mealPlan: MealPlan | null;
  setMealPlan: (p: MealPlan | null) => void;
  updateMealPlan: (plan: MealPlan) => void;
  macros: Macros;
  setMacros: (m: Macros) => void;
  dietPreference: string;
  setDietPreference: (p: string) => void;

  // Workout
  workoutPlan: WorkoutPlan | null;
  setWorkoutPlan: (p: WorkoutPlan | null) => void;

  // Flags
  isGeneratingDiet: boolean;
  setIsGeneratingDiet: (f: boolean) => void;
  isGeneratingWorkout: boolean;
  setIsGeneratingWorkout: (f: boolean) => void;
}

const AppContext = createContext<AppContextType | null>(null);

export function AppContextProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<any>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [reportData, setReportData] = useState("");
  const [reportFileName, setReportFileName] = useState("");
  const [mealPlan, setMealPlanState] = useState<MealPlan | null>(null);
  const [macros, setMacros] = useState<Macros>({ calories: 2200, protein: 165, carbs: 220, fat: 73 });
  const [dietPreference, setDietPreference] = useState("vegetarian");
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null);
  const [isGeneratingDiet, setIsGeneratingDiet] = useState(false);
  const [isGeneratingWorkout, setIsGeneratingWorkout] = useState(false);

  const updateMealPlan = useCallback((plan: MealPlan) => {
    setMealPlanState(plan);
  }, []);

  const setMealPlan = useCallback((plan: MealPlan | null) => {
    setMealPlanState(plan);
  }, []);

  return (
    <AppContext.Provider
      value={{
        user, setUser,
        userProfile, setUserProfile,
        reportData, setReportData,
        reportFileName, setReportFileName,
        mealPlan, setMealPlan, updateMealPlan,
        macros, setMacros,
        dietPreference, setDietPreference,
        workoutPlan, setWorkoutPlan,
        isGeneratingDiet, setIsGeneratingDiet,
        isGeneratingWorkout, setIsGeneratingWorkout,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppContextProvider");
  return ctx;
}
