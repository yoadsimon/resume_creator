import os
import sys
import logging
import uuid
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.chat_utils import create_chat_session, get_chat_session, delete_chat_session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_chat_interface():
    """
    Test the interactive chat interface functionality.
    This tests the ability to create a chat session, send messages, and get responses.
    """
    logging.info("Testing chat interface functionality...")
    
    # Ensure the sample files exist
    resume_path = 'tests/data/sample_resume.docx'
    accomplishments_path = 'tests/data/sample_accomplishments.txt'
    
    if not os.path.exists(resume_path) or not os.path.exists(accomplishments_path):
        logging.error("Sample files not found. Please run generate_test_files.py first.")
        return False
    
    try:
        # Read the sample files
        with open(accomplishments_path, 'r') as f:
            accomplishments = f.read()
        
        # For resume, we'd normally extract text from the DOCX, but for testing we'll use a placeholder
        resume_text = "John Doe - Software Engineer with experience in Python, JavaScript, and cloud technologies."
        
        # Sample job description and company summary
        job_description = "We are looking for a software engineer with experience in Python, cloud technologies, and machine learning."
        company_summary = "ABC Tech is a leading technology company specializing in cloud solutions and machine learning applications."
        
        # Create a chat session
        session_id = str(uuid.uuid4())
        logging.info(f"Creating chat session with ID: {session_id}")
        
        create_chat_session(
            session_id=session_id,
            resume_text=resume_text,
            accomplishments=accomplishments,
            job_description=job_description,
            company_summary=company_summary,
            model_name="gpt-4o-mini"  # Use a smaller model for testing
        )
        
        # Get the chat session
        session = get_chat_session(session_id)
        if not session:
            logging.error("Failed to create chat session")
            return False
        
        logging.info("Chat session created successfully")
        
        # Test sending messages and getting responses
        test_messages = [
            "What skills from my resume match this job description?",
            "Can you help me highlight my machine learning experience?",
            "What should I emphasize in my professional summary?"
        ]
        
        for i, message in enumerate(test_messages):
            logging.info(f"\nTest message {i+1}: {message}")
            
            # Get response
            response = session.get_response(message)
            
            # Check if we got a response
            if not response:
                logging.error(f"No response received for message: {message}")
                return False
            
            logging.info(f"Response: {response[:100]}...")  # Show first 100 chars of response
        
        # Test getting chat history
        history = session.get_chat_history()
        logging.info(f"\nChat history contains {len(history)} messages")
        
        # Check if history contains our messages
        if len(history) < len(test_messages) * 2:  # Each message should have a response
            logging.error(f"Chat history is incomplete. Expected at least {len(test_messages) * 2} messages, got {len(history)}")
            return False
        
        # Test deleting the chat session
        success = delete_chat_session(session_id)
        if not success:
            logging.error("Failed to delete chat session")
            return False
        
        # Verify the session was deleted
        if get_chat_session(session_id):
            logging.error("Chat session still exists after deletion")
            return False
        
        logging.info("Chat session deleted successfully")
        logging.info("\nChat interface test completed successfully!")
        return True
            
    except Exception as e:
        logging.error("Error during chat interface test: %s", str(e))
        return False

if __name__ == "__main__":
    # First make sure we have the sample files
    if not os.path.exists('tests/data/sample_resume.docx') or not os.path.exists('tests/data/sample_accomplishments.txt'):
        logging.info("Sample files not found. Running generate_test_files.py...")
        try:
            from generate_test_files import generate_all_sample_files
            generate_all_sample_files()
        except Exception as e:
            logging.error("Failed to generate sample files: %s", str(e))
            sys.exit(1)
    
    # Run the test
    success = test_chat_interface()
    
    if success:
        logging.info("All tests passed!")
        sys.exit(0)
    else:
        logging.error("Tests failed!")
        sys.exit(1)