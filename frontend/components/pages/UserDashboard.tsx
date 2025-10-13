import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Calendar,
  Bell,
  Settings,
  Download,
  Eye,
  MoreVertical,
  Filter,
  Search,
  Upload,
  MapPin,
  Phone,
  Mail,
  CreditCard,
  ExternalLink,
  ArrowRight,
  Sparkles,
  Award,
  Shield,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Input } from '../ui/input';
import { Card3D } from '../animations/Card3D';
import { FloatingElements } from '../animations/FloatingElements';

interface UserDashboardProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function UserDashboard({ onNavigate }: UserDashboardProps) {
  const [selectedTab, setSelectedTab] = useState('overview');

  const stats = [
    {
      label: 'Active Applications',
      value: '3',
      change: '+2 this month',
      icon: FileText,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-950/20',
      textColor: 'text-blue-600 dark:text-blue-400',
    },
    {
      label: 'Completed',
      value: '12',
      change: '+5 this month',
      icon: CheckCircle2,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50 dark:bg-green-950/20',
      textColor: 'text-green-600 dark:text-green-400',
    },
    {
      label: 'Pending Review',
      value: '2',
      change: 'Requires action',
      icon: Clock,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50 dark:bg-orange-950/20',
      textColor: 'text-orange-600 dark:text-orange-400',
    },
    {
      label: 'Documents',
      value: '24',
      change: '8 verified',
      icon: Shield,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-950/20',
      textColor: 'text-purple-600 dark:text-purple-400',
    },
  ];

  const applications = [
    {
      id: 'APP001',
      service: 'Passport Services',
      status: 'In Progress',
      progress: 65,
      submittedDate: '2024-01-15',
      lastUpdate: '2 days ago',
      nextStep: 'Document Verification',
      priority: 'high',
      statusColor: 'bg-blue-500',
      gradient: 'from-blue-500 to-blue-600',
    },
    {
      id: 'APP002',
      service: 'Driving License',
      status: 'Pending',
      progress: 30,
      submittedDate: '2024-01-20',
      lastUpdate: '5 hours ago',
      nextStep: 'Payment Required',
      priority: 'medium',
      statusColor: 'bg-orange-500',
      gradient: 'from-orange-500 to-orange-600',
    },
    {
      id: 'APP003',
      service: 'PAN Card Update',
      status: 'Completed',
      progress: 100,
      submittedDate: '2024-01-10',
      lastUpdate: '1 week ago',
      nextStep: 'Collect Document',
      priority: 'low',
      statusColor: 'bg-green-500',
      gradient: 'from-green-500 to-green-600',
    },
  ];

  const recentActivity = [
    {
      action: 'Document uploaded',
      service: 'Passport Services',
      time: '2 hours ago',
      icon: Upload,
      color: 'text-blue-600 dark:text-blue-400',
    },
    {
      action: 'Application submitted',
      service: 'Driving License',
      time: '5 hours ago',
      icon: CheckCircle2,
      color: 'text-green-600 dark:text-green-400',
    },
    {
      action: 'Payment completed',
      service: 'PAN Card Update',
      time: '1 day ago',
      icon: CreditCard,
      color: 'text-purple-600 dark:text-purple-400',
    },
    {
      action: 'Status updated',
      service: 'Passport Services',
      time: '2 days ago',
      icon: Bell,
      color: 'text-orange-600 dark:text-orange-400',
    },
  ];

  const userProfile = {
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@example.com',
    phone: '+91 98765 43210',
    aadhaar: 'XXXX XXXX 1234',
    address: 'Mumbai, Maharashtra',
    memberSince: 'January 2023',
    verificationLevel: 'Verified',
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20 relative overflow-hidden">
      {/* Background decorations */}
      <FloatingElements count={6} className="opacity-30" />

      <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-6">
            <div>
              <h1 className="text-4xl font-bold text-[var(--foreground)] mb-2">
                Welcome back, {userProfile.name.split(' ')[0]}! 👋
              </h1>
              <p className="text-[var(--muted-foreground)]">
                Track and manage all your government service applications in one place
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="icon" className="relative">
                <Bell className="w-5 h-5 text-[var(--foreground)]" />
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-[#FF9933] rounded-full text-white text-xs flex items-center justify-center">
                  3
                </span>
              </Button>
              <Button variant="outline" size="icon">
                <Settings className="w-5 h-5 text-[var(--foreground)]" />
              </Button>
              <Avatar className="w-12 h-12 border-2 border-[#000080]">
                <AvatarFallback className="bg-gradient-to-br from-[#000080] to-[#000066] text-white">
                  {userProfile.name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
            </div>
          </div>

          {/* Profile Summary Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="border-2 border-[var(--border)] bg-gradient-to-br from-[#000080] to-[#000066] text-white shadow-xl">
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-white/80" />
                    <div>
                      <div className="text-xs text-white/80">Email</div>
                      <div className="font-medium">{userProfile.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone className="w-5 h-5 text-white/80" />
                    <div>
                      <div className="text-xs text-white/80">Phone</div>
                      <div className="font-medium">{userProfile.phone}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <CreditCard className="w-5 h-5 text-white/80" />
                    <div>
                      <div className="text-xs text-white/80">Aadhaar</div>
                      <div className="font-medium">{userProfile.aadhaar}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Award className="w-5 h-5 text-white/80" />
                    <div>
                      <div className="text-xs text-white/80">Status</div>
                      <Badge className="bg-green-500 text-white border-0 mt-1">
                        {userProfile.verificationLevel}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
            >
              <Card3D intensity={10}>
                <Card className="border-2 border-[var(--border)] shadow-lg hover:shadow-xl transition-shadow overflow-hidden bg-[var(--card)]">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className={`w-14 h-14 ${stat.bgColor} rounded-xl flex items-center justify-center`}>
                        <stat.icon className={`w-7 h-7 ${stat.textColor}`} />
                      </div>
                      <Badge variant="outline" className="text-xs border-[var(--border)] text-[var(--foreground)]">
                        {stat.change}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-[var(--foreground)] mb-1">
                      {stat.value}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)]">
                      {stat.label}
                    </div>
                  </CardContent>
                </Card>
              </Card3D>
            </motion.div>
          ))}
        </div>

        {/* Main Content */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="bg-[var(--card)] border-2 border-[var(--border)] p-1">
            <TabsTrigger value="overview" className="data-[state=active]:bg-[#000080] data-[state=active]:text-white">
              Overview
            </TabsTrigger>
            <TabsTrigger value="applications" className="data-[state=active]:bg-[#000080] data-[state=active]:text-white">
              Applications
            </TabsTrigger>
            <TabsTrigger value="documents" className="data-[state=active]:bg-[#000080] data-[state=active]:text-white">
              Documents
            </TabsTrigger>
            <TabsTrigger value="activity" className="data-[state=active]:bg-[#000080] data-[state=active]:text-white">
              Activity
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Active Applications */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="lg:col-span-2"
              >
                <Card className="border-2 border-[var(--border)] shadow-lg bg-[var(--card)]">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-[var(--foreground)]">Active Applications</CardTitle>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => setSelectedTab('applications')}
                        className="text-[var(--foreground)]"
                      >
                        View All
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {applications.map((app) => (
                      <motion.div
                        key={app.id}
                        className="p-4 bg-[var(--background)] rounded-xl border-2 border-[var(--border)] hover:border-[#000080] transition-all group cursor-pointer"
                        whileHover={{ scale: 1.01 }}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-semibold text-[var(--foreground)]">
                                {app.service}
                              </h4>
                              <Badge
                                className={`${app.statusColor} text-white border-0`}
                              >
                                {app.status}
                              </Badge>
                            </div>
                            <div className="text-xs text-[var(--muted-foreground)] space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">ID:</span>
                                <span>{app.id}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Clock className="w-3 h-3" />
                                <span>Last updated: {app.lastUpdate}</span>
                              </div>
                            </div>
                          </div>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon" className="h-8 w-8">
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="bg-[var(--card)] border-[var(--border)]">
                              <DropdownMenuItem className="text-[var(--foreground)]">
                                <Eye className="w-4 h-4 mr-2" />
                                View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-[var(--foreground)]">
                                <Download className="w-4 h-4 mr-2" />
                                Download Receipt
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>

                        {/* Progress */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-[var(--muted-foreground)]">
                              Next: {app.nextStep}
                            </span>
                            <span className="font-medium text-[var(--foreground)]">
                              {app.progress}%
                            </span>
                          </div>
                          <Progress value={app.progress} className="h-2" />
                        </div>
                      </motion.div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>

              {/* Recent Activity */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <Card className="border-2 border-[var(--border)] shadow-lg bg-[var(--card)]">
                  <CardHeader>
                    <CardTitle className="text-[var(--foreground)]">Recent Activity</CardTitle>
                    <CardDescription className="text-[var(--muted-foreground)]">Your latest updates</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {recentActivity.map((activity, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-start gap-3 pb-3 border-b border-[var(--border)] last:border-0 last:pb-0"
                      >
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${activity.color.includes('blue') ? 'bg-blue-50 dark:bg-blue-950/20' : activity.color.includes('green') ? 'bg-green-50 dark:bg-green-950/20' : activity.color.includes('purple') ? 'bg-purple-50 dark:bg-purple-950/20' : 'bg-orange-50 dark:bg-orange-950/20'}`}>
                          <activity.icon className={`w-5 h-5 ${activity.color}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-[var(--foreground)]">
                            {activity.action}
                          </p>
                          <p className="text-xs text-[var(--muted-foreground)] mt-1">
                            {activity.service}
                          </p>
                          <p className="text-xs text-[var(--muted-foreground)] mt-1 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {activity.time}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="border-2 border-[var(--border)] shadow-lg bg-gradient-to-br from-[#000080] to-[#000066] text-white overflow-hidden relative">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0di00aC0ydjRoLTR2Mmg0djRoMnYtNGg0di0yaC00em0wLTMwVjBoLTJ2NGgtNHYyaDR2NGgyVjZoNFY0aC00ek02IDM0di00SDR2NGgwdjJoNHY0aDJWMzZoNHYtMkg2ek02IDRWMEg0djRIMHYyaDR2NGgyVjZoNFY0SDZ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-20" />
                <CardHeader className="relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center">
                      <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-white">Quick Actions</CardTitle>
                      <CardDescription className="text-white/80">
                        Commonly used services
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="relative z-10">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: 'New Application', icon: FileText, action: () => onNavigate('services') },
                      { label: 'Track Status', icon: Clock, action: () => onNavigate('tracker') },
                      { label: 'Upload Document', icon: Upload, action: () => {} },
                      { label: 'Make Payment', icon: CreditCard, action: () => {} },
                    ].map((action) => (
                      <Button
                        key={action.label}
                        onClick={action.action}
                        variant="secondary"
                        className="h-auto py-4 flex-col gap-2 bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-sm"
                      >
                        <action.icon className="w-6 h-6" />
                        <span className="text-xs">{action.label}</span>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          {/* Applications Tab */}
          <TabsContent value="applications" className="space-y-6">
            <Card className="border-2 border-[var(--border)] shadow-lg bg-[var(--card)]">
              <CardHeader>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <CardTitle className="text-[var(--foreground)]">All Applications</CardTitle>
                    <CardDescription className="text-[var(--muted-foreground)]">Manage and track your applications</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <div className="relative flex-1 md:flex-none">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]" />
                      <Input 
                        placeholder="Search..." 
                        className="pl-9 w-full md:w-64 bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]" 
                      />
                    </div>
                    <Button variant="outline" size="icon" className="border-[var(--border)] text-[var(--foreground)]">
                      <Filter className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {applications.map((app) => (
                    <div
                      key={app.id}
                      className="p-4 bg-[var(--background)] rounded-xl border-2 border-[var(--border)] hover:border-[#000080] hover:shadow-md transition-all cursor-pointer"
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2 flex-wrap">
                            <h4 className="font-semibold text-[var(--foreground)]">
                              {app.service}
                            </h4>
                            <Badge className={`${app.statusColor} text-white border-0`}>
                              {app.status}
                            </Badge>
                            <Badge variant="outline" className="border-[var(--border)] text-[var(--foreground)]">
                              {app.id}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-[var(--muted-foreground)]">Submitted:</span>
                              <div className="font-medium text-[var(--foreground)]">{app.submittedDate}</div>
                            </div>
                            <div>
                              <span className="text-[var(--muted-foreground)]">Next Step:</span>
                              <div className="font-medium text-[var(--foreground)]">{app.nextStep}</div>
                            </div>
                            <div>
                              <span className="text-[var(--muted-foreground)]">Progress:</span>
                              <div className="font-medium text-[var(--foreground)]">{app.progress}%</div>
                            </div>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          className="border-[var(--border)] text-[var(--foreground)] whitespace-nowrap"
                        >
                          View Details
                          <ExternalLink className="w-4 h-4 ml-2" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <Card className="border-2 border-[var(--border)] shadow-lg bg-[var(--card)]">
              <CardHeader>
                <CardTitle className="text-[var(--foreground)]">My Documents</CardTitle>
                <CardDescription className="text-[var(--muted-foreground)]">Manage your uploaded documents</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Shield className="w-16 h-16 text-[var(--muted-foreground)] mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-[var(--foreground)] mb-2">
                    Secure Document Storage
                  </h3>
                  <p className="text-[var(--muted-foreground)] mb-6">
                    Your documents are encrypted and securely stored
                  </p>
                  <Button className="bg-[#000080] hover:bg-[#000066] text-white">
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Document
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity" className="space-y-6">
            <Card className="border-2 border-[var(--border)] shadow-lg bg-[var(--card)]">
              <CardHeader>
                <CardTitle className="text-[var(--foreground)]">Activity Timeline</CardTitle>
                <CardDescription className="text-[var(--muted-foreground)]">Complete history of your actions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-4 p-4 bg-[var(--background)] rounded-xl border border-[var(--border)]"
                    >
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${activity.color.includes('blue') ? 'bg-blue-50 dark:bg-blue-950/20' : activity.color.includes('green') ? 'bg-green-50 dark:bg-green-950/20' : activity.color.includes('purple') ? 'bg-purple-50 dark:bg-purple-950/20' : 'bg-orange-50 dark:bg-orange-950/20'}`}>
                        <activity.icon className={`w-6 h-6 ${activity.color}`} />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-[var(--foreground)]">
                          {activity.action}
                        </p>
                        <p className="text-sm text-[var(--muted-foreground)] mt-1">
                          {activity.service}
                        </p>
                        <p className="text-xs text-[var(--muted-foreground)] mt-2 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {activity.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
