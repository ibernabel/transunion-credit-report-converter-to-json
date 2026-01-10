import { useState } from 'react';
import { useMutation, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import axios from 'axios';
import { Toaster, toast } from 'sonner';
import { UploadZone } from './components/UploadZone';
import { Dashboard } from './components/Dashboard';
import type { CreditReport } from './types/api';
import { Landmark, ShieldAlert } from 'lucide-react';

const queryClient = new QueryClient();

function AppContent() {
  const [report, setReport] = useState<CreditReport | null>(null);

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post<CreditReport>('/v1/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      setReport(data);
      toast.success('Report processed successfully!');
    },
    onError: (error: any) => {
      console.error('Upload error:', error);
      const message = error.response?.data?.detail || 'Failed to process the credit report. Please ensure it is a valid TransUnion PDF.';
      toast.error('Error Processing File', {
        description: message,
      });
    },
  });

  const handleUpload = (file: File) => {
    mutation.mutate(file);
  };

  return (
    <div className="min-h-screen bg-slate-50/50 dark:bg-slate-950">
      <header className="border-b bg-white/50 backdrop-blur-xl sticky top-0 z-10 dark:bg-slate-900/50">
        <div className="container max-w-6xl mx-auto h-16 flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="bg-primary p-1.5 rounded-lg">
              <Landmark className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">Credit<span className="text-primary">Parser</span></h1>
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground uppercase tracking-widest bg-muted px-3 py-1.5 rounded-full">
            <ShieldAlert className="h-3.5 w-3.5" />
            Stateless Session
          </div>
        </div>
      </header>

      <main className="container max-w-6xl mx-auto py-10 px-4">
        {!report ? (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight md:text-4xl">
                Insights for your Financial Health
              </h2>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Upload your credit report PDF to visualize accounts, scores, and debt distribution in a secure, stateless environment.
              </p>
            </div>
            <UploadZone
              onUpload={handleUpload}
              isProcessing={mutation.isPending}
            />
          </div>
        ) : (
          <Dashboard report={report} />
        )}
      </main>

      <footer className="border-t py-6 mt-20">
        <div className="container max-w-6xl mx-auto px-4 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} CreditReport Parser. Private & Secure.
        </div>
      </footer>

      <Toaster position="top-center" richColors />
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
