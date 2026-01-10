import React, { useCallback, useState } from 'react';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface UploadZoneProps {
    onUpload: (file: File) => void;
    isProcessing: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onUpload, isProcessing }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files && files.length > 0 && files[0].type === 'application/pdf') {
            setSelectedFile(files[0]);
        }
    }, []);

    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
        }
    }, []);

    const handleUploadClick = () => {
        if (selectedFile) {
            onUpload(selectedFile);
        }
    };

    return (
        <div className="max-w-xl mx-auto mt-20">
            <Card
                className={cn(
                    "relative border-2 border-dashed transition-colors duration-200 p-12 flex flex-col items-center justify-center text-center",
                    isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25",
                    isProcessing && "opacity-50 pointer-events-none"
                )}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept=".pdf"
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={handleFileChange}
                    disabled={isProcessing}
                />

                {selectedFile ? (
                    <div className="space-y-4">
                        <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary mx-auto">
                            <FileText className="w-8 h-8" />
                        </div>
                        <div>
                            <p className="font-medium">{selectedFile.name}</p>
                            <p className="text-sm text-muted-foreground">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                        <div className="flex gap-2 justify-center">
                            <Button variant="outline" size="sm" onClick={() => setSelectedFile(null)} disabled={isProcessing}>
                                <X className="w-4 h-4 mr-2" />
                                Remove
                            </Button>
                            <Button size="sm" onClick={handleUploadClick} disabled={isProcessing}>
                                {isProcessing ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <Upload className="w-4 h-4 mr-2" />
                                        Process Report
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center justify-center w-16 h-16 rounded-full bg-muted text-muted-foreground mx-auto">
                            <Upload className="w-8 h-8" />
                        </div>
                        <div className="space-y-2">
                            <h3 className="text-xl font-semibold">Upload Credit Report</h3>
                            <p className="text-muted-foreground">
                                Drag and drop your TransUnion PDF here, or click to browse
                            </p>
                        </div>
                        <p className="text-xs text-muted-foreground uppercase tracking-widest">
                            Only PDF files are supported
                        </p>
                    </div>
                )}
            </Card>
        </div>
    );
};
