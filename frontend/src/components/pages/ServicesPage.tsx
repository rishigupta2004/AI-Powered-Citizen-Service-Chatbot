import React, { useState } from 'react';
import { motion } from 'motion/react';
import {
  Search,
  Filter,
  ArrowRight,
  Grid3x3,
  List,
  Clock,
  IndianRupee,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { ServiceCard3D } from '../3d/ServiceCard3D';
import { FloatingElements } from '../animations/FloatingElements';
import { getAllServices } from '../../data/servicesData';

interface ServicesPageProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function ServicesPage({ onNavigate }: ServicesPageProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const allServices = getAllServices();

  // Extract unique categories
  const categories = ['all', ...new Set(allServices.map(s => s.category))];

  // Filter services
  const filteredServices = allServices.filter(service => {
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         service.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || service.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Group services by category
  const servicesByCategory = filteredServices.reduce((acc, service) => {
    if (!acc[service.category]) {
      acc[service.category] = [];
    }
    acc[service.category].push(service);
    return acc;
  }, {} as Record<string, typeof allServices>);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-[#000080] via-[#000066] to-[#000050] text-white py-20 mb-20 overflow-hidden">
        <FloatingElements count={8} className="opacity-20" />
        
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-white/10 text-white border-white/20 backdrop-blur-sm px-6 py-2 text-base">
              Government Services
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              All Services
            </h1>
            <p className="text-xl text-white/90 max-w-3xl mx-auto leading-relaxed">
              Browse our complete catalog of 50+ government services. Fast, secure, and accessible 24/7.
            </p>
          </motion.div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
        {/* Search and Filter Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Search */}
                <div className="md:col-span-2 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--muted-foreground)]" />
                  <Input
                    type="text"
                    placeholder="Search services..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-12 bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]"
                  />
                </div>

                {/* Category Filter */}
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                      <SelectTrigger className="h-12 bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]">
                        <Filter className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map(cat => (
                          <SelectItem key={cat} value={cat}>
                            {cat === 'all' ? 'All Categories' : cat}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* View Mode Toggle */}
                  <div className="flex border border-[var(--border)] rounded-[var(--radius-lg)] bg-[var(--input-background)]">
                    <Button
                      variant={viewMode === 'grid' ? 'default' : 'ghost'}
                      size="sm"
                      className="rounded-r-none h-12"
                      onClick={() => setViewMode('grid')}
                    >
                      <Grid3x3 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant={viewMode === 'list' ? 'default' : 'ghost'}
                      size="sm"
                      className="rounded-l-none h-12"
                      onClick={() => setViewMode('list')}
                    >
                      <List className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Results Count */}
              <div className="mt-4 text-sm text-[var(--muted-foreground)]">
                Showing {filteredServices.length} of {allServices.length} services
                {searchQuery && ` for "${searchQuery}"`}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Services Grid */}
        {viewMode === 'grid' ? (
          // Grid View
          <>
            {Object.entries(servicesByCategory).map(([category, services], categoryIndex) => (
              <motion.div
                key={category}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + categoryIndex * 0.1 }}
                className="mb-16"
              >
                <div className="flex items-center gap-3 mb-8">
                  <h2 className="text-3xl font-bold text-[var(--foreground)]">{category}</h2>
                  <Badge variant="secondary" className="text-sm">
                    {services.length} {services.length === 1 ? 'Service' : 'Services'}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {services.map((service, index) => (
                    <motion.div
                      key={service.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + index * 0.05 }}
                    >
                      <ServiceCard3D
                        icon={service.icon}
                        name={service.name}
                        description={service.description}
                        badge={service.badge}
                        gradient={service.gradient}
                        processingTime={service.processingTime}
                        fee={service.fee}
                        onClick={() => onNavigate('service-detail', service.id)}
                      />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            ))}
          </>
        ) : (
          // List View
          <div className="space-y-4">
            {filteredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="border-2 border-[var(--card-border)] hover:border-[#000080] hover:shadow-[var(--shadow-8)] transition-all bg-[var(--card)] cursor-pointer group"
                  onClick={() => onNavigate('service-detail', service.id)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center gap-6">
                      {/* Icon */}
                      <div className={`w-16 h-16 bg-gradient-to-br ${service.gradient} rounded-[var(--radius-xl)] flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform shadow-[var(--shadow-4)]`}>
                        <service.icon className="w-8 h-8 text-white" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-xl font-bold text-[var(--foreground)] group-hover:text-[#000080] transition-colors">
                            {service.name}
                          </h3>
                          {service.badge && (
                            <Badge variant="secondary" className="text-xs">
                              {service.badge}
                            </Badge>
                          )}
                        </div>
                        <p className="text-[var(--muted-foreground)] mb-3">
                          {service.description}
                        </p>
                        <div className="flex flex-wrap items-center gap-4 text-sm">
                          <div className="flex items-center gap-1 text-[var(--muted-foreground)]">
                            <Clock className="w-4 h-4" />
                            <span>{service.processingTime}</span>
                          </div>
                          <div className="flex items-center gap-1 text-[var(--muted-foreground)]">
                            <IndianRupee className="w-4 h-4" />
                            <span>{service.fee}</span>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {service.category}
                          </Badge>
                        </div>
                      </div>

                      {/* Arrow */}
                      <ArrowRight className="w-6 h-6 text-[var(--muted-foreground)] group-hover:text-[#000080] group-hover:translate-x-1 transition-all flex-shrink-0" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        {/* No Results */}
        {filteredServices.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
          >
            <div className="w-24 h-24 bg-[var(--muted)]/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="w-12 h-12 text-[var(--muted-foreground)]" />
            </div>
            <h3 className="text-2xl font-bold text-[var(--foreground)] mb-2">
              No services found
            </h3>
            <p className="text-[var(--muted-foreground)] mb-6">
              Try adjusting your search or filter criteria
            </p>
            <Button
              variant="outline"
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('all');
              }}
            >
              Clear Filters
            </Button>
          </motion.div>
        )}

        {/* CTA Section */}
        {filteredServices.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-20"
          >
            <Card className="border-2 border-[#000080] shadow-[var(--shadow-12)] bg-gradient-to-br from-[#000080] to-[#000066] text-white overflow-hidden relative">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute inset-0" style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                }} />
              </div>
              <CardContent className="relative z-10 py-12 text-center">
                <h2 className="text-3xl font-bold mb-4">Need Help Choosing?</h2>
                <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
                  Our support team is available 24/7 to guide you through the process
                </p>
                <div className="flex flex-wrap gap-4 justify-center">
                  <Button
                    size="lg"
                    className="bg-white text-[#000080] hover:bg-white/90 px-8 shadow-[var(--shadow-8)]"
                    onClick={() => onNavigate('faq')}
                  >
                    View FAQ
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-2 border-white text-white hover:bg-white hover:text-[#000080] px-8"
                  >
                    Contact Support
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}
