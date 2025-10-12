import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, FileText, Calendar, HardDrive, Eye, Search } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { downloadDocument, searchDocuments, sampleDocuments, type DocumentInfo } from '../lib/documents';
import { useToast } from './ui/use-toast';

interface DocumentDownloaderProps {
  category?: string;
  title?: string;
  description?: string;
}

export function DocumentDownloader({ 
  category, 
  title = "Download Documents", 
  description = "Download forms and documents for government services" 
}: DocumentDownloaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [downloading, setDownloading] = useState<string | null>(null);
  const { toast } = useToast();

  const documents = searchQuery 
    ? searchDocuments(searchQuery)
    : category 
      ? sampleDocuments.filter(doc => doc.category === category)
      : sampleDocuments;

  const handleDownload = async (doc: DocumentInfo) => {
    setDownloading(doc.id);
    try {
      await downloadDocument(doc.id);
      toast({
        title: "Download Started",
        description: `${doc.name} is being downloaded`,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Please try again later",
        variant: "destructive",
      });
    } finally {
      setDownloading(null);
    }
  };

  const handlePreview = (doc: DocumentInfo) => {
    toast({
      title: "Preview",
      description: `Opening preview for ${doc.name}`,
    });
    // In a real app, this would open a preview modal or new tab
    window.open(`/preview/${doc.id}`, '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-[var(--foreground)] mb-2">{title}</h3>
        <p className="text-[var(--muted-foreground)]">{description}</p>
      </div>

      {/* Search */}
      <div className="relative max-w-md mx-auto">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]" />
        <Input
          placeholder="Search documents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {documents.map((doc, index) => (
          <motion.div
            key={doc.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="h-full hover:shadow-lg transition-shadow border-2 hover:border-[var(--primary)]/20">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <FileText className="w-8 h-8 text-[var(--primary)] mb-2" />
                  <Badge variant="secondary" className="text-xs">
                    {doc.format}
                  </Badge>
                </div>
                <CardTitle className="text-lg leading-tight">{doc.name}</CardTitle>
                <CardDescription className="text-sm">
                  {doc.description}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {/* Document Info */}
                  <div className="flex items-center justify-between text-xs text-[var(--muted-foreground)]">
                    <div className="flex items-center gap-1">
                      <HardDrive className="w-3 h-3" />
                      {doc.fileSize}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(doc.lastUpdated).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleDownload(doc)}
                      disabled={downloading === doc.id}
                      className="flex-1 h-9"
                      size="sm"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      {downloading === doc.id ? 'Downloading...' : 'Download'}
                    </Button>
                    
                    <Button
                      onClick={() => handlePreview(doc)}
                      variant="outline"
                      size="sm"
                      className="px-3"
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {documents.length === 0 && (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-[var(--muted-foreground)] mx-auto mb-3" />
          <h4 className="text-lg font-medium text-[var(--foreground)] mb-2">No documents found</h4>
          <p className="text-[var(--muted-foreground)]">
            {searchQuery ? 'Try adjusting your search terms' : 'No documents available for this category'}
          </p>
        </div>
      )}
    </div>
  );
}
