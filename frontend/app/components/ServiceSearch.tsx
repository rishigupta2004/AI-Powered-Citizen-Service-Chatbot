import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Star, 
  Clock, 
  Users, 
  MapPin, 
  ExternalLink,
  FileText,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { useToast } from './ui/use-toast';

interface Service {
  id: string;
  name: string;
  description: string;
  category: string;
  ministry: string;
  processingTime: string;
  fees: string;
  rating: number;
  applicationsToday: number;
  difficulty: 'easy' | 'medium' | 'hard';
  requirements: string[];
  steps: string[];
  onlineAvailable: boolean;
}

const sampleServices: Service[] = [
  {
    id: 'passport-fresh',
    name: 'Fresh Passport Application',
    description: 'Apply for a new Indian passport for travel abroad',
    category: 'passport',
    ministry: 'Ministry of External Affairs',
    processingTime: '15-30 days',
    fees: '₹1,500 - ₹3,500',
    rating: 4.5,
    applicationsToday: 1247,
    difficulty: 'medium',
    requirements: [
      'Proof of Date of Birth',
      'Address Proof',
      'Identity Proof',
      'Passport Size Photographs'
    ],
    steps: [
      'Fill online application',
      'Schedule appointment',
      'Visit Passport Office',
      'Document verification',
      'Police verification',
      'Passport dispatch'
    ],
    onlineAvailable: true
  },
  {
    id: 'aadhaar-enrollment',
    name: 'Aadhaar Enrollment',
    description: 'Get your unique 12-digit Aadhaar number',
    category: 'aadhaar',
    ministry: 'UIDAI',
    processingTime: '60-90 days',
    fees: 'Free',
    rating: 4.2,
    applicationsToday: 2341,
    difficulty: 'easy',
    requirements: [
      'Proof of Identity',
      'Proof of Address',
      'Date of Birth Proof'
    ],
    steps: [
      'Visit Aadhaar Center',
      'Fill enrollment form',
      'Biometric capture',
      'Document verification',
      'Receive acknowledgment',
      'Get Aadhaar by post'
    ],
    onlineAvailable: false
  },
  {
    id: 'pan-application',
    name: 'PAN Card Application',
    description: 'Apply for Permanent Account Number card',
    category: 'pan',
    ministry: 'Income Tax Department',
    processingTime: '10-15 days',
    fees: '₹107',
    rating: 4.3,
    applicationsToday: 892,
    difficulty: 'easy',
    requirements: [
      'Identity Proof',
      'Address Proof',
      'Date of Birth Proof',
      'Passport Size Photo'
    ],
    steps: [
      'Fill Form 49A online',
      'Upload documents',
      'Make payment',
      'Submit application',
      'Receive PAN by post'
    ],
    onlineAvailable: true
  },
  {
    id: 'driving-license',
    name: 'Driving License',
    description: 'Apply for driving license for various vehicle categories',
    category: 'transport',
    ministry: 'Ministry of Road Transport',
    processingTime: '7-15 days',
    fees: '₹200 - ₹1,000',
    rating: 4.0,
    applicationsToday: 567,
    difficulty: 'medium',
    requirements: [
      'Age Proof (18+ for car)',
      'Address Proof',
      'Medical Certificate',
      'Passport Size Photos',
      'Learner\'s License'
    ],
    steps: [
      'Get Learner\'s License',
      'Practice driving',
      'Book driving test',
      'Pass driving test',
      'Submit documents',
      'Receive license'
    ],
    onlineAvailable: true
  }
];

export function ServiceSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const categories = ['all', 'passport', 'aadhaar', 'pan', 'transport'];

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      let filtered = sampleServices;
      
      if (selectedCategory !== 'all') {
        filtered = filtered.filter(service => service.category === selectedCategory);
      }
      
      if (searchQuery.trim()) {
        filtered = filtered.filter(service =>
          service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          service.description.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }
      
      setServices(filtered);
      setLoading(false);
    }, 500);
  }, [searchQuery, selectedCategory]);

  const handleApply = (service: Service) => {
    toast({
      title: "Application Started",
      description: `Starting application for ${service.name}`,
    });
    
    if (service.onlineAvailable) {
      // In a real app, this would navigate to the application form
      window.open(`/apply/${service.id}`, '_blank');
    } else {
      toast({
        title: "Visit Center Required",
        description: "This service requires visiting a government center",
      });
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'hard': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-[var(--foreground)] mb-2">Government Services</h2>
        <p className="text-[var(--muted-foreground)]">
          Search and apply for government services online
        </p>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]" />
              <Input
                placeholder="Search services (e.g., passport, aadhaar, pan)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="flex gap-2">
              {categories.map(category => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Services Grid */}
      {loading ? (
        <div className="text-center py-8">
          <Clock className="w-8 h-8 animate-spin text-[var(--primary)] mx-auto mb-2" />
          <p className="text-[var(--muted-foreground)]">Loading services...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {services.map((service, index) => (
            <motion.div
              key={service.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow border-2 hover:border-[var(--primary)]/20">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{service.name}</CardTitle>
                      <CardDescription className="text-sm mb-3">
                        {service.description}
                      </CardDescription>
                      
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary" className="text-xs">
                          {service.ministry}
                        </Badge>
                        <Badge className={`text-xs ${getDifficultyColor(service.difficulty)}`}>
                          {service.difficulty}
                        </Badge>
                        {service.onlineAvailable && (
                          <Badge className="bg-blue-100 text-blue-800 border-blue-200 text-xs">
                            Online Available
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Service Stats */}
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <Clock className="w-4 h-4 text-[var(--muted-foreground)] mx-auto mb-1" />
                      <div className="font-medium">{service.processingTime}</div>
                      <div className="text-xs text-[var(--muted-foreground)]">Processing</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">{service.fees}</div>
                      <div className="text-xs text-[var(--muted-foreground)]">Fees</div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        <span className="font-medium">{service.rating}</span>
                      </div>
                      <div className="text-xs text-[var(--muted-foreground)]">Rating</div>
                    </div>
                  </div>

                  {/* Today's Applications */}
                  <div className="flex items-center justify-center gap-2 text-sm text-[var(--muted-foreground)]">
                    <Users className="w-4 h-4" />
                    {service.applicationsToday} applications today
                  </div>

                  {/* Requirements Preview */}
                  <div>
                    <h4 className="font-medium text-sm mb-2">Required Documents:</h4>
                    <div className="space-y-1">
                      {service.requirements.slice(0, 3).map((req, reqIndex) => (
                        <div key={reqIndex} className="flex items-center gap-2 text-xs">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          {req}
                        </div>
                      ))}
                      {service.requirements.length > 3 && (
                        <div className="text-xs text-[var(--muted-foreground)]">
                          +{service.requirements.length - 3} more requirements
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2">
                    <Button 
                      onClick={() => handleApply(service)}
                      className="flex-1"
                    >
                      {service.onlineAvailable ? 'Apply Online' : 'Find Center'}
                      <ExternalLink className="w-4 h-4 ml-1" />
                    </Button>
                    
                    <Button variant="outline" size="sm" className="px-3">
                      <FileText className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {services.length === 0 && !loading && (
        <div className="text-center py-12">
          <Search className="w-16 h-16 text-[var(--muted-foreground)] mx-auto mb-4" />
          <h3 className="text-xl font-medium text-[var(--foreground)] mb-2">No Services Found</h3>
          <p className="text-[var(--muted-foreground)] mb-4">
            Try adjusting your search terms or category filter
          </p>
          <Button variant="outline" onClick={() => {setSearchQuery(''); setSelectedCategory('all');}}>
            Show All Services
          </Button>
        </div>
      )}
    </div>
  );
}
