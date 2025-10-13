import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  CheckCircle2,
  Clock,
  FileText,
  Upload,
  CreditCard,
  Truck,
  Package,
  MapPin,
  Calendar,
  Download,
  Share2,
  AlertCircle,
  Info,
  ChevronDown,
  ChevronUp,
  ArrowLeft,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import { Alert, AlertDescription } from '../ui/alert';
import { Card3D } from '../animations/Card3D';

interface ApplicationTrackerProps {
  onNavigate: (page: string) => void;
  applicationId?: string;
}

export function ApplicationTracker({ onNavigate, applicationId = 'APP001' }: ApplicationTrackerProps) {
  const [expandedStep, setExpandedStep] = useState<number | null>(2);

  // Mock application data
  const application = {
    id: applicationId,
    service: 'Passport Services',
    type: 'New Passport Application',
    applicantName: 'Rajesh Kumar Singh',
    submittedDate: '2024-01-15',
    expectedDate: '2024-02-05',
    currentStep: 2,
    progress: 65,
    status: 'In Progress',
    referenceNumber: 'PS-2024-MUM-123456',
  };

  const steps = [
    {
      id: 0,
      title: 'Application Submitted',
      description: 'Your application has been received and assigned a reference number',
      status: 'completed',
      icon: FileText,
      date: '2024-01-15',
      time: '10:30 AM',
      details: [
        'Application ID: APP001',
        'Reference Number: PS-2024-MUM-123456',
        'Fee Paid: ₹1,500',
        'Documents Uploaded: 4/4',
      ],
    },
    {
      id: 1,
      title: 'Document Verification',
      description: 'Your documents are being verified by our team',
      status: 'completed',
      icon: Upload,
      date: '2024-01-16',
      time: '02:15 PM',
      details: [
        'Identity Proof: ✓ Verified',
        'Address Proof: ✓ Verified',
        'Birth Certificate: ✓ Verified',
        'Photographs: ✓ Verified',
      ],
    },
    {
      id: 2,
      title: 'Police Verification',
      description: 'Police verification is in progress at your registered address',
      status: 'in-progress',
      icon: MapPin,
      date: '2024-01-20',
      time: 'Pending',
      details: [
        'Police Station: Andheri West',
        'Assigned Officer: Constable Sharma',
        'Visit Scheduled: 2024-01-25',
        'Expected Completion: 2024-01-27',
      ],
      alert: {
        type: 'info',
        message: 'Please ensure someone is available at the registered address on the scheduled date.',
      },
    },
    {
      id: 3,
      title: 'Printing & Quality Check',
      description: 'Your passport is being printed and quality checked',
      status: 'pending',
      icon: Package,
      date: 'Pending',
      time: 'N/A',
      details: [
        'Printing Status: Awaiting verification',
        'Quality Check: Pending',
        'Dispatch Preparation: Not started',
      ],
    },
    {
      id: 4,
      title: 'Dispatch & Delivery',
      description: 'Your passport will be dispatched to your address',
      status: 'pending',
      icon: Truck,
      date: 'Pending',
      time: 'N/A',
      details: [
        'Courier Partner: India Post',
        'Tracking Number: Will be updated',
        'Delivery Address: As per application',
        'Expected Delivery: 2024-02-05',
      ],
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-[var(--accent)]';
      case 'in-progress':
        return 'bg-[var(--secondary)]';
      case 'pending':
        return 'bg-[var(--muted)]';
      default:
        return 'bg-[var(--muted)]';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle2;
      case 'in-progress':
        return Clock;
      case 'pending':
        return Clock;
      default:
        return Clock;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20">
      <div className="max-w-5xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Button
            variant="ghost"
            onClick={() => onNavigate('dashboard')}
            className="mb-4 -ml-2"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-[var(--foreground)] mb-2">
                Application Tracker
              </h1>
              <p className="text-[var(--muted-foreground)]">
                Track your {application.service} application status
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="icon">
                <Download className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Share2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Application Info Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Card3D intensity={10}>
            <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-12)] bg-gradient-to-br from-[var(--card)] to-[var(--background-secondary)]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl">{application.service}</CardTitle>
                    <CardDescription>{application.type}</CardDescription>
                  </div>
                  <Badge className="bg-[var(--secondary)] text-white text-base px-4 py-2">
                    {application.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-[var(--muted-foreground)]">Overall Progress</span>
                    <span className="font-bold text-[var(--foreground)] text-lg">{application.progress}%</span>
                  </div>
                  <Progress value={application.progress} className="h-3" />
                </div>

                <Separator />

                {/* Application Details */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-xs text-[var(--muted-foreground)] mb-1">Applicant</div>
                    <div className="font-semibold text-[var(--foreground)]">{application.applicantName}</div>
                  </div>
                  <div>
                    <div className="text-xs text-[var(--muted-foreground)] mb-1">Application ID</div>
                    <div className="font-semibold text-[var(--foreground)]">{application.id}</div>
                  </div>
                  <div>
                    <div className="text-xs text-[var(--muted-foreground)] mb-1">Submitted</div>
                    <div className="font-semibold text-[var(--foreground)]">{application.submittedDate}</div>
                  </div>
                  <div>
                    <div className="text-xs text-[var(--muted-foreground)] mb-1">Expected</div>
                    <div className="font-semibold text-[var(--foreground)]">{application.expectedDate}</div>
                  </div>
                </div>

                <Separator />

                {/* Reference Number */}
                <div className="bg-[var(--muted)]/30 rounded-[var(--radius-lg)] p-4 border border-[var(--border)]">
                  <div className="text-xs text-[var(--muted-foreground)] mb-1">Reference Number</div>
                  <div className="font-mono font-bold text-[var(--foreground)] text-lg">
                    {application.referenceNumber}
                  </div>
                </div>
              </CardContent>
            </Card>
          </Card3D>
        </motion.div>

        {/* Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)]">
            <CardHeader>
              <CardTitle>Application Timeline</CardTitle>
              <CardDescription>Detailed status of each step in your application</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-[var(--border)]" />

                {/* Steps */}
                <div className="space-y-6">
                  {steps.map((step, index) => {
                    const StatusIcon = getStatusIcon(step.status);
                    const isExpanded = expandedStep === step.id;

                    return (
                      <motion.div
                        key={step.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 + index * 0.1 }}
                        className="relative"
                      >
                        {/* Timeline dot */}
                        <div className={`absolute left-0 w-12 h-12 rounded-full flex items-center justify-center shadow-[var(--shadow-4)] ${getStatusColor(step.status)}`}>
                          <StatusIcon className="w-6 h-6 text-white" />
                        </div>

                        {/* Step content */}
                        <div className="ml-20">
                          <div
                            className={`p-6 rounded-[var(--radius-xl)] border-2 transition-all cursor-pointer ${
                              step.status === 'in-progress'
                                ? 'border-[var(--secondary)] bg-[var(--secondary)]/5'
                                : step.status === 'completed'
                                ? 'border-[var(--accent)]/30 bg-[var(--accent)]/5'
                                : 'border-[var(--border)] bg-[var(--muted)]/20'
                            } hover:shadow-[var(--shadow-4)]`}
                            onClick={() => setExpandedStep(isExpanded ? null : step.id)}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h3 className="font-bold text-[var(--foreground)] text-lg">
                                    {step.title}
                                  </h3>
                                  {step.status === 'completed' && (
                                    <Badge className="bg-[var(--accent)] text-white">
                                      Completed
                                    </Badge>
                                  )}
                                  {step.status === 'in-progress' && (
                                    <Badge className="bg-[var(--secondary)] text-white">
                                      In Progress
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-[var(--muted-foreground)] text-sm">
                                  {step.description}
                                </p>
                              </div>
                              <div className="flex items-center gap-4">
                                <div className="text-right">
                                  <div className="text-sm font-semibold text-[var(--foreground)]">
                                    {step.date}
                                  </div>
                                  <div className="text-xs text-[var(--muted-foreground)]">
                                    {step.time}
                                  </div>
                                </div>
                                <Button variant="ghost" size="icon" className="flex-shrink-0">
                                  {isExpanded ? (
                                    <ChevronUp className="w-5 h-5" />
                                  ) : (
                                    <ChevronDown className="w-5 h-5" />
                                  )}
                                </Button>
                              </div>
                            </div>

                            {/* Expanded details */}
                            <AnimatePresence>
                              {isExpanded && (
                                <motion.div
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  exit={{ opacity: 0, height: 0 }}
                                  transition={{ duration: 0.2 }}
                                  className="overflow-hidden"
                                >
                                  <Separator className="my-4" />
                                  
                                  {/* Alert if present */}
                                  {step.alert && (
                                    <Alert className="mb-4 border-l-4 border-[var(--info)] bg-[var(--info-bg)]">
                                      <Info className="w-4 h-4 text-[var(--info)]" />
                                      <AlertDescription>{step.alert.message}</AlertDescription>
                                    </Alert>
                                  )}

                                  {/* Details list */}
                                  <div className="space-y-2">
                                    {step.details.map((detail, idx) => (
                                      <div
                                        key={idx}
                                        className="flex items-start gap-2 text-sm"
                                      >
                                        <CheckCircle2 className="w-4 h-4 text-[var(--accent)] flex-shrink-0 mt-0.5" />
                                        <span className="text-[var(--foreground)]">{detail}</span>
                                      </div>
                                    ))}
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Help Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <Card className="border-2 border-[var(--card-border)] bg-gradient-to-br from-[var(--primary)] to-[var(--primary-hover)] text-white">
            <CardHeader>
              <CardTitle className="text-white">Need Help?</CardTitle>
              <CardDescription className="text-white/80">
                Our support team is here to assist you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button
                  variant="secondary"
                  className="h-auto py-4 flex-col gap-2 bg-white/10 hover:bg-white/20 text-white border-white/20"
                >
                  <Info className="w-6 h-6" />
                  <span className="text-sm">FAQs</span>
                </Button>
                <Button
                  variant="secondary"
                  className="h-auto py-4 flex-col gap-2 bg-white/10 hover:bg-white/20 text-white border-white/20"
                >
                  <Calendar className="w-6 h-6" />
                  <span className="text-sm">Schedule Call</span>
                </Button>
                <Button
                  variant="secondary"
                  className="h-auto py-4 flex-col gap-2 bg-white/10 hover:bg-white/20 text-white border-white/20"
                >
                  <AlertCircle className="w-6 h-6" />
                  <span className="text-sm">Report Issue</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
