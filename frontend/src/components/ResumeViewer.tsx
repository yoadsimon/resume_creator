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
  const [inlineEditingField, setInlineEditingField] = useState<{
    section: string;
    itemIndex: number;
    field: string;
    value: string;
  } | null>(null);
  const [editingBullet, setEditingBullet] = useState<{
    section: string;
    itemIndex: number;
    bulletIndex: number;
    content: string;
  } | null>(null);
  const [editingWithAI, setEditingWithAI] = useState<{
    type: 'bullet' | 'field' | 'section';
    section: string;
    itemIndex?: number;
    bulletIndex?: number;
    fieldName?: string;
    content: string;
  } | null>(null);
  const [showAddItemModal, setShowAddItemModal] = useState<string | null>(null);
  const [newItemData, setNewItemData] = useState<any>({});
  const [scrollPosition, setScrollPosition] = useState(0);

  useEffect(() => {
    fetchResumeContent();
  }, []);

  const preserveScrollPosition = () => {
    setScrollPosition(window.pageYOffset || document.documentElement.scrollTop);
  };

  const restoreScrollPosition = () => {
    setTimeout(() => {
      window.scrollTo(0, scrollPosition);
    }, 50);
  };

  const fetchResumeContent = async () => {
    try {
      preserveScrollPosition();
      setLoading(true);
      const response = await axios.get<ResumeContentResponse>('http://localhost:8000/resume/content');
      setResumeContent(response.data);
      setError(null);
      restoreScrollPosition();
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
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center group">
          <h2 className="text-xl font-bold text-gray-900 border-b-2 border-blue-600 pb-1">
            {title}
          </h2>
          <ActionButtons
            onEdit={() => {
              const newName = prompt('Enter new section name:', title);
              if (newName && newName !== title) {
                console.log('Section name editing not yet implemented');
              }
            }}
            onEditWithAI={() => handleEditSection(sectionKey)}
            onDelete={() => deleteSection(sectionKey)}
            showEditWithAI={true}
            showDelete={canDeleteSection(sectionKey)}
          />
        </div>
      </div>
      {children}
    </div>
  );

  const renderWorkExperience = (workExp: ExperienceItem[]) => (
    <div className="space-y-6">
      {workExp.map((exp, index) => (
        <div key={index} className="border-l-4 border-blue-600 pl-4 relative">
          {/* Remove item button */}
          <button
            onClick={() => removeItem('work_experience', index)}
            className="absolute -right-8 top-0 opacity-0 hover:opacity-100 transition-opacity bg-red-100 text-red-600 hover:bg-red-200 rounded-full w-6 h-6 flex items-center justify-center text-xs"
            title="Remove this experience"
          >
            ✕
          </button>
          
          <div className="flex justify-between items-start mb-2">
            <div className="flex-1">
              <EditableField
                value={exp.title}
                sectionKey="work_experience"
                itemIndex={index}
                fieldName="title"
                className="text-lg font-semibold text-gray-900"
                showEditWithAI={true}
                showDelete={true}
                onEditWithAI={() => handleEditSection('work_experience')}
                onDelete={() => removeItem('work_experience', index)}
              >
                <h3 className="text-lg font-semibold text-gray-900">{exp.title}</h3>
              </EditableField>
              
              <EditableField
                value={exp.place}
                sectionKey="work_experience"
                itemIndex={index}
                fieldName="place"
                className="text-gray-700 font-medium"
                showEditWithAI={true}
                showDelete={true}
                onEditWithAI={() => handleEditSection('work_experience')}
                onDelete={() => removeItem('work_experience', index)}
              >
                <p className="text-gray-700 font-medium">{exp.place}</p>
              </EditableField>
            </div>
            
            <EditableField
              value={exp.date}
              sectionKey="work_experience"
              itemIndex={index}
              fieldName="date"
              className="text-gray-500 text-sm"
              showEditWithAI={true}
              showDelete={true}
              onEditWithAI={() => handleEditSection('work_experience')}
              onDelete={() => removeItem('work_experience', index)}
            >
              <span className="text-gray-500 text-sm">{exp.date}</span>
            </EditableField>
          </div>
          
          {/* Bullet points with individual hover behavior */}
          <div className="space-y-1">
            {exp.description.map((desc, descIndex) => (
              <div key={descIndex} className="text-gray-600">
                <div className="flex items-start">
                  <span className="text-blue-600 mr-2 mt-1 flex-shrink-0">•</span>
                  {editingBullet?.section === 'work_experience' &&
                    editingBullet?.itemIndex === index &&
                    editingBullet?.bulletIndex === descIndex ? (
                    <InlineEditField
                      value={editingBullet.content}
                      onSave={(newValue) => editBulletPoint('work_experience', index, descIndex, newValue)}
                      className="flex-1"
                      multiline
                    />
                  ) : (
                    <div className="flex-1">
                      <div className="group flex items-center">
                        <span className="flex-1">{desc}</span>
                        <ActionButtons
                          onEdit={() => setEditingBullet({ section: 'work_experience', itemIndex: index, bulletIndex: descIndex, content: desc })}
                          onEditWithAI={() => handleEditBulletWithAI('work_experience', index, descIndex, desc)}
                          onDelete={() => removeBulletPoint('work_experience', index, descIndex)}
                          showEditWithAI={true}
                          showDelete={true}
                        />
                      </div>
                      {/* Show inline AI editing under this bullet point */}
                      {editingWithAI?.type === 'bullet' &&
                       editingWithAI?.section === 'work_experience' &&
                       editingWithAI?.itemIndex === index &&
                       editingWithAI?.bulletIndex === descIndex && (
                        <InlineAIEditField
                          content={editingWithAI.content}
                          onSubmit={(prompt) => submitInlineAIEdit(prompt)}
                          onCancel={() => setEditingWithAI(null)}
                        />
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Add new bullet point */}
            <button
              onClick={() => {
                const content = prompt('Enter new bullet point:');
                if (content) addBulletPoint('work_experience', index, content);
              }}
              className="text-blue-600 hover:text-blue-800 text-sm flex items-center mt-2 opacity-60 hover:opacity-100 transition-opacity"
            >
              <span className="mr-1">+</span> Add bullet point
            </button>
          </div>
        </div>
      ))}
      
      {/* Add new experience button */}
      <button
        onClick={() => setShowAddItemModal('work_experience')}
        className="w-full border-2 border-dashed border-blue-300 rounded-lg p-4 text-blue-600 hover:border-blue-400 hover:text-blue-700 transition-colors flex items-center justify-center"
      >
        <span className="mr-2">+</span> Add Work Experience
      </button>
    </div>
  );

  const renderProjects = (projects: ProjectItem[]) => (
    <div className="space-y-6">
      {projects.map((project, index) => (
        <div key={index} className="border-l-4 border-green-600 pl-4 relative">
          {/* Remove item button */}
          <button
            onClick={() => removeItem('personal_projects', index)}
            className="absolute -right-8 top-0 opacity-0 hover:opacity-100 transition-opacity bg-red-100 text-red-600 hover:bg-red-200 rounded-full w-6 h-6 flex items-center justify-center text-xs"
            title="Remove this project"
          >
            ✕
          </button>
          
          <div className="flex justify-between items-start mb-2">
            <EditableField
              value={project.title}
              sectionKey="personal_projects"
              itemIndex={index}
              fieldName="title"
              className="text-lg font-semibold text-gray-900 flex-1"
              showEditWithAI={true}
              showDelete={true}
              onEditWithAI={() => handleEditSection('personal_projects')}
              onDelete={() => removeItem('personal_projects', index)}
            >
              <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
            </EditableField>
            
            <EditableField
              value={project.date}
              sectionKey="personal_projects"
              itemIndex={index}
              fieldName="date"
              className="text-gray-500 text-sm"
              showEditWithAI={true}
              showDelete={true}
              onEditWithAI={() => handleEditSection('personal_projects')}
              onDelete={() => removeItem('personal_projects', index)}
            >
              <span className="text-gray-500 text-sm">{project.date}</span>
            </EditableField>
          </div>
          
          {/* Bullet points with individual hover behavior */}
          <div className="space-y-1">
            {project.description.map((desc, descIndex) => (
              <div key={descIndex} className="text-gray-600">
                <div className="flex items-start">
                  <span className="text-green-600 mr-2 mt-1 flex-shrink-0">•</span>
                  {editingBullet?.section === 'personal_projects' &&
                    editingBullet?.itemIndex === index &&
                    editingBullet?.bulletIndex === descIndex ? (
                    <InlineEditField
                      value={editingBullet.content}
                      onSave={(newValue) => editBulletPoint('personal_projects', index, descIndex, newValue)}
                      className="flex-1"
                      multiline
                    />
                  ) : (
                    <div className="flex-1">
                      <div className="group flex items-center">
                        <span className="flex-1">{desc}</span>
                        <ActionButtons
                          onEdit={() => setEditingBullet({ section: 'personal_projects', itemIndex: index, bulletIndex: descIndex, content: desc })}
                          onEditWithAI={() => handleEditBulletWithAI('personal_projects', index, descIndex, desc)}
                          onDelete={() => removeBulletPoint('personal_projects', index, descIndex)}
                          showEditWithAI={true}
                          showDelete={true}
                        />
                      </div>
                      {/* Show inline AI editing under this bullet point */}
                      {editingWithAI?.type === 'bullet' &&
                       editingWithAI?.section === 'personal_projects' &&
                       editingWithAI?.itemIndex === index &&
                       editingWithAI?.bulletIndex === descIndex && (
                        <InlineAIEditField
                          content={editingWithAI.content}
                          onSubmit={(prompt) => submitInlineAIEdit(prompt)}
                          onCancel={() => setEditingWithAI(null)}
                        />
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Add new bullet point */}
            <button
              onClick={() => {
                const content = prompt('Enter new bullet point:');
                if (content) addBulletPoint('personal_projects', index, content);
              }}
              className="text-green-600 hover:text-green-800 text-sm flex items-center mt-2 opacity-60 hover:opacity-100 transition-opacity"
            >
              <span className="mr-1">+</span> Add bullet point
            </button>
          </div>
        </div>
      ))}
      
      {/* Add new project button */}
      <button
        onClick={() => setShowAddItemModal('personal_projects')}
        className="w-full border-2 border-dashed border-green-300 rounded-lg p-4 text-green-600 hover:border-green-400 hover:text-green-700 transition-colors flex items-center justify-center"
      >
        <span className="mr-2">+</span> Add Personal Project
      </button>
    </div>
  );

  const renderEducation = (education: EducationItem[]) => (
    <div className="space-y-6">
      {education.map((edu, index) => (
        <div key={index} className="border-l-4 border-purple-600 pl-4 relative">
          {/* Remove item button */}
          <button
            onClick={() => removeItem('education', index)}
            className="absolute -right-8 top-0 opacity-0 hover:opacity-100 transition-opacity bg-red-100 text-red-600 hover:bg-red-200 rounded-full w-6 h-6 flex items-center justify-center text-xs"
            title="Remove this education item"
          >
            ✕
          </button>
          
          <div className="flex justify-between items-start mb-2">
            <div className="flex-1">
              <EditableField
                value={edu.title}
                sectionKey="education"
                itemIndex={index}
                fieldName="title"
                className="text-lg font-semibold text-gray-900"
                showEditWithAI={true}
                showDelete={true}
                onEditWithAI={() => handleEditSection('education')}
                onDelete={() => removeItem('education', index)}
              >
                <h3 className="text-lg font-semibold text-gray-900">{edu.title}</h3>
              </EditableField>
              
              <EditableField
                value={edu.place}
                sectionKey="education"
                itemIndex={index}
                fieldName="place"
                className="text-gray-700 font-medium"
                showEditWithAI={true}
                showDelete={true}
                onEditWithAI={() => handleEditSection('education')}
                onDelete={() => removeItem('education', index)}
              >
                <p className="text-gray-700 font-medium">{edu.place}</p>
              </EditableField>
            </div>
            
            <EditableField
              value={edu.date}
              sectionKey="education"
              itemIndex={index}
              fieldName="date"
              className="text-gray-500 text-sm"
              showEditWithAI={true}
              showDelete={true}
              onEditWithAI={() => handleEditSection('education')}
              onDelete={() => removeItem('education', index)}
            >
              <span className="text-gray-500 text-sm">{edu.date}</span>
            </EditableField>
          </div>
          
          {/* Optional description points */}
          {edu.description && edu.description.length > 0 && (
            <div className="space-y-1">
              {edu.description.map((desc, descIndex) => (
                <div key={descIndex} className="text-gray-600">
                  <div className="flex items-start">
                    <span className="text-purple-600 mr-2 mt-1 flex-shrink-0">•</span>
                    {editingBullet?.section === 'education' &&
                      editingBullet?.itemIndex === index &&
                      editingBullet?.bulletIndex === descIndex ? (
                      <InlineEditField
                        value={editingBullet.content}
                        onSave={(newValue) => editBulletPoint('education', index, descIndex, newValue)}
                        className="flex-1"
                        multiline
                      />
                    ) : (
                      <div className="flex-1">
                        <div className="group flex items-center">
                          <span className="flex-1">{desc}</span>
                          <ActionButtons
                            onEdit={() => setEditingBullet({ section: 'education', itemIndex: index, bulletIndex: descIndex, content: desc })}
                            onEditWithAI={() => handleEditBulletWithAI('education', index, descIndex, desc)}
                            onDelete={() => removeBulletPoint('education', index, descIndex)}
                            showEditWithAI={true}
                            showDelete={true}
                          />
                        </div>
                        {/* Show inline AI editing under this bullet point */}
                        {editingWithAI?.type === 'bullet' &&
                         editingWithAI?.section === 'education' &&
                         editingWithAI?.itemIndex === index &&
                         editingWithAI?.bulletIndex === descIndex && (
                          <InlineAIEditField
                            content={editingWithAI.content}
                            onSubmit={(prompt) => submitInlineAIEdit(prompt)}
                            onCancel={() => setEditingWithAI(null)}
                          />
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Add new bullet point */}
          <button
            onClick={() => {
              const content = prompt('Enter new bullet point:');
              if (content) addBulletPoint('education', index, content);
            }}
            className="text-purple-600 hover:text-purple-800 text-sm flex items-center mt-2 opacity-60 hover:opacity-100 transition-opacity"
          >
            <span className="mr-1">+</span> Add description point
          </button>
        </div>
      ))}
      
      {/* Add new education button */}
      <button
        onClick={() => setShowAddItemModal('education')}
        className="w-full border-2 border-dashed border-purple-300 rounded-lg p-4 text-purple-600 hover:border-purple-400 hover:text-purple-700 transition-colors flex items-center justify-center"
      >
        <span className="mr-2">+</span> Add Education
      </button>
    </div>
  );

  const editItemField = async (sectionKey: string, itemIndex: number, fieldName: string, newValue: string) => {
    try {
      preserveScrollPosition();
      const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
        'http://localhost:8000/resume/edit-item-field', {
          section_key: sectionKey,
          item_index: itemIndex,
          field_name: fieldName,
          new_value: newValue
        }
      );
      
      if (response.data.success) {
        await fetchResumeContent();
        setInlineEditingField(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to edit field');
    }
  };

  const editBulletPoint = async (sectionKey: string, itemIndex: number, bulletIndex: number, newContent: string) => {
    try {
      preserveScrollPosition();
      const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
        'http://localhost:8000/resume/edit-bullet-point', {
          section_key: sectionKey,
          item_index: itemIndex,
          bullet_index: bulletIndex,
          new_content: newContent
        }
      );
      
      if (response.data.success) {
        await fetchResumeContent();
        setEditingBullet(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to edit bullet point');
    }
  };

  const addBulletPoint = async (sectionKey: string, itemIndex: number, content: string) => {
    try {
      preserveScrollPosition();
      const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
        'http://localhost:8000/resume/manage-bullet', {
          section_key: sectionKey,
          item_index: itemIndex,
          operation: 'add',
          bullet_content: content
        }
      );
      
      if (response.data.success) {
        await fetchResumeContent();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add bullet point');
    }
  };

  const removeBulletPoint = async (sectionKey: string, itemIndex: number, bulletIndex: number) => {
    try {
      preserveScrollPosition();
      const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
        'http://localhost:8000/resume/manage-bullet', {
          section_key: sectionKey,
          item_index: itemIndex,
          operation: 'remove',
          bullet_index: bulletIndex
        }
      );
      
      if (response.data.success) {
        await fetchResumeContent();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove bullet point');
    }
  };

  const addItem = async (sectionKey: string, itemData: any) => {
    try {
      preserveScrollPosition();
      const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
        'http://localhost:8000/resume/manage-item', {
          section_key: sectionKey,
          operation: 'add',
          item_data: itemData
        }
      );
      
      if (response.data.success) {
        await fetchResumeContent();
        setShowAddItemModal(null);
        setNewItemData({});
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add item');
    }
  };

  const removeItem = async (sectionKey: string, itemIndex: number) => {
    if (window.confirm('Are you sure you want to remove this item?')) {
      try {
        preserveScrollPosition();
        const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
          'http://localhost:8000/resume/manage-item', {
            section_key: sectionKey,
            operation: 'remove',
            item_index: itemIndex
          }
        );
        
        if (response.data.success) {
          await fetchResumeContent();
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to remove item');
      }
    }
  };

  const InlineEditField = ({ 
    value, 
    onSave, 
    className = "", 
    placeholder = "",
    multiline = false 
  }: {
    value: string;
    onSave: (newValue: string) => void;
    className?: string;
    placeholder?: string;
    multiline?: boolean;
  }) => {
    const [editValue, setEditValue] = useState(value);
    
    const handleSave = () => {
      if (editValue.trim() !== value) {
        onSave(editValue.trim());
      } else {
        // Cancel editing - clear both editing states
        setEditingBullet(null);
        setInlineEditingField(null);
      }
    };

    const handleCancel = () => {
      // Cancel editing - clear both editing states
      setEditingBullet(null);
      setInlineEditingField(null);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !multiline) {
        handleSave();
      } else if (e.key === 'Escape') {
        handleCancel();
      }
    };

    return (
      <div className="flex items-center space-x-2 w-full">
        {multiline ? (
          <textarea
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyPress}
            className={`${className} flex-1 bg-transparent border border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none min-h-[60px]`}
            placeholder={placeholder}
            rows={3}
            autoFocus
          />
        ) : (
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyPress={handleKeyPress}
            className={`${className} flex-1 bg-transparent border border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            placeholder={placeholder}
            autoFocus
          />
        )}
        <button
          onClick={handleSave}
          className="flex-shrink-0 text-green-600 hover:text-green-800 text-sm p-1"
        >
          ✓
        </button>
        <button
          onClick={handleCancel}
          className="flex-shrink-0 text-red-600 hover:text-red-800 text-sm p-1"
        >
          ✕
        </button>
      </div>
    );
  };

  // ActionButtons: show on hover only
  const ActionButtons: React.FC<{
    onEdit: () => void;
    onEditWithAI?: () => void;
    onDelete?: () => void;
    showEditWithAI?: boolean;
    showDelete?: boolean;
  }> = ({ onEdit, onEditWithAI, onDelete, showEditWithAI = false, showDelete = false }) => (
  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1 ml-2">
    <button
      onClick={onEdit}
      className="text-gray-400 hover:text-blue-600 text-sm p-1"
      title="Edit"
    >
      ✏️
    </button>
    {showEditWithAI && onEditWithAI && (
      <button
        onClick={onEditWithAI}
        className="text-gray-400 hover:text-green-600 text-sm p-1"
        title="Edit with AI"
      >
        🤖
      </button>
    )}
    {showDelete && onDelete && (
      <button
        onClick={onDelete}
        className="text-gray-400 hover:text-red-600 text-sm p-1"
        title="Delete"
      >
        🗑️
      </button>
    )}
  </div>
);

  // EditableField: for section titles and fields
  const EditableField = ({
    value,
    sectionKey,
    itemIndex,
    fieldName,
    className = "",
    children,
    multiline = false,
    showEditWithAI = false,
    showDelete = false,
    onEditWithAI,
    onDelete
  }: {
    value: string;
    sectionKey: string;
    itemIndex: number;
    fieldName: string;
    className?: string;
    children: React.ReactNode;
    multiline?: boolean;
    showEditWithAI?: boolean;
    showDelete?: boolean;
    onEditWithAI?: () => void;
    onDelete?: () => void;
  }) => {
    const isEditing = inlineEditingField?.section === sectionKey &&
      inlineEditingField?.itemIndex === itemIndex &&
      inlineEditingField?.field === fieldName;

    const isAIEditing = editingWithAI?.type === 'field' &&
      editingWithAI?.section === sectionKey &&
      editingWithAI?.itemIndex === itemIndex &&
      editingWithAI?.fieldName === fieldName;

    if (isEditing) {
      return (
        <div className={className}>
          <InlineEditField
            value={inlineEditingField.value}
            onSave={(newValue) => editItemField(sectionKey, itemIndex, fieldName, newValue)}
            className="w-full"
            multiline={multiline}
          />
        </div>
      );
    }

    return (
      <div className={className}>
        <div className="group flex items-center">
          <div className="flex-1">{children}</div>
          <ActionButtons
            onEdit={() => setInlineEditingField({ section: sectionKey, itemIndex, field: fieldName, value })}
            onEditWithAI={() => handleEditFieldWithAI(sectionKey, itemIndex, fieldName, value)}
            onDelete={onDelete}
            showEditWithAI={showEditWithAI}
            showDelete={showDelete}
          />
        </div>
        {/* Show inline AI editing under this field */}
        {isAIEditing && (
          <InlineAIEditField
            content={editingWithAI.content}
            onSubmit={(prompt) => submitInlineAIEdit(prompt)}
            onCancel={() => setEditingWithAI(null)}
          />
        )}
      </div>
    );
  };

  // Add Item Modal Component
  const AddItemModal = ({ sectionKey, onClose }: { sectionKey: string; onClose: () => void }) => {
    const getItemTemplate = (section: string) => {
      switch (section) {
        case 'work_experience':
          return { title: '', place: '', date: '', description: [''] };
        case 'personal_projects':
          return { title: '', date: '', description: [''] };
        case 'education':
          return { title: '', place: '', date: '', description: [] };
        default:
          return { description: [] };
      }
    };

    const [formData, setFormData] = useState<{
      title?: string;
      place?: string;
      date?: string;
      description: string[];
    }>(getItemTemplate(sectionKey));

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      
      // Remove empty description entries
      const cleanedData = {
        ...formData,
        description: formData.description?.filter((desc: string) => desc.trim() !== '') || []
      };
      
      addItem(sectionKey, cleanedData);
    };

    const addDescriptionField = () => {
      setFormData({
        ...formData,
        description: [...(formData.description || []), '']
      });
    };

    const updateDescription = (index: number, value: string) => {
      const newDescription = [...(formData.description || [])];
      newDescription[index] = value;
      setFormData({ ...formData, description: newDescription });
    };

    const removeDescription = (index: number) => {
      const newDescription = [...(formData.description || [])];
      newDescription.splice(index, 1);
      setFormData({ ...formData, description: newDescription });
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[60] p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 className="text-xl font-bold text-gray-900">
              Add New {getSectionTitle(sectionKey).slice(0, -1)} Item
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="flex-1 p-6 overflow-auto space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {sectionKey === 'personal_projects' ? 'Project Title' : 'Title'}
              </label>
              <input
                type="text"
                value={formData.title || ''}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            {(sectionKey === 'work_experience' || sectionKey === 'education') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {sectionKey === 'work_experience' ? 'Company' : 'Institution'}
                </label>
                <input
                  type="text"
                  value={formData.place || ''}
                  onChange={(e) => setFormData({ ...formData, place: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input
                type="text"
                value={formData.date || ''}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                placeholder="e.g., Jan 2023 - Present"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description Points
              </label>
              {formData.description?.map((desc: string, index: number) => (
                <div key={index} className="flex space-x-2 mb-2">
                  <textarea
                    value={desc}
                    onChange={(e) => updateDescription(index, e.target.value)}
                    placeholder="Enter description point..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    rows={2}
                  />
                  <button
                    type="button"
                    onClick={() => removeDescription(index)}
                    className="text-red-500 hover:text-red-700 px-2"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={addDescriptionField}
                className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
              >
                <span className="mr-1">+</span> Add description point
              </button>
            </div>

            <div className="flex space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Add Item
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  // Add deleteSection function
  const deleteSection = (sectionKey: string) => {
    if (window.confirm(`Are you sure you want to delete the entire ${sectionKey} section?`)) {
      console.log(`Delete section ${sectionKey} not yet implemented`);
      // TODO: Implement section deletion
    }
  };

  // Update canDeleteSection to allow main section deletion
  const canDeleteSection = (sectionKey: string) => {
    // Allow deletion of all sections except summary
    return sectionKey !== 'summary';
  };

  // Update handleEditBulletWithAI to use inline editing
  const handleEditBulletWithAI = (sectionKey: string, itemIndex: number, bulletIndex: number, content: string) => {
    setEditingWithAI({ 
      type: 'bullet',
      section: sectionKey, 
      itemIndex, 
      bulletIndex, 
      content 
    });
  };

  // Add function for field AI editing
  const handleEditFieldWithAI = (sectionKey: string, itemIndex: number, fieldName: string, content: string) => {
    setEditingWithAI({ 
      type: 'field',
      section: sectionKey, 
      itemIndex, 
      fieldName, 
      content 
    });
  };

  // Add function for section AI editing  
  const handleEditSectionWithAI = (sectionKey: string, content: string) => {
    handleEditSection(sectionKey);
  };

  // Update submitBulletAIEdit to work with inline editing
  const submitInlineAIEdit = async (prompt: string) => {
    if (!editingWithAI || !prompt.trim()) return;

    try {
      setIsEditing(true);
      preserveScrollPosition();
      
      if (editingWithAI.type === 'bullet') {
        // Use the dedicated bullet AI enhancement endpoint
        const response = await axios.post<{ success: boolean; message: string; updated_data: any }>(
          'http://localhost:8000/resume/edit-bullet-with-ai', {
            section_key: editingWithAI.section,
            item_index: editingWithAI.itemIndex!,
            bullet_index: editingWithAI.bulletIndex!,
            new_content: prompt
          }
        );
        
        if (response.data.success) {
          await fetchResumeContent();
          setEditingWithAI(null);
          setError(null);
        }
      } else if (editingWithAI.type === 'field') {
        // For field AI editing, we can use a similar approach or the existing edit-section endpoint
        // For now, let's use the existing section editing approach
        const formData = new FormData();
        formData.append('section_key', editingWithAI.section);
        formData.append('edit_prompt', `Improve this ${editingWithAI.fieldName}: "${editingWithAI.content}". User request: ${prompt}`);
        formData.append('use_o1_model', 'false');

        const response = await axios.post<{success: boolean; message: string; updated_section: any}>(
          'http://localhost:8000/resume/edit-section', 
          formData
        );
        
        if (response.data.success) {
          await fetchResumeContent();
          setEditingWithAI(null);
          setError(null);
        }
      } else if (editingWithAI.type === 'section') {
        // Use existing section editing
        handleEditSection(editingWithAI.section);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to edit with AI');
    } finally {
      setIsEditing(false);
    }
  };

  // Replace InlineAIEditField with a simple, clean Google/ChatGPT style search bar
  const InlineAIEditField = ({ 
    content,
    onSubmit,
    onCancel,
    className = ""
  }: {
    content: string;
    onSubmit: (prompt: string) => void;
    onCancel: () => void;
    className?: string;
  }) => {
    const [prompt, setPrompt] = useState('');
    
    const handleSubmit = () => {
      if (prompt.trim()) {
        onSubmit(prompt.trim());
      }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSubmit();
      } else if (e.key === 'Escape') {
        onCancel();
      }
    };

    return (
      <div className={`mt-2 ${className}`}>
        <div className="flex items-center space-x-2 p-2 border border-blue-300 rounded-full bg-white shadow-sm">
          <div className="flex-1 flex items-center space-x-3">
            <span className="text-blue-500 text-lg">🤖</span>
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="How would you like to improve this? (e.g., make it more quantified, add technical details...)"
              className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
              autoFocus
              disabled={isEditing}
            />
          </div>
          <div className="flex items-center space-x-1">
            {prompt.trim() && (
              <button
                onClick={handleSubmit}
                disabled={isEditing}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-full transition-colors disabled:opacity-50"
                title="Enhance with AI"
              >
                {isEditing ? (
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            )}
            <button
              onClick={onCancel}
              disabled={isEditing}
              className="p-2 text-gray-400 hover:bg-gray-50 rounded-full transition-colors disabled:opacity-50"
              title="Cancel"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    );
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
                  <div>
                    {inlineEditingField?.section === 'professional_summary' && 
                     inlineEditingField?.itemIndex === 0 && 
                     inlineEditingField?.field === 'content' ? (
                      <div className="text-gray-700 leading-relaxed">
                        <InlineEditField
                          value={inlineEditingField.value}
                          onSave={(newValue) => editItemField('professional_summary', 0, 'content', newValue)}
                          className="w-full"
                          multiline
                        />
                      </div>
                    ) : (
                      <div>
                        <div className="group flex items-start">
                          <p className="text-gray-700 leading-relaxed flex-1">
                            {structuredContent.professional_summary}
                          </p>
                          <ActionButtons
                            onEdit={() => setInlineEditingField({ 
                              section: 'professional_summary', 
                              itemIndex: 0, 
                              field: 'content', 
                              value: structuredContent.professional_summary 
                            })}
                            onEditWithAI={() => handleEditSectionWithAI('professional_summary', structuredContent.professional_summary)}
                            onDelete={() => {
                              if (window.confirm('Are you sure you want to delete the Professional Summary?')) {
                                editItemField('professional_summary', 0, 'content', '');
                              }
                            }}
                            showEditWithAI={true}
                            showDelete={true}
                          />
                        </div>
                        {/* Show inline AI editing under professional summary */}
                        {editingWithAI?.type === 'section' &&
                         editingWithAI?.section === 'professional_summary' && (
                          <InlineAIEditField
                            content={editingWithAI.content}
                            onSubmit={(prompt) => submitInlineAIEdit(prompt)}
                            onCancel={() => setEditingWithAI(null)}
                          />
                        )}
                      </div>
                    )}
                  </div>
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
      
      {/* Add Item Modal */}
      {showAddItemModal && (
        <AddItemModal
          sectionKey={showAddItemModal}
          onClose={() => setShowAddItemModal(null)}
        />
      )}

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