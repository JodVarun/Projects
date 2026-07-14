import { useState, useEffect } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Label } from "./ui/label";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";
import { Button } from "./ui/button";
import { RefreshCw, Loader2, Sparkles } from "lucide-react";
import { useAppContext } from "../context/AppContext";
import { generateDietPlan } from "../services/geminiService";

// ---- Fallback static meal plans ----

const fallbackMealPlans = {
  vegetarian: {
    breakfast: [
      { name: "Oatmeal with berries & honey", quantity: "150g", calories: 250, protein: 8, carbs: 45, fat: 4 },
      { name: "Greek yogurt", quantity: "200g", calories: 150, protein: 20, carbs: 8, fat: 4 },
      { name: "Banana", quantity: "1 medium", calories: 105, protein: 1, carbs: 27, fat: 0 },
      { name: "Almonds", quantity: "20g", calories: 120, protein: 4, carbs: 4, fat: 10 },
    ],
    lunch: [
      { name: "Dal tadka (yellow lentils)", quantity: "200g", calories: 180, protein: 12, carbs: 26, fat: 4 },
      { name: "Brown rice", quantity: "150g", calories: 216, protein: 5, carbs: 45, fat: 2 },
      { name: "Mixed vegetable sabzi", quantity: "150g", calories: 120, protein: 4, carbs: 15, fat: 5 },
      { name: "Raita (cucumber yogurt)", quantity: "100g", calories: 60, protein: 3, carbs: 6, fat: 2 },
      { name: "Roti (whole wheat)", quantity: "2 pieces", calories: 194, protein: 6, carbs: 30, fat: 2 },
    ],
    snacks: [
      { name: "Protein bar", quantity: "1 bar", calories: 180, protein: 12, carbs: 20, fat: 6 },
      { name: "Banana", quantity: "1 medium", calories: 40, protein: 1, carbs: 27, fat: 0 },
    ],
    dinner: [
      { name: "Paneer tikka", quantity: "150g", calories: 280, protein: 18, carbs: 8, fat: 20 },
      { name: "Mix veg curry", quantity: "200g", calories: 140, protein: 5, carbs: 18, fat: 6 },
      { name: "Roti", quantity: "2 pieces", calories: 240, protein: 6, carbs: 30, fat: 2 },
    ],
  },
};

export default function DietTab() {
  const {
    userProfile, reportData, macros, setMacros,
    mealPlan, setMealPlan, updateMealPlan,
    dietPreference, setDietPreference,
    isGeneratingDiet, setIsGeneratingDiet,
  } = useAppContext();

  const [aiGenerated, setAiGenerated] = useState(false);
  const [error, setError] = useState("");

  // Calculate macros when profile changes
  useEffect(() => {
    if (userProfile?.dailyCalories && userProfile?.weight && userProfile?.goal) {
      const targetCalories = userProfile.dailyCalories;
      const weight = userProfile.weight;
      const goal = userProfile.goal;

      let proteinMultiplier = 2.0;
      if (goal === "lose") proteinMultiplier = 2.2;
      if (goal === "maintain") proteinMultiplier = 1.8;

      const protein = Math.round(weight * proteinMultiplier);
      const fatCalories = targetCalories * 0.27;
      const fat = Math.round(fatCalories / 9);
      const carbCalories = targetCalories - protein * 4 - fatCalories;
      const carbs = Math.round(carbCalories / 4);

      setMacros({ calories: targetCalories, protein, carbs, fat });
    }
  }, [userProfile, setMacros]);

  // Load initial meal plan if none exists
  useEffect(() => {
    if (!mealPlan) {
      setMealPlan(fallbackMealPlans.vegetarian);
    }
  }, [mealPlan, setMealPlan]);

  const handleGenerateWithAI = async () => {
    setIsGeneratingDiet(true);
    setError("");
    setAiGenerated(false);
    try {
      const plan = await generateDietPlan(userProfile, macros, dietPreference, reportData);
      updateMealPlan(plan);
      setAiGenerated(true);
    } catch (err: any) {
      console.error("Diet generation error:", err);
      if (err.message?.includes("Gemini API") || err.message?.includes("Failed to parse")) {
        setError("AI generation failed. Using default plan. Please check your Gemini API key.");
      } else {
        setError("Failed to generate diet plan. Try again.");
      }
      // Fallback
      if (!mealPlan) {
        setMealPlan(fallbackMealPlans.vegetarian);
      }
    } finally {
      setIsGeneratingDiet(false);
    }
  };

  const pieData = [
    { name: "Protein", value: macros.protein * 4, color: "#ccff00" },
    { name: "Carbs", value: macros.carbs * 4, color: "#a855f7" },
    { name: "Fat", value: macros.fat * 9, color: "#3b82f6" },
  ];

  const foodsToPrefer = [
    "Whole grains (oats, quinoa, brown rice)",
    "Lean proteins (chicken, fish, tofu, paneer)",
    "Leafy greens (spinach, kale, methi)",
    "Healthy fats (avocado, nuts, olive oil)",
    "Fresh fruits (berries, apples, bananas)",
    "Lentils & legumes (dal, rajma, chana)",
  ];

  const foodsToAvoid = [
    "Processed sugars and candy",
    "Deep fried foods (pakoras, samosas)",
    "Sugary beverages and sodas",
    "Refined carbohydrates (maida, white bread)",
    "Excessive oil and ghee",
    "Junk food and fast food",
  ];

  if (!mealPlan) {
    return <div className="text-white">Loading meal plan...</div>;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-white">Diet Protocol</h1>

      {/* Personalization Info */}
      {userProfile?.dailyCalories ? (
        <div className="bg-gradient-to-r from-[#ccff00]/10 to-transparent border border-[#ccff00]/30 rounded-2xl p-4">
          <p className="text-sm text-gray-300">
            ✨ <span className="text-[#ccff00] font-semibold">Personalized Plan</span> — This diet is tailored to your {macros.calories} calorie goal for <span className="font-semibold">{userProfile.goal === "lose" ? "weight loss" : userProfile.goal === "gain" ? "muscle gain" : "maintenance"}</span>
            {reportData && <span className="text-purple-400"> • Enhanced with medical report insights</span>}
          </p>
        </div>
      ) : (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-4">
          <p className="text-sm text-yellow-200">
            💡 <span className="font-semibold">Tip:</span> Complete your profile in the Home tab to get a personalized diet plan based on your calorie needs!
          </p>
        </div>
      )}

      {/* AI Generated Badge */}
      {aiGenerated && (
        <div className="bg-purple-500/10 border border-purple-500/30 rounded-2xl p-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <p className="text-sm text-purple-300">
            This meal plan was generated by AI based on your profile{reportData ? ", medical report" : ""}, and diet preference. Ask the chatbot to swap any dish!
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Macros Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#18181b] rounded-3xl p-8 border border-gray-800">
          <h3 className="text-2xl font-bold text-white mb-6">Daily Macros</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Calories</span>
              <span className="text-2xl font-bold text-[#ccff00]">{macros.calories} kcal</span>
            </div>
            <div className="h-px bg-gray-800" />
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Protein</span>
              <span className="text-xl font-semibold text-white">{macros.protein}g</span>
            </div>
            <div className="h-px bg-gray-800" />
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Carbs</span>
              <span className="text-xl font-semibold text-white">{macros.carbs}g</span>
            </div>
            <div className="h-px bg-gray-800" />
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Fat</span>
              <span className="text-xl font-semibold text-white">{macros.fat}g</span>
            </div>
          </div>
        </div>

        <div className="bg-[#18181b] rounded-3xl p-8 border border-gray-800">
          <h3 className="text-2xl font-bold text-white mb-6">Macro Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Legend wrapperStyle={{ color: "#fff" }} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Diet Preference */}
      <div className="bg-[#18181b] rounded-3xl p-8 border border-gray-800">
        <Label className="text-gray-300 mb-3 block text-lg">Diet Preference</Label>
        <Select value={dietPreference} onValueChange={setDietPreference}>
          <SelectTrigger className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl max-w-md">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-[#27272a] border-gray-700">
            <SelectItem value="vegetarian">Vegetarian</SelectItem>
            <SelectItem value="eggetarian">Egg-etarian</SelectItem>
            <SelectItem value="nonvegetarian">Non-vegetarian</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Food Guidance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#18181b] rounded-3xl p-8 border border-green-500/20">
          <h3 className="text-2xl font-bold text-green-400 mb-6">Foods to Prefer ✓</h3>
          <ul className="space-y-3">
            {foodsToPrefer.map((food, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="text-green-400 mt-1">●</span>
                <span className="text-gray-300">{food}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-[#18181b] rounded-3xl p-8 border border-red-500/20">
          <h3 className="text-2xl font-bold text-red-400 mb-6">Foods to Avoid ✗</h3>
          <ul className="space-y-3">
            {foodsToAvoid.map((food, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="text-red-400 mt-1">●</span>
                <span className="text-gray-300">{food}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Daily Meal Plan */}
      <div className="bg-[#18181b] rounded-3xl p-8 border border-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-white">Daily Meal Plan</h3>
          <Button
            onClick={handleGenerateWithAI}
            disabled={isGeneratingDiet}
            className="bg-[#ccff00] text-black hover:bg-[#b8e600] rounded-xl px-4 py-2 font-semibold"
          >
            {isGeneratingDiet ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                AI Generate
              </>
            )}
          </Button>
        </div>

        <div className="space-y-8">
          {/* Breakfast */}
          <div>
            <h4 className="text-xl font-semibold text-[#ccff00] mb-4">Breakfast</h4>
            <div className="space-y-3">
              {mealPlan.breakfast.map((item, index) => (
                <div key={index} className="flex justify-between items-center py-2 border-b border-gray-800">
                  <span className="text-gray-300">{item.name}</span>
                  <span className="text-gray-500">{item.quantity} • {item.calories} cal</span>
                </div>
              ))}
            </div>
          </div>

          {/* Lunch */}
          <div>
            <h4 className="text-xl font-semibold text-[#ccff00] mb-4">Lunch</h4>
            <div className="space-y-3">
              {mealPlan.lunch.map((item, index) => (
                <div key={index} className="flex justify-between items-center py-2 border-b border-gray-800">
                  <span className="text-gray-300">{item.name}</span>
                  <span className="text-gray-500">{item.quantity} • {item.calories} cal</span>
                </div>
              ))}
            </div>
          </div>

          {/* Snacks */}
          <div>
            <h4 className="text-xl font-semibold text-[#ccff00] mb-4">Snacks</h4>
            <div className="space-y-3">
              {mealPlan.snacks.map((item, index) => (
                <div key={index} className="flex justify-between items-center py-2 border-b border-gray-800">
                  <span className="text-gray-300">{item.name}</span>
                  <span className="text-gray-500">{item.quantity} • {item.calories} cal</span>
                </div>
              ))}
            </div>
          </div>

          {/* Dinner */}
          <div>
            <h4 className="text-xl font-semibold text-[#ccff00] mb-4">Dinner</h4>
            <div className="space-y-3">
              {mealPlan.dinner.map((item, index) => (
                <div key={index} className="flex justify-between items-center py-2 border-b border-gray-800">
                  <span className="text-gray-300">{item.name}</span>
                  <span className="text-gray-500">{item.quantity} • {item.calories} cal</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}