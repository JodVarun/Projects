import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { useAppContext } from "../context/AppContext";
import { streamChat, parseDietUpdate, applyDietUpdate, type ChatMessage } from "../services/geminiService";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface AIChatBotProps {
  onClose: () => void;
}

export default function AIChatBot({ onClose }: AIChatBotProps) {
  const {
    userProfile, reportData, mealPlan, macros,
    dietPreference, workoutPlan, updateMealPlan,
  } = useAppContext();

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm FITFUEL AI, your personal fitness assistant powered by Gemini. I know about your profile, diet, workout, and medical reports. How can I help you today? 💪\n\n💡 Try: \"Replace the dinner roti with naan\" or \"How much protein should I eat?\"",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || isStreaming) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Prepare chat history for Gemini (skip first system message)
    const chatHistory: ChatMessage[] = messages
      .slice(1) // Skip initial greeting
      .map((m) => ({
        role: m.role === "user" ? "user" as const : "model" as const,
        content: m.content,
      }));
    chatHistory.push({ role: "user", content: input });

    // Add empty assistant message for streaming
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      setIsLoading(false);
      setIsStreaming(true);

      await streamChat(
        chatHistory,
        userProfile,
        reportData,
        mealPlan,
        macros,
        dietPreference,
        workoutPlan,
        // onChunk
        (text) => {
          // Remove the DIET_UPDATE block from displayed text
          const displayText = text.replace(/```DIET_UPDATE[\s\S]*?```/g, "").trim();
          setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              role: "assistant",
              content: displayText,
            };
            return newMessages;
          });
        },
        // onDone
        (fullText) => {
          setIsStreaming(false);

          // Check for diet update instructions
          const dietUpdate = parseDietUpdate(fullText);
          if (dietUpdate && mealPlan) {
            const updatedPlan = applyDietUpdate(mealPlan, dietUpdate);
            updateMealPlan(updatedPlan);

            // Clean display text
            const displayText = fullText.replace(/```DIET_UPDATE[\s\S]*?```/g, "").trim();
            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = {
                role: "assistant",
                content: displayText + "\n\n✅ Your diet plan has been updated! Check the Diet tab.",
              };
              return newMessages;
            });
          }
        },
        // onError
        (err) => {
          console.error("Chat error:", err);
          setIsStreaming(false);
          setIsLoading(false);

          // Fallback to smart local responses
          const smartResponse = generateLocalResponse(input.toLowerCase());
          setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              role: "assistant",
              content: smartResponse,
            };
            return newMessages;
          });
        }
      );
    } catch (err) {
      console.error("Chat error:", err);
      setIsLoading(false);
      setIsStreaming(false);

      const errorMessage: Message = {
        role: "assistant",
        content: "I'm having trouble connecting right now. Please check your Gemini API key in the .env file and try again! 💪",
      };
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = errorMessage;
        return newMessages;
      });
    }
  };

  const generateLocalResponse = (query: string): string => {
    if (query.includes("protein") || query.includes("macro")) {
      return userProfile?.weight
        ? `Based on your weight of ${userProfile.weight}kg, I recommend consuming ${Math.round(userProfile.weight * 2)}g of protein daily. Spread this across 4-5 meals with sources like chicken, fish, eggs, and legumes! 💪\n\n⚠️ Note: AI chat requires a Gemini API key for full functionality.`
        : "For optimal muscle growth, aim for 1.8-2.2g of protein per kg of body weight. Complete your profile in the Home tab for personalized recommendations! 🎯\n\n⚠️ AI chat requires a Gemini API key.";
    }
    if (query.includes("workout") || query.includes("exercise")) {
      return "Check your Workout tab for a personalized exercise plan! Click 'AI Generate' to get a plan tailored to your goals. 🏋️\n\n⚠️ Full AI chat requires a Gemini API key.";
    }
    if (query.includes("diet") || query.includes("meal") || query.includes("food")) {
      return "Check your Diet tab for a personalized meal plan! Click 'AI Generate' to get a plan based on your calorie target and preferences. 🍽️\n\n⚠️ Full AI chat (including dish modifications) requires a Gemini API key.";
    }
    return "I'd love to help! For full AI-powered responses, please add your Gemini API key to the .env file. In the meantime, check out the Diet and Workout tabs for personalized plans! 🚀";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-8 right-28 w-96 h-[600px] bg-[#18181b] rounded-3xl shadow-2xl border border-gray-800 flex flex-col z-40">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#ccff00] to-purple-500 p-6 rounded-t-3xl">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-black">FITFUEL AI</h3>
            <p className="text-sm text-black/70">
              {isStreaming ? "Streaming response..." : "Powered by Gemini"}
            </p>
          </div>
          {isStreaming && (
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-black rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
              <div className="w-2 h-2 bg-black rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
              <div className="w-2 h-2 bg-black rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 whitespace-pre-line ${
                message.role === "user"
                  ? "bg-[#ccff00] text-black"
                  : "bg-[#27272a] text-gray-200"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            className="bg-[#27272a] border-gray-700 text-white placeholder:text-gray-500 rounded-xl"
            disabled={isLoading || isStreaming}
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || isStreaming || !input.trim()}
            className="bg-[#ccff00] hover:bg-[#b8e600] text-black rounded-xl px-4 disabled:opacity-50"
          >
            {isLoading || isStreaming ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </Button>
        </div>
      </div>
    </div>
  );
}