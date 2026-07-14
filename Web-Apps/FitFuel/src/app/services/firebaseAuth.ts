import { initializeApp } from "firebase/app";
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber, type ConfirmationResult } from "firebase/auth";

// @ts-ignore - Vite injects import.meta.env at build time
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "",
};

// Only initialize if config is present
const isFirebaseConfigured = !!firebaseConfig.apiKey && firebaseConfig.apiKey !== "";

let app: any = null;
let auth: any = null;

if (isFirebaseConfigured) {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
}

export { auth, isFirebaseConfigured };
export type { ConfirmationResult };

// Setup invisible reCAPTCHA
export function setupRecaptcha(buttonId: string): RecaptchaVerifier | null {
  if (!auth) return null;

  const verifier = new RecaptchaVerifier(auth, buttonId, {
    size: "invisible",
    callback: () => {
      // reCAPTCHA solved
    },
  });

  return verifier;
}

// Send OTP via Firebase
export async function sendFirebaseOtp(
  phoneNumber: string,
  recaptchaVerifier: RecaptchaVerifier
): Promise<ConfirmationResult> {
  if (!auth) throw new Error("Firebase not configured");

  // Ensure phone number has country code
  let formattedPhone = phoneNumber.trim();
  if (!formattedPhone.startsWith("+")) {
    // Default to India (+91) if no country code
    formattedPhone = "+91" + formattedPhone.replace(/^0/, "");
  }

  return signInWithPhoneNumber(auth, formattedPhone, recaptchaVerifier);
}

// Verify OTP
export async function verifyFirebaseOtp(
  confirmationResult: ConfirmationResult,
  otp: string
) {
  const result = await confirmationResult.confirm(otp);
  return result.user;
}
