import React from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Shield,
  Globe,
  Users,
  FileCheck,
  CreditCard,
  Briefcase,
  GraduationCap,
  Car,
  CheckCircle2,
  TrendingUp,
  Award,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { ImageWithFallback } from '../figma/ImageWithFallback';

interface HomeProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function Home({ onNavigate }: HomeProps) {
  const features = [
    {
      icon: Shield,
      title: 'Compliant by Design',
      description: 'Built with strict adherence to government standards and security protocols',
      note: 'Meets all regulatory requirements',
      gradient: 'from-navy to-navy/80',
    },
    {
      icon: Users,
      title: 'Accessible & Inclusive',
      description: 'WCAG 2.1 AA compliant ensuring access for all citizens',
      note: 'Full keyboard navigation & screen reader support',
      gradient: 'from-accent to-accent/80',
    },
    {
      icon: Globe,
      title: 'Ready for Multilingual',
      description: 'Support for multiple Indian languages for wider reach',
      note: 'Available in 10+ regional languages',
      gradient: 'from-saffron to-saffron/80',
    },
  ];

  const services = [
    {
      id: 'passport',
      icon: FileCheck,
      name: 'Passport Services',
      description: 'Apply, renew, or track your passport application online',
      status: 'Available',
      badge: 'Popular',
      gradient: 'from-blue-500 to-blue-600',
    },
    {
      id: 'aadhaar',
      icon: CreditCard,
      name: 'Aadhaar Services',
      description: 'Update, download, or link your Aadhaar card',
      status: 'Available',
      badge: 'Essential',
      gradient: 'from-purple-500 to-purple-600',
    },
    {
      id: 'epfo',
      icon: Briefcase,
      name: 'EPFO Services',
      description: 'Check PF balance, transfer, and claim settlements',
      status: 'Available',
      badge: 'Trending',
      gradient: 'from-green-500 to-green-600',
    },
    {
      id: 'scholarship',
      icon: GraduationCap,
      name: 'Scholarship Programs',
      description: 'Apply for government scholarships and grants',
      status: 'New',
      badge: 'New',
      gradient: 'from-orange-500 to-orange-600',
    },
    {
      id: 'driving-license',
      icon: Car,
      name: 'Driving License',
      description: 'Apply for new or renew existing driving license',
      status: 'Available',
      badge: 'Quick',
      gradient: 'from-red-500 to-red-600',
    },
  ];

  const stats = [
    { value: '10M+', label: 'Active Users' },
    { value: '50+', label: 'Services' },
    { value: '99.9%', label: 'Uptime' },
    { value: '24/7', label: 'Support' },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-gradient-to-br from-navy via-navy/95 to-navy/90">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="text-white"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Badge className="mb-6 bg-saffron text-white border-0 text-sm px-4 py-1">
                  Government of India Initiative
                </Badge>
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-5xl md:text-6xl font-bold mb-6 leading-tight"
              >
                Citizen Services
                <span className="block text-saffron mt-2">Made Simple</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-xl text-white/80 mb-8 leading-relaxed"
              >
                Access all government services in one place. Fast, secure, and accessible to everyone.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="flex flex-wrap gap-4"
              >
                <Button
                  size="lg"
                  className="bg-saffron hover:bg-saffron/90 text-white px-8 group"
                  onClick={() => onNavigate('services')}
                >
                  Get Started
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="border-2 border-white text-white hover:bg-white hover:text-navy px-8"
                  onClick={() => onNavigate('about')}
                >
                  Learn More
                </Button>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="grid grid-cols-4 gap-6 mt-12"
              >
                {stats.map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="text-2xl md:text-3xl font-bold text-saffron">{stat.value}</div>
                    <div className="text-xs md:text-sm text-white/70 mt-1">{stat.label}</div>
                  </div>
                ))}
              </motion.div>
            </motion.div>

            {/* Right Image */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1709967884183-7ffa9d168508?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxpbmRpYSUyMGdvdmVybm1lbnQlMjBidWlsZGluZyUyMGFyY2hpdGVjdHVyZXxlbnwxfHx8fDE3NjAxMDU3Njl8MA&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Government Services Illustration"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-navy/50 to-transparent" />
              </div>
              {/* Floating Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 }}
                className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-2xl p-4 max-w-xs"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-accent to-accent/80 rounded-lg flex items-center justify-center">
                    <CheckCircle2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="font-semibold text-navy">100% Secure</div>
                    <div className="text-sm text-gray-600">End-to-end encryption</div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
              fill="white"
            />
          </svg>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="py-20 bg-white relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-navy mb-4">Why Choose Our Platform</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Built with cutting-edge technology and designed for every citizen
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 shadow-lg group cursor-pointer">
                  <CardHeader>
                    <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                      <feature.icon className="w-8 h-8 text-white" />
                    </div>
                    <CardTitle className="text-2xl text-navy">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base mb-4">
                      {feature.description}
                    </CardDescription>
                    <div className="bg-gray-50 border-l-4 border-saffron p-3 rounded">
                      <div className="flex items-start gap-2">
                        <Award className="w-4 h-4 text-saffron flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700 italic">{feature.note}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-navy mb-4">Quick Access Services</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Popular government services at your fingertips
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {services.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.05 }}
              >
                <Card
                  className="h-full hover:shadow-2xl transition-all duration-300 cursor-pointer group border-0 shadow-lg overflow-hidden"
                  onClick={() => onNavigate('service-detail', service.id)}
                >
                  <CardHeader className="relative">
                    <div className={`w-full h-24 bg-gradient-to-br ${service.gradient} rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform relative overflow-hidden`}>
                      <service.icon className="w-12 h-12 text-white z-10" />
                      <div className="absolute inset-0 bg-white/20 group-hover:bg-white/30 transition-colors" />
                    </div>
                    <div className="absolute top-4 right-4">
                      <Badge className="bg-white text-navy shadow-md">
                        {service.badge}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg text-navy">{service.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm mb-4 min-h-[3rem]">
                      {service.description}
                    </CardDescription>
                    <div className="flex items-center justify-between">
                      <Badge
                        variant="outline"
                        className="border-accent text-accent text-xs"
                      >
                        {service.status}
                      </Badge>
                      <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-navy group-hover:translate-x-1 transition-all" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mt-12"
          >
            <Button
              size="lg"
              variant="outline"
              className="border-2 border-navy text-navy hover:bg-navy hover:text-white"
              onClick={() => onNavigate('services')}
            >
              View All Services
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-navy via-navy/95 to-navy/90 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-white/80 mb-8">
              Join millions of citizens already using our platform for seamless government services
            </p>
            <Button
              size="lg"
              className="bg-saffron hover:bg-saffron/90 text-white px-8"
              onClick={() => onNavigate('services')}
            >
              Explore Services
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
