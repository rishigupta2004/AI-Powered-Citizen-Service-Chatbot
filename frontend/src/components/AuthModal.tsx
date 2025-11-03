import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  X,
  Phone,
  CreditCard,
  Mail,
  Lock,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ShieldCheck,
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { toast } from 'sonner@2.0.3';
import { useAuth } from './AuthContext';
import { Logo } from './Logo';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type AuthMethod = 'phone' | 'aadhaar' | 'google';
type AuthStep = 'method' | 'input' | 'otp' | 'profile';

export function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [authMethod, setAuthMethod] = useState<AuthMethod | null>(null);
  const [authStep, setAuthStep] = useState<AuthStep>('method');
  const [inputValue, setInputValue] = useState('');
  const [otp, setOtp] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [otpTimer, setOtpTimer] = useState(0);
  const { login } = useAuth();

  // OTP timer countdown
  useEffect(() => {
    if (otpTimer > 0) {
      const timer = setTimeout(() => setOtpTimer(otpTimer - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [otpTimer]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => {
        setAuthMethod(null);
        setAuthStep('method');
        setInputValue('');
        setOtp('');
        setName('');
        setEmail('');
        setOtpTimer(0);
      }, 300);
    }
  }, [isOpen]);

  const handleMethodSelect = (method: AuthMethod) => {
    setAuthMethod(method);
    if (method === 'google') {
      handleGoogleLogin();
    } else {
      setAuthStep('input');
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    // Simulate Google OAuth
    setTimeout(() => {
      const mockUser = {
        id: 'G' + Math.random().toString(36).substr(2, 9),
        name: 'Rajesh Kumar',
        email: 'rajesh.kumar@gmail.com',
        loginMethod: 'google' as const,
        avatar: 'https://ui-avatars.com/api/?name=Rajesh+Kumar&background=000080&color=fff',
        verified: true,
      };
      login(mockUser);
      setIsLoading(false);
      toast.success('Successfully logged in with Google!');
      onSuccess?.();
      onClose();
    }, 1500);
  };

  const validateInput = (): boolean => {
    if (authMethod === 'phone') {
      const phoneRegex = /^[6-9]\d{9}$/;
      if (!phoneRegex.test(inputValue)) {
        toast.error('Please enter a valid 10-digit mobile number');
        return false;
      }
    } else if (authMethod === 'aadhaar') {
      const aadhaarRegex = /^\d{12}$/;
      if (!aadhaarRegex.test(inputValue.replace(/\s/g, ''))) {
        toast.error('Please enter a valid 12-digit Aadhaar number');
        return false;
      }
    }
    return true;
  };

  const handleSendOTP = async () => {
    if (!validateInput()) return;

    setIsLoading(true);
    // Simulate OTP sending
    setTimeout(() => {
      setIsLoading(false);
      setAuthStep('otp');
      setOtpTimer(30);
      toast.success('OTP sent successfully!');
    }, 1000);
  };

  const handleVerifyOTP = async () => {
    if (otp.length !== 6) {
      toast.error('Please enter a valid 6-digit OTP');
      return;
    }

    setIsLoading(true);
    // Simulate OTP verification
    setTimeout(() => {
      setIsLoading(false);
      setAuthStep('profile');
    }, 1000);
  };

  const handleCompleteSignup = async () => {
    if (!name.trim()) {
      toast.error('Please enter your name');
      return;
    }

    setIsLoading(true);
    // Simulate user creation
    setTimeout(() => {
      const mockUser = {
        id: authMethod === 'phone' ? 'P' : 'A' + Math.random().toString(36).substr(2, 9),
        name: name,
        email: email || undefined,
        phone: authMethod === 'phone' ? inputValue : undefined,
        aadhaar: authMethod === 'aadhaar' ? inputValue : undefined,
        loginMethod: authMethod as 'phone' | 'aadhaar' | 'google',
        verified: true,
      };
      login(mockUser);
      setIsLoading(false);
      toast.success(`Welcome to Seva Sindhu, ${name}!`);
      onSuccess?.();
      onClose();
    }, 1000);
  };

  const handleResendOTP = () => {
    if (otpTimer > 0) return;
    setOtpTimer(30);
    toast.success('OTP resent successfully!');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[var(--z-modal)]"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed inset-0 flex items-center justify-center z-[var(--z-modal)] p-4"
          >
            <Card className="w-full max-w-md bg-[var(--card)] border-2 border-[var(--border)] shadow-2xl max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <CardHeader className="relative pb-6 border-b border-[var(--border)]">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="absolute right-4 top-4 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  aria-label="Close"
                >
                  <X className="w-5 h-5" />
                </Button>
                
                <div className="flex flex-col items-center">
                  <div className="mb-4">
                    <Logo size="lg" showText={false} />
                  </div>
                  <CardTitle className="text-2xl text-center text-[var(--foreground)]">
                    {authStep === 'method' && 'Welcome to Seva Sindhu'}
                    {authStep === 'input' && 'Enter Details'}
                    {authStep === 'otp' && 'Verify OTP'}
                    {authStep === 'profile' && 'Complete Profile'}
                  </CardTitle>
                  <CardDescription className="text-center mt-2 text-[var(--muted-foreground)]">
                    {authStep === 'method' && 'Login or create your account to access government services'}
                    {authStep === 'input' && 'We will send you a verification code'}
                    {authStep === 'otp' && 'Enter the 6-digit code sent to your device'}
                    {authStep === 'profile' && 'Tell us a bit about yourself'}
                  </CardDescription>
                </div>
              </CardHeader>

              <CardContent className="pt-6">
                {/* Method Selection */}
                {authStep === 'method' && (
                  <div className="space-y-4">
                    <Button
                      onClick={() => handleMethodSelect('phone')}
                      variant="outline"
                      className="w-full h-auto py-4 justify-start border-2 border-[var(--border)] hover:border-[#000080] hover:bg-[#000080]/5 transition-all group"
                    >
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                        <Phone className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 text-left">
                        <div className="font-semibold text-[var(--foreground)]">Mobile Number</div>
                        <div className="text-sm text-[var(--muted-foreground)]">Login with your phone number</div>
                      </div>
                      <ArrowRight className="w-5 h-5 text-[var(--muted-foreground)] group-hover:text-[#000080] group-hover:translate-x-1 transition-all" />
                    </Button>

                    <Button
                      onClick={() => handleMethodSelect('aadhaar')}
                      variant="outline"
                      className="w-full h-auto py-4 justify-start border-2 border-[var(--border)] hover:border-[#000080] hover:bg-[#000080]/5 transition-all group"
                    >
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                        <CreditCard className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 text-left">
                        <div className="font-semibold text-[var(--foreground)]">Aadhaar Card</div>
                        <div className="text-sm text-[var(--muted-foreground)]">Login with your Aadhaar number</div>
                      </div>
                      <ArrowRight className="w-5 h-5 text-[var(--muted-foreground)] group-hover:text-[#000080] group-hover:translate-x-1 transition-all" />
                    </Button>

                    <div className="relative">
                      <Separator className="my-6" />
                      <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-[var(--card)] px-3 text-sm text-[var(--muted-foreground)]">
                        or
                      </span>
                    </div>

                    <Button
                      onClick={() => handleMethodSelect('google')}
                      variant="outline"
                      disabled={isLoading}
                      className="w-full h-auto py-4 justify-start border-2 border-[var(--border)] hover:border-[#000080] hover:bg-[#000080]/5 transition-all group"
                    >
                      {isLoading ? (
                        <Loader2 className="w-6 h-6 animate-spin mr-4" />
                      ) : (
                        <>
                          <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                            <Mail className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1 text-left">
                            <div className="font-semibold text-[var(--foreground)]">Google Account</div>
                            <div className="text-sm text-[var(--muted-foreground)]">Continue with Gmail</div>
                          </div>
                          <ArrowRight className="w-5 h-5 text-[var(--muted-foreground)] group-hover:text-[#000080] group-hover:translate-x-1 transition-all" />
                        </>
                      )}
                    </Button>

                    <div className="mt-6 p-4 bg-[var(--muted)]/30 rounded-xl border border-[var(--border)]">
                      <div className="flex items-start gap-3">
                        <ShieldCheck className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-[var(--muted-foreground)]">
                          <div className="font-medium text-[var(--foreground)] mb-1">Secure Authentication</div>
                          Your data is encrypted and protected. We never share your information with third parties.
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Input Step */}
                {authStep === 'input' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-[#000080] to-[#000066] rounded-2xl flex items-center justify-center">
                        {authMethod === 'phone' ? (
                          <Phone className="w-8 h-8 text-white" />
                        ) : (
                          <CreditCard className="w-8 h-8 text-white" />
                        )}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="input-value" className="text-[var(--foreground)]">
                        {authMethod === 'phone' ? 'Mobile Number' : 'Aadhaar Number'}
                      </Label>
                      <Input
                        id="input-value"
                        type="tel"
                        placeholder={authMethod === 'phone' ? '98765 43210' : '1234 5678 9012'}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        className="h-12 text-lg bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                        maxLength={authMethod === 'phone' ? 10 : 14}
                      />
                      <p className="text-xs text-[var(--muted-foreground)]">
                        {authMethod === 'phone' 
                          ? 'Enter your 10-digit mobile number without country code'
                          : 'Enter your 12-digit Aadhaar number'
                        }
                      </p>
                    </div>

                    <div className="flex gap-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => setAuthStep('method')}
                        className="flex-1 border-[var(--border)] text-[var(--foreground)]"
                      >
                        Back
                      </Button>
                      <Button
                        onClick={handleSendOTP}
                        disabled={isLoading}
                        className="flex-1 bg-gradient-to-r from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] text-white"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Sending...
                          </>
                        ) : (
                          <>
                            Send OTP
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )}

                {/* OTP Verification Step */}
                {authStep === 'otp' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center">
                        <Lock className="w-8 h-8 text-white" />
                      </div>
                    </div>

                    <div className="text-center mb-6">
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Code sent to <span className="font-medium text-[var(--foreground)]">
                          {authMethod === 'phone' 
                            ? `+91 ${inputValue.slice(0, 5)}*****`
                            : `Aadhaar ending ${inputValue.slice(-4)}`
                          }
                        </span>
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="otp" className="text-[var(--foreground)]">Enter OTP</Label>
                      <Input
                        id="otp"
                        type="tel"
                        placeholder="000000"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        className="h-14 text-2xl text-center tracking-widest font-mono bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                        maxLength={6}
                        autoComplete="one-time-code"
                      />
                      {otpTimer > 0 ? (
                        <p className="text-xs text-center text-[var(--muted-foreground)]">
                          Resend OTP in {otpTimer}s
                        </p>
                      ) : (
                        <button
                          onClick={handleResendOTP}
                          className="text-xs text-center w-full text-[#000080] hover:underline"
                        >
                          Didn't receive code? Resend OTP
                        </button>
                      )}
                    </div>

                    <div className="flex gap-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => setAuthStep('input')}
                        className="flex-1 border-[var(--border)] text-[var(--foreground)]"
                      >
                        Back
                      </Button>
                      <Button
                        onClick={handleVerifyOTP}
                        disabled={isLoading || otp.length !== 6}
                        className="flex-1 bg-gradient-to-r from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] text-white"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Verifying...
                          </>
                        ) : (
                          <>
                            Verify
                            <CheckCircle2 className="w-4 h-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )}

                {/* Profile Completion Step */}
                {authStep === 'profile' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-[#FF9933] to-[#FF7700] rounded-2xl flex items-center justify-center">
                        <CheckCircle2 className="w-8 h-8 text-white" />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="name" className="text-[var(--foreground)]">
                          Full Name <span className="text-red-500">*</span>
                        </Label>
                        <Input
                          id="name"
                          type="text"
                          placeholder="Enter your full name"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          className="h-12 bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-[var(--foreground)]">
                          Email (Optional)
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          placeholder="your.email@example.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="h-12 bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                        />
                      </div>
                    </div>

                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-xl border border-blue-200 dark:border-blue-800">
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-blue-900 dark:text-blue-100">
                          <div className="font-medium mb-1">Verification Complete</div>
                          Your {authMethod === 'phone' ? 'mobile number' : 'Aadhaar'} has been verified successfully.
                        </div>
                      </div>
                    </div>

                    <Button
                      onClick={handleCompleteSignup}
                      disabled={isLoading || !name.trim()}
                      className="w-full h-12 bg-gradient-to-r from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] text-white text-lg"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin mr-2" />
                          Creating Account...
                        </>
                      ) : (
                        <>
                          Get Started
                          <ArrowRight className="w-5 h-5 ml-2" />
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
