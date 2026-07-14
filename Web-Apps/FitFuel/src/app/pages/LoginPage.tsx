import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import {
  isFirebaseConfigured,
  setupRecaptcha,
  sendFirebaseOtp,
  verifyFirebaseOtp,
  type ConfirmationResult,
} from "../services/firebaseAuth";

export default function LoginPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [name, setName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [debugOtp, setDebugOtp] = useState("");
  const [authMode, setAuthMode] = useState<"firebase" | "local">(
    isFirebaseConfigured ? "firebase" : "local"
  );

  // Firebase state
  const [confirmationResult, setConfirmationResult] =
    useState<ConfirmationResult | null>(null);
  const recaptchaRef = useRef<any>(null);

  useEffect(() => {
    // Check if already logged in
    const sessionToken = localStorage.getItem("sessionToken");
    if (sessionToken) {
      navigate("/dashboard");
    }
  }, [navigate]);

  useEffect(() => {
    // Setup reCAPTCHA when in firebase mode and on phone step
    if (authMode === "firebase" && step === "phone" && !recaptchaRef.current) {
      setTimeout(() => {
        recaptchaRef.current = setupRecaptcha("send-otp-btn");
      }, 500);
    }
  }, [authMode, step]);

  const handleSendOtp = async () => {
    if (!phoneNumber || !name) {
      setError("Please enter your name and phone number");
      return;
    }

    setLoading(true);
    setError("");

    if (authMode === "firebase") {
      // Firebase Phone Auth
      try {
        if (!recaptchaRef.current) {
          recaptchaRef.current = setupRecaptcha("send-otp-btn");
        }

        if (!recaptchaRef.current) {
          throw new Error("reCAPTCHA not initialized");
        }

        const result = await sendFirebaseOtp(phoneNumber, recaptchaRef.current);
        setConfirmationResult(result);
        setStep("otp");
      } catch (err: any) {
        console.error("Firebase OTP error:", err);

        if (err.code === "auth/invalid-phone-number") {
          setError("Invalid phone number. Use format: +91XXXXXXXXXX");
        } else if (err.code === "auth/too-many-requests") {
          setError("Too many attempts. Please try again later.");
        } else if (err.code === "auth/captcha-check-failed") {
          setError("reCAPTCHA verification failed. Please refresh and try again.");
          recaptchaRef.current = null;
        } else {
          setError(`Firebase Error: ${err.message || "Unknown error"}`);
        }
      }
    } else {
      // Local fallback OTP
      handleLocalSendOtp();
    }

    setLoading(false);
  };

  const handleLocalSendOtp = () => {
    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    localStorage.setItem(`otp:${phoneNumber}`, generatedOtp);
    setDebugOtp(generatedOtp);
    setStep("otp");
  };

  const handleVerifyOtp = async () => {
    if (!otp) {
      setError("Please enter the OTP");
      return;
    }

    setLoading(true);
    setError("");

    if (authMode === "firebase" && confirmationResult) {
      // Firebase verification
      try {
        const firebaseUser = await verifyFirebaseOtp(confirmationResult, otp);

        const sessionToken = firebaseUser.uid;
        const user = {
          phoneNumber: firebaseUser.phoneNumber || phoneNumber,
          name,
          uid: firebaseUser.uid,
          createdAt: Date.now(),
          profile: {
            age: null,
            gender: null,
            height: null,
            weight: null,
            activityLevel: null,
            goal: null,
            dailyCalories: null,
          },
        };

        localStorage.setItem("sessionToken", sessionToken);
        localStorage.setItem("user", JSON.stringify(user));
        navigate("/dashboard");
      } catch (err: any) {
        console.error("Firebase verify error:", err);
        if (err.code === "auth/invalid-verification-code") {
          setError("Invalid OTP. Please check and try again.");
        } else if (err.code === "auth/code-expired") {
          setError("OTP expired. Please request a new one.");
        } else {
          setError("Verification failed. Please try again.");
        }
      }
    } else {
      // Local verification
      const storedOtp = localStorage.getItem(`otp:${phoneNumber}`);

      if (storedOtp === otp) {
        const sessionToken = `local_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        const user = {
          phoneNumber,
          name,
          createdAt: Date.now(),
          profile: {
            age: null,
            gender: null,
            height: null,
            weight: null,
            activityLevel: null,
            goal: null,
            dailyCalories: null,
          },
        };

        localStorage.setItem("sessionToken", sessionToken);
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.removeItem(`otp:${phoneNumber}`);
        navigate("/dashboard");
      } else {
        setError("Invalid OTP");
      }
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#050505] flex">
      {/* Left Side - Image */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#ccff00]/20 via-transparent to-purple-500/20" />
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1758875569612-94d5e0f1a35f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhdGhsZXRpYyUyMHBlcnNvbiUyMGZpdG5lc3MlMjBneW18ZW58MXx8fHwxNzczNzI3NzUxfDA&ixlib=rb-4.1.0&q=80&w=1080"
          alt="Fitness"
          className="w-full h-full object-cover opacity-80"
        />
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4">
              <span className="text-white">FIT</span>
              <span className="text-[#ccff00]">FUEL</span>
              <span className="text-white">.</span>
            </h1>
            <p className="text-gray-400 text-lg">
              Your Personal Fitness Companion
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-[#18181b] rounded-3xl p-8 shadow-2xl border border-gray-800">
            {step === "phone" ? (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">
                    Welcome Back
                  </h2>
                  <p className="text-gray-400">
                    Enter your details to get started
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name" className="text-gray-300">
                      Your Name
                    </Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="John Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="mt-1.5 bg-[#27272a] border-gray-700 text-white placeholder:text-gray-500 h-12 rounded-xl focus:border-[#ccff00] focus:ring-[#ccff00]"
                    />
                  </div>

                  <div>
                    <Label htmlFor="phone" className="text-gray-300">
                      Phone Number
                    </Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder={authMode === "firebase" ? "+91 98765 43210" : "Enter any number"}
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      className="mt-1.5 bg-[#27272a] border-gray-700 text-white placeholder:text-gray-500 h-12 rounded-xl focus:border-[#ccff00] focus:ring-[#ccff00]"
                    />
                    {authMode === "firebase" && (
                      <p className="text-xs text-gray-500 mt-1">Include country code (e.g., +91 for India)</p>
                    )}
                  </div>
                </div>

                {/* Auth Mode Indicator */}
                <div className={`rounded-xl p-3 text-sm ${
                  authMode === "firebase"
                    ? "bg-green-500/10 border border-green-500/30 text-green-400"
                    : "bg-yellow-500/10 border border-yellow-500/30 text-yellow-400"
                }`}>
                  {authMode === "firebase"
                    ? "🔒 Secured with Firebase Phone Auth — Real SMS OTP"
                    : "🧪 Demo mode — OTP shown on screen (add Firebase config for real SMS)"}
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-3 text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <Button
                  id="send-otp-btn"
                  onClick={handleSendOtp}
                  disabled={loading}
                  className="w-full h-12 bg-[#ccff00] hover:bg-[#b8e600] text-black font-semibold rounded-xl text-base"
                >
                  {loading ? "Sending..." : "Send OTP"}
                </Button>

                <p className="text-center text-gray-500 text-sm">
                  {authMode === "firebase"
                    ? "We'll send you a verification code via SMS"
                    : "OTP will be shown on screen for testing"}
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">
                    Verify OTP
                  </h2>
                  <p className="text-gray-400">
                    {authMode === "firebase"
                      ? `Enter the code sent to ${phoneNumber}`
                      : `Enter the test OTP shown below`}
                  </p>
                </div>

                <div>
                  <Label htmlFor="otp" className="text-gray-300">
                    One-Time Password
                  </Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="123456"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    maxLength={6}
                    className="mt-1.5 bg-[#27272a] border-gray-700 text-white placeholder:text-gray-500 h-12 rounded-xl text-center text-2xl tracking-widest focus:border-[#ccff00] focus:ring-[#ccff00]"
                  />
                </div>

                {/* Debug OTP for local mode */}
                {debugOtp && authMode === "local" && (
                  <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-xl p-3 text-yellow-400 text-sm">
                    🧪 Test OTP: <span className="font-mono font-bold text-lg">{debugOtp}</span>
                  </div>
                )}

                {error && (
                  <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-3 text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <Button
                  onClick={handleVerifyOtp}
                  disabled={loading}
                  className="w-full h-12 bg-[#ccff00] hover:bg-[#b8e600] text-black font-semibold rounded-xl text-base"
                >
                  {loading ? "Verifying..." : "Verify & Continue"}
                </Button>

                <button
                  onClick={() => {
                    setStep("phone");
                    setOtp("");
                    setError("");
                    setDebugOtp("");
                    setConfirmationResult(null);
                    recaptchaRef.current = null;
                  }}
                  className="w-full text-gray-400 hover:text-[#ccff00] text-sm transition-colors"
                >
                  Change phone number
                </button>
              </div>
            )}
          </div>

          <p className="text-center text-gray-600 text-xs mt-6">
            By continuing, you agree to our Terms & Privacy Policy
          </p>
        </div>
      </div>

      {/* reCAPTCHA container (invisible) */}
      <div id="recaptcha-container" />
    </div>
  );
}