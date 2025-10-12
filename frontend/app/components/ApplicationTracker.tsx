import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  FileText, 
  Calendar,
  MapPin,
  Phone,
  Mail,
  Download
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { useToast } from './ui/use-toast';

interface ApplicationStatus {
  id: string;
  applicationNumber: string;
  serviceName: string;
  status: 'submitted' | 'under-review' | 'approved' | 'rejected' | 'completed';
  submittedDate: string;
  lastUpdated: string;
  expectedCompletion: string;
  currentStage: string;
  nextAction: string;
  documents: string[];
  trackingSteps: {
    step: string;
    status: 'completed' | 'current' | 'pending';
    date?: string;
    description: string;
  }[];
}

// Sample application data
const sampleApplications: ApplicationStatus[] = [
  {
    id: '1',
    applicationNumber: 'PP2024001234',
    serviceName: 'Passport Application',
    status: 'under-review',
    submittedDate: '2024-01-15',
    lastUpdated: '2024-01-20',
    expectedCompletion: '2024-02-15',
    currentStage: 'Document Verification',
    nextAction: 'Police Verification Pending',
    documents: ['Application Form', 'Address Proof', 'Identity Proof', 'Photographs'],
    trackingSteps: [
      {
        step: 'Application Submitted',
        status: 'completed',
        date: '2024-01-15',
        description: 'Application received and initial processing started'
      },
      {
        step: 'Document Verification',
        status: 'current',
        date: '2024-01-18',
        description: 'Documents are being verified by officials'
      },
      {
        step: 'Police Verification',
        status: 'pending',
        description: 'Background verification process'
      },
      {
        step: 'Passport Printing',
        status: 'pending',
        description: 'Passport will be printed and dispatched'
      },
      {
        step: 'Delivery',
        status: 'pending',
        description: 'Passport will be delivered to your address'
      }
    ]
  },
  {
    id: '2',
    applicationNumber: 'AA2024005678',
    serviceName: 'Aadhaar Update',
    status: 'completed',
    submittedDate: '2024-01-10',
    lastUpdated: '2024-01-25',
    expectedCompletion: '2024-01-25',
    currentStage: 'Completed',
    nextAction: 'Download Updated Aadhaar',
    documents: ['Update Request', 'Supporting Documents'],
    trackingSteps: [
      {
        step: 'Update Request Submitted',
        status: 'completed',
        date: '2024-01-10',
        description: 'Update request received'
      },
      {
        step: 'Document Verification',
        status: 'completed',
        date: '2024-01-15',
        description: 'Documents verified successfully'
      },
      {
        step: 'Data Updated',
        status: 'completed',
        date: '2024-01-25',
        description: 'Aadhaar information updated in database'
      }
    ]
  }
];

export function ApplicationTracker() {
  const [searchQuery, setSearchQuery] = useState('');
  const [applications, setApplications] = useState<ApplicationStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    // Simulate loading applications
    setLoading(true);
    setTimeout(() => {
      setApplications(sampleApplications);
      setLoading(false);
    }, 1000);
  }, []);

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      toast({
        title: "Search Required",
        description: "Please enter an application number",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    // Simulate search
    setTimeout(() => {
      const found = sampleApplications.filter(app => 
        app.applicationNumber.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setApplications(found);
      setLoading(false);
      
      if (found.length === 0) {
        toast({
          title: "No Applications Found",
          description: "Please check your application number and try again"
        });
      }
    }, 800);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'approved': return 'bg-blue-500';
      case 'under-review': return 'bg-yellow-500';
      case 'rejected': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'approved': return CheckCircle;
      case 'under-review': return Clock;
      case 'rejected': return AlertCircle;
      default: return Clock;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-[var(--foreground)] mb-2">Track Your Application</h2>
        <p className="text-[var(--muted-foreground)]">
          Enter your application number to check the current status
        </p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]" />
              <Input
                placeholder="Enter application number (e.g., PP2024001234)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? 'Searching...' : 'Track Application'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Applications */}
      {loading ? (
        <div className="text-center py-8">
          <Clock className="w-8 h-8 animate-spin text-[var(--primary)] mx-auto mb-2" />
          <p className="text-[var(--muted-foreground)]">Loading applications...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {applications.map((app, index) => {
            const StatusIcon = getStatusIcon(app.status);
            
            return (
              <motion.div
                key={app.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card className="border-2">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {app.serviceName}
                          <Badge className={`${getStatusColor(app.status)} text-white`}>
                            {app.status.replace('-', ' ').toUpperCase()}
                          </Badge>
                        </CardTitle>
                        <CardDescription className="mt-1">
                          Application #: {app.applicationNumber}
                        </CardDescription>
                      </div>
                      <StatusIcon className={`w-6 h-6 ${getStatusColor(app.status).replace('bg-', 'text-')}`} />
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    {/* Application Details */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-[var(--muted-foreground)]" />
                        <span>Submitted: {new Date(app.submittedDate).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-[var(--muted-foreground)]" />
                        <span>Expected: {new Date(app.expectedCompletion).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-[var(--muted-foreground)]" />
                        <span>Current: {app.currentStage}</span>
                      </div>
                    </div>

                    {/* Next Action */}
                    <div className="bg-[var(--muted)] p-3 rounded-lg">
                      <h4 className="font-medium text-[var(--foreground)] mb-1">Next Action</h4>
                      <p className="text-sm text-[var(--muted-foreground)]">{app.nextAction}</p>
                    </div>

                    {/* Tracking Steps */}
                    <div>
                      <h4 className="font-medium text-[var(--foreground)] mb-3">Progress Timeline</h4>
                      <div className="space-y-3">
                        {app.trackingSteps.map((step, stepIndex) => (
                          <div key={stepIndex} className="flex items-start gap-3">
                            <div className={`w-3 h-3 rounded-full mt-1 ${
                              step.status === 'completed' ? 'bg-green-500' :
                              step.status === 'current' ? 'bg-blue-500' :
                              'bg-gray-300'
                            }`} />
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <h5 className={`font-medium ${
                                  step.status === 'completed' ? 'text-green-600' :
                                  step.status === 'current' ? 'text-blue-600' :
                                  'text-[var(--muted-foreground)]'
                                }`}>
                                  {step.step}
                                </h5>
                                {step.date && (
                                  <span className="text-xs text-[var(--muted-foreground)]">
                                    {new Date(step.date).toLocaleDateString()}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-[var(--muted-foreground)]">
                                {step.description}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        Download Receipt
                      </Button>
                      <Button variant="outline" size="sm">
                        <Phone className="w-4 h-4 mr-1" />
                        Contact Support
                      </Button>
                      {app.status === 'completed' && (
                        <Button size="sm">
                          <Download className="w-4 h-4 mr-1" />
                          Download Document
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {applications.length === 0 && !loading && (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-[var(--muted-foreground)] mx-auto mb-4" />
          <h3 className="text-xl font-medium text-[var(--foreground)] mb-2">No Applications Found</h3>
          <p className="text-[var(--muted-foreground)] mb-4">
            Enter your application number above to track your government service applications
          </p>
          <Button variant="outline" onClick={() => setApplications(sampleApplications)}>
            View Sample Applications
          </Button>
        </div>
      )}
    </div>
  );
}
