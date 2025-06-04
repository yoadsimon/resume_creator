import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface ResumeContent {
  content: string;
  file_path: string;
  file_size: number;
  last_modified: number;
}

interface ResumeViewerProps {
  onClose: () => void;
}

const ResumeViewer: React.FC<ResumeViewerProps> = ({ onClose }) => {
  const [resumeContent, setResumeContent] = useState<ResumeContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchResumeContent();
  }, []);

  const fetchResumeContent = async () => {
    try {
      setLoading(true);
      const response = await axios.get<ResumeContent>('http://localhost:8000/resume/content');
      setResumeContent(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load resume content');
    } finally {
      setLoading(false);
    }
  };

  const downloadResume = async () => {
    try {
      const response = await axios.get('http://localhost:8000/resume/download', {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'tailored_resume.docx';
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError('Failed to download resume');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <div className="flex items-center justify-center">
            <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="ml-2 text-lg">Loading resume content...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Resume Viewer</h2>
            {resumeContent && (
              <div className="text-sm text-gray-500 mt-1">
                <span>Size: {formatFileSize(resumeContent.file_size)}</span>
                <span className="mx-2">•</span>
                <span>Modified: {formatDate(resumeContent.last_modified)}</span>
              </div>
            )}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={downloadResume}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Download
            </button>
            <button
              onClick={onClose}
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
            >
              Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {error ? (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-600">{error}</p>
              <button
                onClick={fetchResumeContent}
                className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
              >
                Retry
              </button>
            </div>
          ) : resumeContent ? (
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="bg-white rounded border shadow-sm p-8 font-mono text-sm leading-relaxed">
                <pre className="whitespace-pre-wrap break-words">
                  {resumeContent.content}
                </pre>
              </div>
              
              {/* Future editing section placeholder */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="text-lg font-medium text-blue-900 mb-2">Coming Soon: Resume Editor</h3>
                <p className="text-blue-700">
                  In future versions, you'll be able to edit your resume content directly in this interface.
                  Features will include:
                </p>
                <ul className="list-disc list-inside text-blue-700 mt-2 space-y-1">
                  <li>Section-by-section editing</li>
                  <li>Real-time preview</li>
                  <li>Formatting options</li>
                  <li>Export to different formats</li>
                </ul>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default ResumeViewer; 