#!/usr/bin/env python3
"""
Utility functions for chat-based resume generation.
This module provides tools for creating and managing chat-based interactions
for interactive resume generation.
"""

import os
from typing import List, Dict, Any, Optional

from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from src.utils.langchain_utils import LangChainClient


class ChatSession:
    """
    A class for managing a chat session for interactive resume generation.
    """
    
    def __init__(self, session_id: str, model_name: str = "gpt-4o-mini"):
        """
        Initialize a chat session.
        
        Args:
            session_id (str): A unique identifier for the session.
            model_name (str, optional): The name of the OpenAI model to use. Defaults to "gpt-4o-mini".
        """
        self.session_id = session_id
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model_name=model_name,
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.embeddings = OpenAIEmbeddings(
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )
        self.vector_store = None
        self.chain = None
        
    def initialize_with_context(self, 
                               resume_text: str, 
                               accomplishments: str, 
                               job_description: str, 
                               company_summary: str):
        """
        Initialize the chat session with context from the resume, accomplishments,
        job description, and company summary.
        
        Args:
            resume_text (str): The text of the resume.
            accomplishments (str): The accomplishments text.
            job_description (str): The job description text.
            company_summary (str): The company summary text.
        """
        # Combine all context into a single document
        context = f"""
        # Resume
        {resume_text}
        
        # Accomplishments
        {accomplishments}
        
        # Job Description
        {job_description}
        
        # Company Summary
        {company_summary}
        """
        
        # Create a vector store from the context
        langchain_client = LangChainClient()
        self.vector_store = langchain_client.create_vector_store_from_text(context)
        
        # Create a conversational retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            memory=self.memory
        )
        
        # Add system message to memory
        system_message = f"""
        You are a resume assistant helping the user create a tailored resume for a job application.
        You have access to the user's resume, accomplishments, the job description, and company summary.
        
        Your goal is to help the user create a resume that highlights their most relevant skills and experiences
        for the specific job they're applying to.
        
        You can:
        1. Answer questions about the job description or company
        2. Suggest skills or experiences to highlight
        3. Help rewrite sections of the resume to better match the job
        4. Provide feedback on the resume
        
        Be helpful, professional, and focused on creating the best possible resume for this specific job.
        """
        
        self.memory.chat_memory.add_user_message("Hello, I need help tailoring my resume for a job application.")
        self.memory.chat_memory.add_ai_message(
            "I'd be happy to help you tailor your resume! I have access to your resume, accomplishments, "
            "the job description, and company information. What specific aspect of your resume would you like "
            "to work on first? For example, I can help you highlight relevant skills, rewrite your professional "
            "summary, or suggest which experiences to emphasize."
        )
    
    def get_response(self, message: str) -> str:
        """
        Get a response from the chat model based on the user's message.
        
        Args:
            message (str): The user's message.
            
        Returns:
            str: The model's response.
        """
        if not self.chain:
            return "Please initialize the chat session with context first."
        
        response = self.chain({"question": message})
        return response["answer"]
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the chat history.
        
        Returns:
            List[Dict[str, str]]: The chat history as a list of dictionaries with 'role' and 'content' keys.
        """
        history = []
        for message in self.memory.chat_memory.messages:
            role = "user" if message.type == "human" else "assistant"
            history.append({"role": role, "content": message.content})
        return history


# Dictionary to store active chat sessions
active_sessions = {}


def create_chat_session(session_id: str, 
                       resume_text: str, 
                       accomplishments: str, 
                       job_description: str, 
                       company_summary: str,
                       model_name: str = "gpt-4o-mini") -> ChatSession:
    """
    Create a new chat session.
    
    Args:
        session_id (str): A unique identifier for the session.
        resume_text (str): The text of the resume.
        accomplishments (str): The accomplishments text.
        job_description (str): The job description text.
        company_summary (str): The company summary text.
        model_name (str, optional): The name of the OpenAI model to use. Defaults to "gpt-4o-mini".
        
    Returns:
        ChatSession: The created chat session.
    """
    session = ChatSession(session_id, model_name)
    session.initialize_with_context(
        resume_text=resume_text,
        accomplishments=accomplishments,
        job_description=job_description,
        company_summary=company_summary
    )
    active_sessions[session_id] = session
    return session


def get_chat_session(session_id: str) -> Optional[ChatSession]:
    """
    Get an existing chat session.
    
    Args:
        session_id (str): The unique identifier for the session.
        
    Returns:
        Optional[ChatSession]: The chat session if it exists, None otherwise.
    """
    return active_sessions.get(session_id)


def delete_chat_session(session_id: str) -> bool:
    """
    Delete a chat session.
    
    Args:
        session_id (str): The unique identifier for the session.
        
    Returns:
        bool: True if the session was deleted, False otherwise.
    """
    if session_id in active_sessions:
        del active_sessions[session_id]
        return True
    return False