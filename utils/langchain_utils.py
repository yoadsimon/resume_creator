"""
Utility functions and classes for LangChain integration.
This module provides tools for working with LangChain, including prompt templates,
LLM chains, and vector databases for semantic search.
"""

import os
from typing import List, Dict, Any, Optional

from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.sequential import SequentialChain
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
import tempfile
import shutil

from utils.open_ai import OpenAIClient


class LangChainClient:
    """
    Client for interacting with LangChain.
    Provides methods for creating prompt templates, LLM chains, and vector databases.
    """
    
    def __init__(self, model_name="gpt-4o-mini"):
        """
        Initialize the LangChain client.
        
        Args:
            model_name (str): The name of the OpenAI model to use.
        """
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model_name=model_name,
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )
        self.embeddings = OpenAIEmbeddings(
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )
        # Create a temporary directory for ChromaDB
        self.chroma_temp_dir = tempfile.mkdtemp(prefix="chroma_")
    
    def __del__(self):
        """Clean up temporary directory when client is destroyed."""
        if hasattr(self, 'chroma_temp_dir') and os.path.exists(self.chroma_temp_dir):
            shutil.rmtree(self.chroma_temp_dir, ignore_errors=True)
    
    def create_prompt_template(self, template: str, input_variables: List[str]) -> PromptTemplate:
        """
        Create a prompt template.
        
        Args:
            template (str): The template string.
            input_variables (List[str]): The input variables for the template.
            
        Returns:
            PromptTemplate: The prompt template.
        """
        return PromptTemplate(template=template, input_variables=input_variables)
    
    def create_llm_chain(self, prompt_template: PromptTemplate, output_key: str = "text") -> LLMChain:
        """
        Create an LLM chain.
        
        Args:
            prompt_template (PromptTemplate): The prompt template.
            output_key (str): The key for the output.
            
        Returns:
            LLMChain: The LLM chain.
        """
        return LLMChain(llm=self.llm, prompt=prompt_template, output_key=output_key)
    
    def create_sequential_chain(self, chains: List[LLMChain], input_variables: List[str], 
                               output_variables: List[str]) -> SequentialChain:
        """
        Create a sequential chain.
        
        Args:
            chains (List[LLMChain]): The chains to sequence.
            input_variables (List[str]): The input variables for the chain.
            output_variables (List[str]): The output variables for the chain.
            
        Returns:
            SequentialChain: The sequential chain.
        """
        return SequentialChain(
            chains=chains,
            input_variables=input_variables,
            output_variables=output_variables
        )
    
    def create_vector_store(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> Chroma:
        """
        Create a vector store from texts using ChromaDB.
        
        Args:
            texts (List[str]): The texts to embed.
            metadatas (Optional[List[Dict[str, Any]]]): Metadata for each text.
            
        Returns:
            Chroma: The vector store.
        """
        return Chroma.from_texts(
            texts=texts, 
            embedding=self.embeddings, 
            metadatas=metadatas,
            persist_directory=self.chroma_temp_dir
        )
    
    def create_vector_store_from_text(self, text: str, chunk_size: int = 1000, 
                                     chunk_overlap: int = 200) -> Chroma:
        """
        Create a vector store from a single text by splitting it into chunks.
        
        Args:
            text (str): The text to embed.
            chunk_size (int): The size of each chunk.
            chunk_overlap (int): The overlap between chunks.
            
        Returns:
            Chroma: The vector store.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_text(text)
        return self.create_vector_store(chunks)
    
    def create_retrieval_qa_chain(self, vector_store: Chroma, prompt_template: Optional[PromptTemplate] = None) -> RetrievalQA:
        """
        Create a retrieval QA chain.
        
        Args:
            vector_store (Chroma): The vector store.
            prompt_template (Optional[PromptTemplate]): The prompt template.
            
        Returns:
            RetrievalQA: The retrieval QA chain.
        """
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        if prompt_template:
            return RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt_template}
            )
        else:
            return RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever
            )
    
    def semantic_search(self, vector_store: Chroma, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search on a vector store.
        
        Args:
            vector_store (Chroma): The vector store.
            query (str): The query.
            k (int): The number of results to return.
            
        Returns:
            List[Dict[str, Any]]: The search results.
        """
        return vector_store.similarity_search(query, k=k)


def create_resume_generation_chain(client: LangChainClient, use_o1_model: bool = False):
    """
    Create a chain for generating a resume.
    
    Args:
        client (LangChainClient): The LangChain client.
        use_o1_model (bool): Whether to use the o1 model.
        
    Returns:
        SequentialChain: The resume generation chain.
    """
    # Step 1: Extract key skills from job description
    skills_template = """
    List the key skills and requirements in this job description:

    {job_description}

    Skills:
    """
    skills_prompt = client.create_prompt_template(
        template=skills_template,
        input_variables=["job_description"]
    )
    skills_chain = client.create_llm_chain(skills_prompt, output_key="skills")
    
    # Step 2: Generate resume using skills, job description, company summary, and accomplishments
    resume_template = """
    You are an expert resume writer specializing in crafting resumes for professionals in the {job_industry} industry. 
    Your task is to create a compelling, tailored resume that aligns with the job I'm applying for, highlighting my most relevant skills and experiences.

    **Job Description:**
    {job_description}

    **Company Summary:**
    {company_summary}

    **Key Skills Required:**
    {skills}

    **My Accomplishments and Experience:**
    {accomplishments}

    **Instructions:**
    - **Focus on Relevance**: Only include skills, experiences, and accomplishments that are directly relevant to the job description and company values.
    - **Exclude Irrelevant Content**: Do not include any accomplishments or experiences that are not pertinent to the job requirements.
    - **Use Professional Language**: Employ a professional tone with strong action verbs and industry-specific terminology.
    - **Quantify Achievements**: Include measurable results and specific examples to demonstrate the impact of my work.
    - **Incorporate Keywords**: Use keywords from the job description to optimize the resume for Applicant Tracking Systems (ATS).
    - **Format**: Structure the resume in the following JSON format:
    ```
    {{
      "Professional Summary": "Your professional summary here.",
      "Work Experience": [
        {{"title": "Job Title 1", "place": "Company Name 1", "date": "Date Range 1", "description": "[Description of responsibilities and achievements in bullet points.]"}},
        {{"title": "Job Title 2", "place": "Company Name 2", "date": "Date Range 2", "description": "[Description of responsibilities and achievements in bullet points.]"}},
        ...
      ],
      "Personal Projects": [
        {{"title": "Project Title 1", "date": "Date Range 1", "description": "[Description of the project, your role, and achievements in bullet points.]"}},
        {{"title": "Project Title 2", "date": "Date Range 2", "description": "[Description of the project, your role, and achievements in bullet points.]"}},
        ...
      ],
      "Education": [
        {{"title": "Degree or Certification 1", "place": "Institution Name 1", "description": "[Relevant coursework, honors, or achievements in bullet points.]"}},
        {{"title": "Degree or Certification 2", "place": "Institution Name 2", "description": "[Relevant coursework, honors, or achievements in bullet points.]"}},
        ...
      ],
      "Skills": ["Skill1", "Skill2", ...],
      "Languages": ["Language1", "Language2", ...]
    }}
    ```
    - **Formatting Preferences**: Provide the output strictly in the JSON format shown above without any additional text or explanations.
    - **Customization**: Tailor each section to demonstrate how my background makes me an ideal candidate for this specific position.
    - **Exclude Personal Information**: Do not include personal details such as age, marital status, or photo.
    - **Avoid Repetition**: Ensure that the content is varied and that each point provides new information.
    - **Emphasize Relevance**: Exclude any information that is not directly related to the job description or required qualifications.

    Please generate the resume accordingly, ensuring that it is polished, professional, and positions me as a strong candidate for the role. Output the result in the specified JSON format only.
    """
    
    resume_prompt = client.create_prompt_template(
        template=resume_template,
        input_variables=["job_description", "company_summary", "skills", "accomplishments", "job_industry"]
    )
    resume_chain = client.create_llm_chain(resume_prompt, output_key="resume")
    
    # Create the sequential chain
    chain = client.create_sequential_chain(
        chains=[skills_chain, resume_chain],
        input_variables=["job_description", "company_summary", "accomplishments", "job_industry"],
        output_variables=["resume"]
    )
    
    return chain


def create_accomplishments_extraction_chain(client: LangChainClient):
    """
    Create a chain for extracting accomplishments from a resume.
    
    Args:
        client (LangChainClient): The LangChain client.
        
    Returns:
        LLMChain: The accomplishments extraction chain.
    """
    template = """
    You are a professional resume assistant.

    Please extract accomplishments from the following resume text:

    {resume_text}

    Organize the accomplishments under the appropriate headings:
    - "Professional Experience"
    - "Personal Projects"
    - "Education"

    Ensure the final result is a consolidated list of accomplishments presented in a clear, consistent format.

    Do not include any additional explanations or text. Provide only the accomplishments.
    """
    
    prompt = client.create_prompt_template(
        template=template,
        input_variables=["resume_text"]
    )
    
    return client.create_llm_chain(prompt, output_key="accomplishments")


def create_combined_accomplishments_chain(client: LangChainClient):
    """
    Create a chain for combining existing accomplishments with new ones.
    
    Args:
        client (LangChainClient): The LangChain client.
        
    Returns:
        LLMChain: The combined accomplishments chain.
    """
    template = """
    You are a professional resume assistant.

    Given the following existing accomplishments:

    {existing_accomplishments}

    And the following resume text:

    {resume_text}

    Please extract any new accomplishments not already included in the existing accomplishments.
    Merge them into the existing accomplishments under the appropriate headings:
    - "Professional Experience"
    - "Personal Projects"
    - "Education"

    Ensure the final result is a consolidated list of accomplishments with no duplicate entries,
    presented in the same format.

    Do not include any additional explanations or text. Provide only the updated accomplishments.
    """
    
    prompt = client.create_prompt_template(
        template=template,
        input_variables=["existing_accomplishments", "resume_text"]
    )
    
    return client.create_llm_chain(prompt, output_key="combined_accomplishments")


def create_personal_details_extraction_chain(client: LangChainClient):
    """
    Create a chain for extracting personal details from a resume.
    
    Args:
        client (LangChainClient): The LangChain client.
        
    Returns:
        LLMChain: The personal details extraction chain.
    """
    template = """
    Extract and return ONLY the personal details mentioned in the following text in the JSON format with keys: name, phone_number, linkedin, github, email, and address:

    {resume_text}
    """
    
    prompt = client.create_prompt_template(
        template=template,
        input_variables=["resume_text"]
    )
    
    return client.create_llm_chain(prompt, output_key="personal_details")