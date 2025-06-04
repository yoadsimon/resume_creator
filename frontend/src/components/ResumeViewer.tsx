import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface PersonalInfo {
  name: string;
  email: string;
  phone_number: string;
  address: string;
  linkedin: string;
  github: string;
}

interface ExperienceItem {
  title: string;
  place: string;
  date: string;
  description: string[];
}

interface ProjectItem {
  title: string;
  date: string;
  description: string[];
}

interface EducationItem {
  title: string;
  place: string;
  date: string;
  description: string[];
}

interface StructuredResumeContent {
  personal_info: PersonalInfo;
  professional_summary: string;
  work_experience: ExperienceItem[];
  personal_projects: ProjectItem[];
  education: EducationItem[];
  skills: string[];
  languages: string[];
}

interface ResumeContentResponse {
  structured_content?: StructuredResumeContent;
  raw_content?: string;
  file_path: string;
  file_size: number;
  last_modified: number;
  note?: string;
}

interface ResumeViewerProps {
  onClose: () => void;
}

const ResumeViewer: React.FC<ResumeViewerProps> = ({ onClose }) => {
  const [resumeContent, setResumeContent] = useState<ResumeContentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [editPrompt, setEditPrompt] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchResumeContent();
  }, []);

  const fetchResumeContent = async () => {
    try {
      setLoading(true);
      const response = await axios.get<ResumeContentResponse>('http://localhost:8000/resume/content');
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

  const handleEditSection = (sectionKey: string) => {
    setEditingSection(sectionKey);
    setEditPrompt('');
  };

  const closeEditModal = () => {
    setEditingSection(null);
    setEditPrompt('');
    setIsEditing(false);
  };

  const submitEdit = async () => {
    if (!editingSection || !editPrompt.trim()) return;

    try {
      setIsEditing(true);
      const formData = new FormData();
      formData.append('section_key', editingSection);
      formData.append('edit_prompt', editPrompt);
      formData.append('use_o1_model', 'false');

      const response = await axios.post<{success: boolean; message: string; updated_section: any}>('http://localhost:8000/resume/edit-section', formData);
      
      if (response.data.success) {
        // Refresh the resume content to show changes
        await fetchResumeContent();
        closeEditModal();
        setError(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to edit section');
    } finally {
      setIsEditing(false);
    }
  };

  const getSectionTitle = (sectionKey: string) => {
    const titles: { [key: string]: string } = {
      'professional_summary': 'Professional Summary',
      'work_experience': 'Work Experience',
      'personal_projects': 'Personal Projects',
      'education': 'Education',
      'skills_languages': 'Skills & Languages'
    };
    return titles[sectionKey] || sectionKey;
  };

  const renderPersonalInfo = (personalInfo: PersonalInfo) => (
    <div className="text-center mb-8 border-b border-gray-200 pb-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-3">{personalInfo.name}</h1>
      <div className="text-gray-600 space-y-1">
        {personalInfo.email && (
          <div className="flex items-center justify-center space-x-1">
            <span>📧</span>
            <span>{personalInfo.email}</span>
          </div>
        )}
        {personalInfo.phone_number && (
          <div className="flex items-center justify-center space-x-1">
            <span>📱</span>
            <span>{personalInfo.phone_number}</span>
          </div>
        )}
        {personalInfo.address && (
          <div className="flex items-center justify-center space-x-1">
            <span>📍</span>
            <span>{personalInfo.address}</span>
          </div>
        )}
        <div className="flex items-center justify-center space-x-4 mt-2">
          {personalInfo.linkedin && (
            <a href={personalInfo.linkedin} className="text-blue-600 hover:text-blue-800">
              LinkedIn
            </a>
          )}
          {personalInfo.github && (
            <a href={personalInfo.github} className="text-gray-600 hover:text-gray-800">
              GitHub
            </a>
          )}
        </div>
      </div>
    </div>
  );

  const renderEditableSection = (title: string, sectionKey: string, children: React.ReactNode) => (
    <div className="mb-8 group">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 border-b-2 border-blue-600 pb-1">
          {title}
        </h2>
        <button
          onClick={() => handleEditSection(sectionKey)}
          className="opacity-0 group-hover:opacity-100 transition-opacity bg-blue-100 text-blue-700 px-3 py-1 rounded-md text-sm hover:bg-blue-200"
        >
          ✏️ Edit with AI
        </button>
      </div>
      {children}
    </div>
  );

  const renderWorkExperience = (workExp: ExperienceItem[]) => (
    <div className="space-y-6">
      {workExp.map((exp, index) => (
        <div key={index} className="border-l-4 border-blue-600 pl-4">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{exp.title}</h3>
              <p className="text-gray-700 font-medium">{exp.place}</p>
            </div>
            <span className="text-gray-500 text-sm">{exp.date}</span>
          </div>
          <ul className="space-y-1">
            {exp.description.map((desc, descIndex) => (
              <li key={descIndex} className="text-gray-600 flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>{desc}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );

  const renderProjects = (projects: ProjectItem[]) => (
    <div className="space-y-6">
      {projects.map((project, index) => (
        <div key={index} className="border-l-4 border-green-600 pl-4">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
            <span className="text-gray-500 text-sm">{project.date}</span>
          </div>
          <ul className="space-y-1">
            {project.description.map((desc, descIndex) => (
              <li key={descIndex} className="text-gray-600 flex items-start">
                <span className="text-green-600 mr-2">•</span>
                <span>{desc}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );

  const renderEducation = (education: EducationItem[]) => (
    <div className="space-y-6">
      {education.map((edu, index) => (
        <div key={index} className="border-l-4 border-purple-600 pl-4">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{edu.title}</h3>
              <p className="text-gray-700 font-medium">{edu.place}</p>
            </div>
            <span className="text-gray-500 text-sm">{edu.date}</span>
          </div>
          {edu.description && edu.description.length > 0 && (
            <ul className="space-y-1">
              {edu.description.map((desc, descIndex) => (
                <li key={descIndex} className="text-gray-600 flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span>{desc}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );

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

  const structuredContent = resumeContent?.structured_content;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] flex flex-col">
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
        <div className="flex-1 overflow-auto p-8">
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
          ) : structuredContent ? (
            // Structured Resume Display
            <div className="bg-white rounded-lg border border-gray-200 p-8 max-w-4xl mx-auto">
              {/* Personal Information */}
              {renderPersonalInfo(structuredContent.personal_info)}

              {/* Professional Summary */}
              {structuredContent.professional_summary && (
                renderEditableSection(
                  "Professional Summary",
                  "professional_summary",
                  <p className="text-gray-700 leading-relaxed">
                    {structuredContent.professional_summary}
                  </p>
                )
              )}

              {/* Work Experience */}
              {structuredContent.work_experience && structuredContent.work_experience.length > 0 && (
                renderEditableSection(
                  "Work Experience",
                  "work_experience",
                  renderWorkExperience(structuredContent.work_experience)
                )
              )}

              {/* Personal Projects */}
              {structuredContent.personal_projects && structuredContent.personal_projects.length > 0 && (
                renderEditableSection(
                  "Personal Projects",
                  "personal_projects",
                  renderProjects(structuredContent.personal_projects)
                )
              )}

              {/* Education */}
              {structuredContent.education && structuredContent.education.length > 0 && (
                renderEditableSection(
                  "Education",
                  "education",
                  renderEducation(structuredContent.education)
                )
              )}

              {/* Skills & Languages */}
              {(structuredContent.skills.length > 0 || structuredContent.languages.length > 0) && (
                renderEditableSection(
                  "Skills & Languages",
                  "skills_languages",
                  <div className="space-y-3">
                    {structuredContent.skills.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Skills:</h4>
                        <div className="flex flex-wrap gap-2">
                          {structuredContent.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {structuredContent.languages.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Languages:</h4>
                        <div className="flex flex-wrap gap-2">
                          {structuredContent.languages.map((language, index) => (
                            <span
                              key={index}
                              className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                            >
                              {language}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              )}

              {/* Future AI Editing Notice */}
              <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
                <h3 className="text-lg font-medium text-blue-900 mb-2">🤖 AI-Powered Editing</h3>
                <p className="text-blue-700 mb-2">
                  Hover over any section and click "Edit with AI" to improve specific parts of your resume using AI prompts.
                </p>
                <p className="text-sm text-blue-600">
                  Coming soon: Line-by-line editing, section rewriting, and content enhancement.
                </p>
              </div>
            </div>
          ) : resumeContent?.raw_content ? (
            // Fallback Raw Content Display
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="bg-white rounded border shadow-sm p-8 font-mono text-sm leading-relaxed">
                <pre className="whitespace-pre-wrap break-words">
                  {resumeContent.raw_content}
                </pre>
              </div>
            </div>
          ) : null}
        </div>
      </div>
      
      {/* Edit Section Modal */}
      {editingSection && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-xl font-bold text-gray-900">
                Edit {getSectionTitle(editingSection)}
              </h3>
              <button
                onClick={closeEditModal}
                className="text-gray-400 hover:text-gray-600 text-2xl"
                disabled={isEditing}
              >
                ×
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 p-6 overflow-auto">
              <div className="mb-4">
                <p className="text-gray-600 mb-3">
                  Describe how you'd like to improve this section. Be specific about what changes you want to make.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <h4 className="font-medium text-blue-900 mb-2">💡 Example prompts:</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• "Make this sound more technical and add cybersecurity keywords"</li>
                    <li>• "Emphasize leadership and team management skills"</li>
                    <li>• "Add more quantified achievements with specific numbers"</li>
                    <li>• "Make the language more action-oriented and impactful"</li>
                  </ul>
                </div>
              </div>
              
              <div className="mb-4">
                <label htmlFor="edit-prompt" className="block text-sm font-medium text-gray-700 mb-2">
                  Your editing instructions:
                </label>
                <textarea
                  id="edit-prompt"
                  value={editPrompt}
                  onChange={(e) => setEditPrompt(e.target.value)}
                  placeholder="Enter your editing instructions here..."
                  className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  disabled={isEditing}
                />
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={closeEditModal}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                disabled={isEditing}
              >
                Cancel
              </button>
              <button
                onClick={submitEdit}
                disabled={!editPrompt.trim() || isEditing}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {isEditing ? (
                  <>
                    <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Editing with AI...
                  </>
                ) : (
                  '🤖 Edit with AI'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeViewer; 