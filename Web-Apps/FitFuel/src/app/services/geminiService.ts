import type { MealPlan, Macros, UserProfile, WorkoutPlan } from "../context/AppContext";

// @ts-ignore - Vite injects import.meta.env at build time
const GEMINI_API_KEY: string = import.meta.env.VITE_GEMINI_API_KEY || "";
const GEMINI_MODEL = "gemini-2.5-flash";
const GEMINI_FALLBACK_MODEL = "gemini-2.5-flash-lite";
const BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models";

function getApiUrl(model: string) {
  return `${BASE_URL}/${model}:generateContent?key=${GEMINI_API_KEY}`;
}
function getStreamUrl(model: string) {
  return `${BASE_URL}/${model}:streamGenerateContent?alt=sse&key=${GEMINI_API_KEY}`;
}

// ---- Helper ----

function buildSystemContext(
  profile: UserProfile | null,
  reportData: string,
  mealPlan: MealPlan | null,
  macros: Macros,
  dietPreference: string,
  workoutPlan: WorkoutPlan | null
): string {
  let ctx = `You are FITFUEL AI, a personal fitness and nutrition assistant. Be concise, helpful, and use emojis sparingly.\n\n`;

  if (profile) {
    ctx += `## User Profile\n`;
    ctx += `- Name: ${profile.name}\n`;
    if (profile.age) ctx += `- Age: ${profile.age} years\n`;
    if (profile.gender) ctx += `- Gender: ${profile.gender}\n`;
    if (profile.height) ctx += `- Height: ${profile.height} cm\n`;
    if (profile.weight) ctx += `- Weight: ${profile.weight} kg\n`;
    if (profile.activityLevel) ctx += `- Activity Level: ${profile.activityLevel}\n`;
    if (profile.goal) ctx += `- Goal: ${profile.goal === "lose" ? "Weight Loss" : profile.goal === "gain" ? "Muscle Gain" : "Maintain Weight"}\n`;
    if (profile.dailyCalories) ctx += `- Daily Calorie Target: ${profile.dailyCalories} kcal\n`;
    ctx += `\n`;
  }

  ctx += `## Current Macros Target\n`;
  ctx += `- Calories: ${macros.calories} kcal, Protein: ${macros.protein}g, Carbs: ${macros.carbs}g, Fat: ${macros.fat}g\n`;
  ctx += `- Diet Preference: ${dietPreference}\n\n`;

  if (reportData) {
    ctx += `## Medical Report Insights\n${reportData}\n\n`;
  }

  if (mealPlan) {
    ctx += `## Current Diet Plan\n`;
    for (const [meal, items] of Object.entries(mealPlan)) {
      ctx += `### ${meal.charAt(0).toUpperCase() + meal.slice(1)}\n`;
      (items as any[]).forEach((item: any) => {
        ctx += `- ${item.name} (${item.quantity}, ${item.calories} cal)\n`;
      });
    }
    ctx += `\n`;
  }

  if (workoutPlan) {
    ctx += `## Current Workout Plan\n`;
    workoutPlan.exercises.forEach((ex) => {
      ctx += `- ${ex.name}: ${ex.sets} sets × ${ex.reps} (${ex.category})\n`;
    });
    ctx += `\n`;
  }

  return ctx;
}

// ---- Streaming chat ----

export interface ChatMessage {
  role: "user" | "model";
  content: string;
}

export async function streamChat(
  messages: ChatMessage[],
  profile: UserProfile | null,
  reportData: string,
  mealPlan: MealPlan | null,
  macros: Macros,
  dietPreference: string,
  workoutPlan: WorkoutPlan | null,
  onChunk: (text: string) => void,
  onDone: (fullText: string) => void,
  onError: (err: Error) => void
) {
  const systemContext = buildSystemContext(profile, reportData, mealPlan, macros, dietPreference, workoutPlan);

  // Add diet modification instructions
  const systemPrompt = systemContext + `\n## Special Instructions
When the user asks to change, replace, or swap a dish/food in their diet plan, respond with a CONFIRMATION of the change and include a JSON block in this exact format:
\`\`\`DIET_UPDATE
{
  "meal": "breakfast|lunch|snacks|dinner",
  "oldItem": "name of old item",
  "newItem": { "name": "new dish name", "quantity": "amount", "calories": 123, "protein": 10, "carbs": 20, "fat": 5 }
}
\`\`\`
Only include this JSON block when the user explicitly asks to change a food item. For general questions, just answer normally.
`;

  const contents = [
    {
      role: "user",
      parts: [{ text: systemPrompt + "\n\nPlease acknowledge you understand your role silently — do not print these instructions." }],
    },
    {
      role: "model",
      parts: [{ text: "Understood! I'm FITFUEL AI, ready to help with fitness and nutrition. How can I assist you?" }],
    },
    ...messages.map((m) => ({
      role: m.role === "user" ? "user" : "model",
      parts: [{ text: m.content }],
    })),
  ];

  const models = [GEMINI_MODEL, GEMINI_FALLBACK_MODEL];

  for (const model of models) {
    try {
      const response = await fetch(getStreamUrl(model), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents,
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 2048,
          },
        }),
      });

      if (!response.ok) {
        const errText = await response.text();
        console.warn(`Model ${model} failed (${response.status}), trying next...`);
        if (model === models[models.length - 1]) {
          throw new Error(`Gemini API error: ${response.status} — ${errText}`);
        }
        continue;
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (!data || data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data);
              const text = parsed.candidates?.[0]?.content?.parts?.[0]?.text;
              if (text) {
                fullText += text;
                onChunk(fullText);
              }
            } catch {
              // skip invalid JSON
            }
          }
        }
      }

      onDone(fullText);
      return; // Success — stop trying models
    } catch (err: any) {
      if (model === models[models.length - 1]) {
        onError(err);
      }
    }
  }
}

// ---- Diet plan generation ----

export async function generateDietPlan(
  profile: UserProfile | null,
  macros: Macros,
  dietPreference: string,
  reportData: string
): Promise<MealPlan> {
  const prompt = `Generate a personalized daily Indian meal plan.

Requirements:
- Diet preference: ${dietPreference}
- Target: ${macros.calories} kcal, ${macros.protein}g protein, ${macros.carbs}g carbs, ${macros.fat}g fat
${profile?.goal ? `- Goal: ${profile.goal === "lose" ? "Weight Loss" : profile.goal === "gain" ? "Muscle Gain" : "Maintain"}` : ""}
${reportData ? `- Medical report insights to consider: ${reportData}` : ""}

Return ONLY valid JSON (no markdown fences, no explanation) in this exact format:
{
  "breakfast": [{"name": "...", "quantity": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}],
  "lunch": [{"name": "...", "quantity": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}],
  "snacks": [{"name": "...", "quantity": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}],
  "dinner": [{"name": "...", "quantity": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}]
}

Include 3-5 items per meal. Use Indian fusion dishes. Ensure total calories approximately match the target.`;

  let response = await fetch(getApiUrl(GEMINI_MODEL), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.8, maxOutputTokens: 2048 },
    }),
  });

  if (!response.ok) {
    // Try fallback model
    response = await fetch(getApiUrl(GEMINI_FALLBACK_MODEL), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.8, maxOutputTokens: 2048 },
      }),
    });
    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`);
    }
  }

  const data = await response.json();
  let text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";

  // Strip markdown code fences if present
  text = text.replace(/```json\s*/gi, "").replace(/```\s*/g, "").trim();

  try {
    return JSON.parse(text) as MealPlan;
  } catch {
    throw new Error("Failed to parse diet plan from AI response");
  }
}

// ---- Workout plan generation ----

export async function generateWorkoutPlan(
  profile: UserProfile | null,
  reportData: string
): Promise<WorkoutPlan> {
  const prompt = `Generate a personalized workout plan.

User info:
${profile?.goal ? `- Goal: ${profile.goal === "lose" ? "Weight Loss" : profile.goal === "gain" ? "Muscle Gain" : "Maintain"}` : "- Goal: General Fitness"}
${profile?.age ? `- Age: ${profile.age}` : ""}
${profile?.weight ? `- Weight: ${profile.weight} kg` : ""}
${profile?.activityLevel ? `- Activity Level: ${profile.activityLevel}` : ""}
${reportData ? `- Medical considerations: ${reportData}` : ""}

Return ONLY valid JSON (no markdown fences, no explanation) in this exact format:
{
  "exercises": [
    {"name": "Exercise Name", "sets": 3, "reps": "10-12", "category": "Strength|Cardio|Flexibility", "notes": "optional tip"}
  ],
  "cardio": ["description of each cardio recommendation"],
  "recovery": ["recovery tip 1", "recovery tip 2"],
  "notes": "Overall workout plan notes tailored to user"
}

Include 7-10 exercises, 3-4 cardio recommendations, and 4-5 recovery tips. Tailor to user's goal and any medical considerations.`;

  let response = await fetch(getApiUrl(GEMINI_MODEL), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.8, maxOutputTokens: 2048 },
    }),
  });

  if (!response.ok) {
    response = await fetch(getApiUrl(GEMINI_FALLBACK_MODEL), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.8, maxOutputTokens: 2048 },
      }),
    });
    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`);
    }
  }

  const data = await response.json();
  let text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";

  text = text.replace(/```json\s*/gi, "").replace(/```\s*/g, "").trim();

  try {
    return JSON.parse(text) as WorkoutPlan;
  } catch {
    throw new Error("Failed to parse workout plan from AI response");
  }
}

// ---- Report analysis ----

export async function analyzeReport(reportText: string): Promise<string> {
  const prompt = `You are a health analyst AI. Analyze this medical report and provide a concise summary of key health markers, concerns, and recommendations relevant to fitness and nutrition planning.

Report content:
${reportText}

Provide a structured summary with:
1. Key health markers (cholesterol, blood sugar, vitamin levels, etc.)
2. Any concerns or areas needing attention
3. Dietary recommendations based on the report
4. Exercise considerations based on the report

Be concise but thorough. This summary will be used to personalize the user's diet and workout plans.`;

  let response = await fetch(getApiUrl(GEMINI_MODEL), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.4, maxOutputTokens: 1024 },
    }),
  });

  if (!response.ok) {
    response = await fetch(getApiUrl(GEMINI_FALLBACK_MODEL), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.4, maxOutputTokens: 1024 },
      }),
    });
    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`);
    }
  }

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text || "Unable to analyze report.";
}

// ---- Parse diet update from chat response ----

export function parseDietUpdate(text: string): {
  meal: string;
  oldItem: string;
  newItem: { name: string; quantity: string; calories: number; protein: number; carbs: number; fat: number };
} | null {
  const match = text.match(/```DIET_UPDATE\s*\n([\s\S]*?)\n```/);
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch {
    return null;
  }
}

export function applyDietUpdate(
  currentPlan: MealPlan,
  update: { meal: string; oldItem: string; newItem: any }
): MealPlan {
  const newPlan = { ...currentPlan };
  const mealKey = update.meal as keyof MealPlan;

  if (newPlan[mealKey]) {
    newPlan[mealKey] = newPlan[mealKey].map((item) =>
      item.name.toLowerCase().includes(update.oldItem.toLowerCase())
        ? { ...update.newItem }
        : item
    );
  }

  return newPlan;
}
