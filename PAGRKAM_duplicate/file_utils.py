import os
from datetime import datetime # <--- THIS IS THE MISSING IMPORT
import io
from PIL import Image

# Ensure the necessary imports are in the original code block
# If you copied the previous version, please ensure this import is present.

UPLOAD_DIR = 'uploads'

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    print(f"Created uploads directory: {UPLOAD_DIR}")

def save_uploaded_file(uploaded_file, username, job_title):
    """
    Saves an uploaded file (Resume/CV) to the local 'uploads' directory 
    and returns the saved file path.
    """
    if uploaded_file is None:
        return None
        
    # Create a unique filename: username_job-title_timestamp.pdf
    # The error was on this line because datetime wasn't imported:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S") 
    
    # Sanitize job title for filename
    safe_job_title = job_title.replace(" ", "_").replace("(", "").replace(")", "")
    
    # Get the file extension
    file_extension = uploaded_file.name.split('.')[-1]
    
    file_name = f"{username}_{safe_job_title}_{timestamp}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        # Read the uploaded file contents
        file_bytes = uploaded_file.read()
        
        # Write the bytes to the permanent file path
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            
        return file_path
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return None