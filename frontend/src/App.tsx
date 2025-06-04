import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import ResumeViewer from './components/ResumeViewer';
import './App.css';

interface FormData {
  resumeFile: File | null;
  accomplishments: File | null;
  jobDescriptionLink: string;
  companyBaseLink: string;
  companyName: string;
  useO1Model: boolean;
}

function App() {
  const [formData, setFormData] = useState<FormData>({
    resumeFile: null,
    accomplishments: null,
    jobDescriptionLink: '',
    companyBaseLink: '',
    companyName: '',
    useO1Model: false,
  });
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResumeUrl, setGeneratedResumeUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showResumeViewer, setShowResumeViewer] = useState(false);
  const [hasExistingResume, setHasExistingResume] = useState(false);
  const [checkingExistingResume, setCheckingExistingResume] = useState(true);

  // Check for existing resume on app startup
  useEffect(() => {
    const checkExistingResume = async () => {
      try {
        const response = await axios.get<{structured_content?: any; raw_content?: string}>('http://localhost:8000/resume/content');
        if (response.data.structured_content || response.data.raw_content) {
          setHasExistingResume(true);
        }
      } catch (err) {
        // No existing resume or error - that's fine
        setHasExistingResume(false);
      } finally {
        setCheckingExistingResume(false);
      }
    };

    checkExistingResume();
  }, []);

  const resumeDropzone = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFormData(prev => ({ ...prev, resumeFile: acceptedFiles[0] }));
    }
  });

  const accomplishmentsDropzone = useDropzone({
    accept: {
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFormData(prev => ({ ...prev, accomplishments: acceptedFiles[0] }));
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.resumeFile) {
      setError('Please upload a resume file');
      return;
    }

    if (!formData.jobDescriptionLink || !formData.companyBaseLink) {
      setError('Please fill in all required fields');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedResumeUrl(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('resume_file', formData.resumeFile);
      if (formData.accomplishments) {
        formDataToSend.append('accomplishments_file', formData.accomplishments);
      }
      formDataToSend.append('job_description_link', formData.jobDescriptionLink);
      formDataToSend.append('company_base_link', formData.companyBaseLink);
      formDataToSend.append('company_name', formData.companyName);
      formDataToSend.append('use_o1_model', formData.useO1Model.toString());

      const response = await axios.post('http://localhost:8000/generate_resume', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      // Create a URL for the downloaded file
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]));
      setGeneratedResumeUrl(url);
      setHasExistingResume(true);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred while generating the resume');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadResume = () => {
    if (generatedResumeUrl) {
      const link = document.createElement('a');
      link.href = generatedResumeUrl;
      link.download = 'tailored_resume.docx';
      link.click();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Resume Creator</h1>
          <p className="text-lg text-gray-600">Generate tailored resumes using AI technology</p>
        </div>

        {/* Existing Resume Section */}
        {checkingExistingResume ? (
          <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
            <div className="flex items-center justify-center">
              <svg className="animate-spin h-5 w-5 text-blue-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-gray-600">Checking for existing resume...</span>
            </div>
          </div>
        ) : hasExistingResume ? (
          <div className="bg-gradient-to-r from-green-50 to-blue-50 shadow-lg rounded-lg p-6 mb-8 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">✅ Resume Available</h3>
                <p className="text-gray-600">You have a resume ready to view and edit. You can view it now or generate a new one below.</p>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowResumeViewer(true)}
                  className="bg-purple-600 text-white px-6 py-3 rounded-md hover:bg-purple-700 transition-colors font-medium"
                >
                  🔍 View & Edit Resume
                </button>
                <button
                  onClick={async () => {
                    try {
                      const response = await axios.get('http://localhost:8000/resume/download', {
                        responseType: 'blob',
                      });
                      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]));
                      const link = document.createElement('a');
                      link.href = url;
                      link.download = 'current_resume.docx';
                      link.click();
                      window.URL.revokeObjectURL(url);
                    } catch (err) {
                      setError('Failed to download resume');
                    }
                  }}
                  className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors font-medium"
                >
                  📥 Download
                </button>
              </div>
            </div>
          </div>
        ) : null}

        <div className="bg-white shadow-xl rounded-lg overflow-hidden">
          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            {/* Resume File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Resume File (Required) <span className="text-red-500">*</span>
              </label>
              <div 
                {...resumeDropzone.getRootProps()} 
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  resumeDropzone.isDragActive 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...resumeDropzone.getInputProps()} />
                {formData.resumeFile ? (
                  <div className="text-green-600">
                    <svg className="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="font-medium">{formData.resumeFile.name}</p>
                  </div>
                ) : (
                  <div className="text-gray-500">
                    <svg className="mx-auto h-12 w-12 mb-2" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <p>Drop your resume (.docx) here, or click to select</p>
                  </div>
                )}
              </div>
            </div>

            {/* Accomplishments File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Accomplishments File (Optional)
              </label>
              <div 
                {...accomplishmentsDropzone.getRootProps()} 
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  accomplishmentsDropzone.isDragActive 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...accomplishmentsDropzone.getInputProps()} />
                {formData.accomplishments ? (
                  <div className="text-green-600">
                    <svg className="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="font-medium">{formData.accomplishments.name}</p>
                  </div>
                ) : (
                  <div className="text-gray-500">
                    <svg className="mx-auto h-12 w-12 mb-2" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <p>Drop your accomplishments (.txt) here, or click to select</p>
                  </div>
                )}
              </div>
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="jobDescriptionLink" className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description Link <span className="text-red-500">*</span>
                </label>
                <input
                  type="url"
                  id="jobDescriptionLink"
                  value={formData.jobDescriptionLink}
                  onChange={(e) => setFormData(prev => ({ ...prev, jobDescriptionLink: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="https://..."
                  required
                />
              </div>

              <div>
                <label htmlFor="companyBaseLink" className="block text-sm font-medium text-gray-700 mb-2">
                  Company Base Link <span className="text-red-500">*</span>
                </label>
                <input
                  type="url"
                  id="companyBaseLink"
                  value={formData.companyBaseLink}
                  onChange={(e) => setFormData(prev => ({ ...prev, companyBaseLink: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="https://..."
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-2">
                Company Name (Optional)
              </label>
              <input
                type="text"
                id="companyName"
                value={formData.companyName}
                onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter company name"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="useO1Model"
                checked={formData.useO1Model}
                onChange={(e) => setFormData(prev => ({ ...prev, useO1Model: e.target.checked }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="useO1Model" className="ml-2 block text-sm text-gray-700">
                Use O1 Model (Advanced)
              </label>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-red-600">{error}</p>
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={isGenerating}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isGenerating ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Resume...
                  </div>
                ) : (
                  'Generate Resume'
                )}
              </button>

              {generatedResumeUrl && (
                <button
                  type="button"
                  onClick={downloadResume}
                  className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
                >
                  Download Resume
                </button>
              )}
            </div>
          </form>
        </div>

        {generatedResumeUrl && (
          <div className="mt-8 bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Resume Generated Successfully!</h3>
            <p className="text-gray-600 mb-4">Your tailored resume has been generated and is ready for download.</p>
            <div className="flex space-x-4">
              <button
                onClick={downloadResume}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Download Resume
              </button>
              <button
                onClick={() => setShowResumeViewer(true)}
                className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors"
              >
                View Resume
              </button>
            </div>
          </div>
        )}

        {/* Resume Viewer Modal */}
        {showResumeViewer && (
          <ResumeViewer onClose={() => setShowResumeViewer(false)} />
        )}
      </div>
    </div>
  );
}

export default App;
