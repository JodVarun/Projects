import { useState } from "react";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { useAppContext } from "../context/AppContext";

export default function HomeTab() {
  const { user, setUserProfile, userProfile, setMacros } = useAppContext();

  const [goal, setGoal] = useState(userProfile?.goal || "maintain");
  const [gender, setGender] = useState(userProfile?.gender || "male");
  const [age, setAge] = useState(userProfile?.age?.toString() || "");
  const [height, setHeight] = useState(userProfile?.height?.toString() || "");
  const [weight, setWeight] = useState(userProfile?.weight?.toString() || "");
  const [activityLevel, setActivityLevel] = useState(userProfile?.activityLevel || "moderate");
  const [dailyCalories, setDailyCalories] = useState<number | null>(userProfile?.dailyCalories || null);
  const [loading, setLoading] = useState(false);

  const calculateCalories = async () => {
    if (!age || !height || !weight) return;

    setLoading(true);

    // Calculate BMR using Mifflin-St Jeor Equation
    let bmr: number;
    const weightNum = parseFloat(weight);
    const heightNum = parseFloat(height);
    const ageNum = parseInt(age);

    if (gender === "male") {
      bmr = 10 * weightNum + 6.25 * heightNum - 5 * ageNum + 5;
    } else {
      bmr = 10 * weightNum + 6.25 * heightNum - 5 * ageNum - 161;
    }

    const activityMultipliers: Record<string, number> = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      veryActive: 1.9,
    };

    let tdee = bmr * activityMultipliers[activityLevel];

    if (goal === "lose") tdee -= 500;
    else if (goal === "gain") tdee += 500;

    const finalCalories = Math.round(tdee);
    setDailyCalories(finalCalories);

    // Calculate macros
    let proteinMultiplier = 2.0;
    if (goal === "lose") proteinMultiplier = 2.2;
    if (goal === "maintain") proteinMultiplier = 1.8;

    const protein = Math.round(weightNum * proteinMultiplier);
    const fatCalories = finalCalories * 0.27;
    const fat = Math.round(fatCalories / 9);
    const carbCalories = finalCalories - protein * 4 - fatCalories;
    const carbs = Math.round(carbCalories / 4);

    setMacros({ calories: finalCalories, protein, carbs, fat });

    // Update user profile in context and localStorage
    const profileData = {
      name: user?.name || "",
      phoneNumber: user?.phoneNumber || "",
      goal,
      gender,
      age: ageNum,
      height: heightNum,
      weight: weightNum,
      activityLevel,
      dailyCalories: finalCalories,
    };

    setUserProfile(profileData);

    // Save to localStorage
    const currentUser = JSON.parse(localStorage.getItem("user") || "{}");
    currentUser.profile = { ...currentUser.profile, ...profileData };
    localStorage.setItem("user", JSON.stringify(currentUser));

    setLoading(false);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-white">Calorie Calculator</h1>

      {/* Input Form */}
      <div className="bg-[#18181b] rounded-3xl p-8 border border-gray-800">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Goal */}
          <div>
            <Label className="text-gray-300 mb-2 block">Goal</Label>
            <Select value={goal} onValueChange={setGoal}>
              <SelectTrigger className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#27272a] border-gray-700">
                <SelectItem value="lose">Lose Weight</SelectItem>
                <SelectItem value="maintain">Maintain Weight</SelectItem>
                <SelectItem value="gain">Gain Weight</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Gender */}
          <div>
            <Label className="text-gray-300 mb-2 block">Gender</Label>
            <Select value={gender} onValueChange={setGender}>
              <SelectTrigger className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#27272a] border-gray-700">
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Age */}
          <div>
            <Label className="text-gray-300 mb-2 block">Age (years)</Label>
            <Input
              type="number"
              placeholder="25"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl"
            />
          </div>

          {/* Height */}
          <div>
            <Label className="text-gray-300 mb-2 block">Height (cm)</Label>
            <Input
              type="number"
              placeholder="175"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl"
            />
          </div>

          {/* Weight */}
          <div>
            <Label className="text-gray-300 mb-2 block">Weight (kg)</Label>
            <Input
              type="number"
              placeholder="70"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl"
            />
          </div>

          {/* Activity Level */}
          <div>
            <Label className="text-gray-300 mb-2 block">Activity Level</Label>
            <Select value={activityLevel} onValueChange={setActivityLevel}>
              <SelectTrigger className="bg-[#27272a] border-gray-700 text-white h-12 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#27272a] border-gray-700">
                <SelectItem value="sedentary">Sedentary (little/no exercise)</SelectItem>
                <SelectItem value="light">Light (1-3 days/week)</SelectItem>
                <SelectItem value="moderate">Moderate (3-5 days/week)</SelectItem>
                <SelectItem value="active">Active (6-7 days/week)</SelectItem>
                <SelectItem value="veryActive">Very Active (2x per day)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Calculate Button */}
        <Button
          onClick={calculateCalories}
          disabled={loading || !age || !height || !weight}
          className="w-full mt-8 h-14 bg-[#ccff00] hover:bg-[#b8e600] text-black font-bold text-lg rounded-xl"
        >
          {loading ? "Calculating..." : "Calculate"}
        </Button>
      </div>

      {/* Result */}
      {dailyCalories !== null && (
        <div className="bg-gradient-to-br from-[#ccff00]/10 to-purple-500/10 rounded-3xl p-8 border border-[#ccff00]/30">
          <h3 className="text-2xl font-bold text-white mb-4">Daily Calories</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-6xl font-bold text-[#ccff00]">{dailyCalories}</span>
            <span className="text-2xl text-gray-400">kcal/day</span>
          </div>
          <p className="text-gray-400 mt-4">
            Based on your profile and activity level, this is your recommended daily caloric intake to {goal === "lose" ? "lose" : goal === "gain" ? "gain" : "maintain"} weight.
          </p>
          <p className="text-[#ccff00]/70 text-sm mt-2">
            ✨ Your Diet and Workout tabs will now be personalized to this profile!
          </p>
        </div>
      )}
    </div>
  );
}