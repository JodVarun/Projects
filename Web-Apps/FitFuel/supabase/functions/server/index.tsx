import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import * as kv from "./kv_store.tsx";
import { createClient } from "npm:@supabase/supabase-js";

const app = new Hono();

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-09ae0bc1/health", (c) => {
  return c.json({ status: "ok" });
});

// Send OTP endpoint
app.post("/make-server-09ae0bc1/send-otp", async (c) => {
  try {
    const { phoneNumber } = await c.req.json();
    
    if (!phoneNumber) {
      return c.json({ error: "Phone number is required" }, 400);
    }

    // Generate 6-digit OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    
    // Store OTP in KV store with 10 minute expiration
    const otpKey = `otp:${phoneNumber}`;
    await kv.set(otpKey, {
      otp,
      timestamp: Date.now(),
      expiresIn: 600000 // 10 minutes
    });

    // In a real app, you would send OTP via SMS API here
    // For now, we'll log it to console for testing
    console.log(`OTP for ${phoneNumber}: ${otp}`);
    
    // NOTE: To use a real SMS service like MSG91, Twilio, or AWS SNS:
    // 1. Get API key from the service
    // 2. Make HTTP request to their API
    // Example with MSG91:
    // const msg91ApiKey = Deno.env.get('MSG91_API_KEY');
    // await fetch(`https://api.msg91.com/api/v5/otp?...`, {
    //   method: 'POST',
    //   headers: { 'authkey': msg91ApiKey },
    //   body: JSON.stringify({ ... })
    // });

    return c.json({ 
      success: true, 
      message: "OTP sent successfully",
      // In production, remove this debug info
      debug: { otp } // For testing only - remove in production
    });
  } catch (error) {
    console.error("Error sending OTP:", error);
    return c.json({ error: "Failed to send OTP" }, 500);
  }
});

// Verify OTP and create/login user
app.post("/make-server-09ae0bc1/verify-otp", async (c) => {
  try {
    const { phoneNumber, otp, name } = await c.req.json();
    
    if (!phoneNumber || !otp) {
      return c.json({ error: "Phone number and OTP are required" }, 400);
    }

    // Get stored OTP
    const otpKey = `otp:${phoneNumber}`;
    const storedData = await kv.get(otpKey);
    
    if (!storedData) {
      return c.json({ error: "OTP expired or not found" }, 400);
    }

    // Check expiration
    const now = Date.now();
    if (now - storedData.timestamp > storedData.expiresIn) {
      await kv.del(otpKey);
      return c.json({ error: "OTP expired" }, 400);
    }

    // Verify OTP
    if (storedData.otp !== otp) {
      return c.json({ error: "Invalid OTP" }, 400);
    }

    // Delete OTP after successful verification
    await kv.del(otpKey);

    // Check if user exists
    const userKey = `user:${phoneNumber}`;
    let user = await kv.get(userKey);

    if (!user) {
      // Create new user
      user = {
        phoneNumber,
        name: name || "User",
        createdAt: now,
        profile: {
          age: null,
          gender: null,
          height: null,
          weight: null,
          activityLevel: null,
          goal: null,
          dailyCalories: null
        }
      };
      await kv.set(userKey, user);
    } else if (name && user.name !== name) {
      // Update user name if provided
      user.name = name;
      await kv.set(userKey, user);
    }

    // Create session token (simple implementation)
    const sessionToken = `${phoneNumber}_${now}_${Math.random().toString(36).substring(7)}`;
    const sessionKey = `session:${sessionToken}`;
    await kv.set(sessionKey, {
      phoneNumber,
      createdAt: now,
      expiresIn: 2592000000 // 30 days
    });

    return c.json({ 
      success: true, 
      user,
      sessionToken
    });
  } catch (error) {
    console.error("Error verifying OTP:", error);
    return c.json({ error: "Failed to verify OTP" }, 500);
  }
});

// Get user profile
app.get("/make-server-09ae0bc1/user/:phoneNumber", async (c) => {
  try {
    const phoneNumber = c.req.param('phoneNumber');
    const sessionToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!sessionToken) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    // Verify session
    const sessionKey = `session:${sessionToken}`;
    const session = await kv.get(sessionKey);
    
    if (!session || session.phoneNumber !== phoneNumber) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    const userKey = `user:${phoneNumber}`;
    const user = await kv.get(userKey);
    
    if (!user) {
      return c.json({ error: "User not found" }, 404);
    }

    return c.json({ user });
  } catch (error) {
    console.error("Error getting user profile:", error);
    return c.json({ error: "Failed to get user profile" }, 500);
  }
});

// Update user profile
app.post("/make-server-09ae0bc1/user/:phoneNumber/profile", async (c) => {
  try {
    const phoneNumber = c.req.param('phoneNumber');
    const sessionToken = c.req.header('Authorization')?.split(' ')[1];
    const profileData = await c.req.json();
    
    if (!sessionToken) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    // Verify session
    const sessionKey = `session:${sessionToken}`;
    const session = await kv.get(sessionKey);
    
    if (!session || session.phoneNumber !== phoneNumber) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    const userKey = `user:${phoneNumber}`;
    const user = await kv.get(userKey);
    
    if (!user) {
      return c.json({ error: "User not found" }, 404);
    }

    // Update profile
    user.profile = { ...user.profile, ...profileData };
    await kv.set(userKey, user);

    return c.json({ success: true, user });
  } catch (error) {
    console.error("Error updating user profile:", error);
    return c.json({ error: "Failed to update user profile" }, 500);
  }
});

// Save workout data
app.post("/make-server-09ae0bc1/user/:phoneNumber/workout", async (c) => {
  try {
    const phoneNumber = c.req.param('phoneNumber');
    const sessionToken = c.req.header('Authorization')?.split(' ')[1];
    const workoutData = await c.req.json();
    
    if (!sessionToken) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    const sessionKey = `session:${sessionToken}`;
    const session = await kv.get(sessionKey);
    
    if (!session || session.phoneNumber !== phoneNumber) {
      return c.json({ error: "Unauthorized" }, 401);
    }

    const workoutKey = `workout:${phoneNumber}:${Date.now()}`;
    await kv.set(workoutKey, {
      ...workoutData,
      timestamp: Date.now()
    });

    return c.json({ success: true });
  } catch (error) {
    console.error("Error saving workout:", error);
    return c.json({ error: "Failed to save workout" }, 500);
  }
});

// AI Chat endpoint with streaming support
app.post("/make-server-09ae0bc1/ai-chat", async (c) => {
  try {
    const { messages, userProfile } = await c.req.json();
    
    if (!messages || !Array.isArray(messages)) {
      return c.json({ error: "Messages array is required" }, 400);
    }

    // Get OpenAI API key from environment
    const openaiApiKey = Deno.env.get('OPENAI_API_KEY');
    
    if (!openaiApiKey) {
      console.error("OPENAI_API_KEY not found in environment variables");
      return c.json({ 
        error: "AI service not configured. Please add OPENAI_API_KEY to environment variables." 
      }, 500);
    }

    // Build system prompt with user context
    let systemPrompt = `You are FITFUEL AI, an expert personal fitness trainer and nutritionist. You provide personalized fitness advice, workout plans, diet recommendations, and health insights.

Your personality:
- Encouraging and motivating
- Professional yet friendly
- Use fitness terminology but explain complex concepts
- Give specific, actionable advice
- Always prioritize user safety

Guidelines:
- Keep responses concise (2-3 paragraphs max)
- Ask clarifying questions when needed
- Reference scientific principles when relevant
- Never diagnose medical conditions - recommend consulting a doctor for serious concerns`;

    if (userProfile) {
      systemPrompt += `\n\nUser Profile:`;
      if (userProfile.name) systemPrompt += `\n- Name: ${userProfile.name}`;
      if (userProfile.age) systemPrompt += `\n- Age: ${userProfile.age}`;
      if (userProfile.gender) systemPrompt += `\n- Gender: ${userProfile.gender}`;
      if (userProfile.weight) systemPrompt += `\n- Weight: ${userProfile.weight}kg`;
      if (userProfile.height) systemPrompt += `\n- Height: ${userProfile.height}cm`;
      if (userProfile.goal) {
        const goalText = userProfile.goal === 'lose' ? 'Lose Weight' : 
                        userProfile.goal === 'gain' ? 'Gain Muscle' : 'Maintain Weight';
        systemPrompt += `\n- Goal: ${goalText}`;
      }
      if (userProfile.dailyCalories) systemPrompt += `\n- Daily Calorie Target: ${userProfile.dailyCalories} kcal`;
      if (userProfile.activityLevel) systemPrompt += `\n- Activity Level: ${userProfile.activityLevel}`;
    }

    // Call OpenAI API with streaming
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openaiApiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini', // Fast and cost-effective model
        messages: [
          { role: 'system', content: systemPrompt },
          ...messages
        ],
        temperature: 0.7,
        max_tokens: 500,
        stream: true, // Enable streaming
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('OpenAI API error:', errorData);
      return c.json({ 
        error: `AI service error: ${errorData.error?.message || 'Unknown error'}` 
      }, response.status);
    }

    // Return streaming response
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error("Error in AI chat:", error);
    return c.json({ error: "AI chat failed. Please try again." }, 500);
  }
});

Deno.serve(app.fetch);