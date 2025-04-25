import os
import sqlite3
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Path
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles # Only for potentially serving safe files if needed, not used for the vulnerable endpoint
from pydantic import BaseModel
import aiosqlite # Using async sqlite for FastAPI
from starlette.middleware.cors import CORSMiddleware

# --- Configuration ---
UPLOAD_FOLDER = 'uploads_fastapi'
DATABASE = 'vulnerable_app_fastapi.db'
# ALLOWED_EXTENSIONS is not strictly enforced in the vulnerable upload endpoint

# --- FastAPI App Initialization ---
app = FastAPI(title="Vulnerable Instagram Clone Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Model ---
class CommentCreate(BaseModel):
    """Pydantic model for comment creation request body."""
    comment_text: str

# --- Database Setup ---
async def init_db():
    """Initializes the SQLite database asynchronously."""
    if not os.path.exists(DATABASE):
        print(f"Creating database: {DATABASE}")
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute('''
                CREATE TABLE comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_name TEXT NOT NULL,
                    comment_text TEXT NOT NULL
                )
            ''')
            await db.commit()
            print("Database initialized and 'comments' table created.")
    else:
        print(f"Database {DATABASE} already exists.")

async def get_db():
    """Provides an asynchronous database connection."""
    # For simple cases, opening a new connection per request is okay.
    # For production, consider connection pooling.
    return await aiosqlite.connect(DATABASE)

# --- Ensure Upload Folder Exists ---
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload folder: {UPLOAD_FOLDER}")

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Initialize the database when the application starts."""
    await init_db()

# --- Routes ---

@app.get('/')
async def index():
    """Basic route to confirm the server is running."""
    return {"message": "Vulnerable FastAPI App is running!"}

# --- Image Endpoints ---

@app.post("/images", status_code=201)
async def upload_image(file: UploadFile = File(...)):
    """
    Handles image uploads.
    VULNERABILITY: Unsafe File Upload.
    Does not properly validate file types or sanitize filenames.
    Allows uploading potentially malicious files (e.g., .php, .html, .sh).
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file part")
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")

    # VULNERABLE PART: No real validation or sanitization
    # Directly use the client-provided filename.
    filename = file.filename
    # Construct the path. Note: This doesn't prevent path traversal *during saving*
    # if the filename itself contains '../' etc. (e.g., '.._malicious.txt')
    # os.path.join might normalize some paths, but the core issue is trusting filename.
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Save the file directly without checking extension or content.
        # Use shutil.copyfileobj to handle the async UploadFile stream.
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"message": f"File '{filename}' uploaded successfully (potentially unsafely!)"}
    except Exception as e:
        # Basic error handling
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    finally:
        # Ensure the file pointer is closed
        await file.close()

@app.get("/images")
async def list_images():
    """Lists the names of files currently in the upload folder."""
    try:
        # Ensure we only list files, not directories
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
        return {"images": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not list files: {str(e)}")

@app.get("/images/{image_name:path}")
async def get_image(image_name: str = Path(...)):
    """
    Serves a specific file based on the provided path.
    VULNERABILITY: Local File Inclusion (LFI) / Path Traversal.
    Allows accessing files potentially outside the intended directory by manipulating 'image_name'.
    """
    # VULNERABLE PART: Directly using the user-provided 'image_name' path parameter.
    # An attacker can provide paths like '../../../../etc/passwd' (Linux)
    # or '..\\..\\..\\windows\\system.ini' (Windows).
    # We avoid using FastAPI's safe FileResponse or StaticFiles here to demonstrate the vulnerability.

    # Construct the potentially vulnerable file path relative to the app's root.
    # WARNING: This is highly insecure and for demonstration purposes only.
    # It allows reading files from anywhere the server process has permissions to read.
    vulnerable_path = os.path.abspath(os.path.join(".", image_name)) # Path relative to CWD

    # DEBUG: Print the path being accessed
    print(f"Attempting to access LFI path: {vulnerable_path}")

    # Check if the path exists and is a file
    if not os.path.exists(vulnerable_path) or not os.path.isfile(vulnerable_path):
        # To make the LFI less obvious, return 404 instead of revealing the attempt
        # In a real LFI test, you might check common file paths.
         raise HTTPException(status_code=404, detail=f"File not found at calculated path: {vulnerable_path}")
        # Alternatively, be more explicit for demonstration:
        # raise HTTPException(status_code=404, detail=f"LFI Attempt: File not found or is not a file at path: {vulnerable_path}")


    try:
        # Read the file content directly - THIS IS THE DANGEROUS PART
        with open(vulnerable_path, "rb") as f:
            content = f.read()
        # Return the raw content. Guessing the media type might fail for non-standard files.
        # For demonstration, we return as plain text or octet-stream.
        # A real attacker might exfiltrate data differently.
        media_type = "text/plain" # Default, adjust if needed based on expected file types
        if '.' in image_name:
             ext = image_name.rsplit('.', 1)[-1].lower()
             if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                 media_type = f'image/{ext}'
             elif ext == 'pdf':
                 media_type = 'application/pdf'
             # Add more specific types if needed

        return Response(content=content, media_type=media_type)

    except PermissionError:
         raise HTTPException(status_code=403, detail=f"Permission denied for path: {vulnerable_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read file at path {vulnerable_path}: {str(e)}")


# --- Comment Endpoints ---

@app.post("/comments/{image_name}", status_code=201)
async def add_comment(comment_data: CommentCreate, image_name: str = Path(...)):
    """
    Adds a comment for a given image name.
    VULNERABILITY: SQL Injection.
    Constructs the SQL query using unsafe string formatting.
    """
    db = None # Initialize db to None
    try:
        db = await get_db()
        cursor = await db.cursor()

        comment_text = comment_data.comment_text

        # VULNERABLE PART: Directly embedding user input into the SQL query.
        # An attacker can inject SQL commands via the 'comment_text'.
        # Example payload for comment_text: "Nice pic!'); INSERT INTO comments (image_name, comment_text) VALUES ('evil.jpg', 'PWNED'); --"
        # Note: The exact payload might need adjustment based on SQL dialect and context.
        #query = f"INSERT INTO comments (image_name, comment_text) VALUES ('{image_name}', '{comment_text}')"

        query = f"INSERT INTO comments (image_name, comment_text) VALUES ('{image_name}', '{comment_text}')"
        print(f"Executing VULNERABLE SQL: {query}") # Log the query for demonstration

        await cursor.executescript(query) # Execute the potentially malicious query
        await db.commit()

        # Fetch the ID of the inserted comment (optional)
        # last_id = cursor.lastrowid

        await cursor.close()
        return {"message": "Comment added successfully (potentially via SQL Injection!)", "image_name": image_name, "comment": comment_text} # "id": last_id

    except sqlite3.Error as e:
        # Catch database errors, which might indicate a failed injection attempt or other DB issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        if db:
            await db.close()


@app.get("/comments/{image_name}")
async def get_comments(image_name: str = Path(...)):
    """Retrieves all comments for a specific image name."""
    db = None
    try:
        db = await get_db()
        # Use row factory to get results as dictionaries
        db.row_factory = aiosqlite.Row
        cursor = await db.cursor()

        # Use parameterized query here for safety (contrast with the vulnerable POST endpoint)
        query = "SELECT id, image_name, comment_text FROM comments WHERE image_name = ?"
        await cursor.execute(query, (image_name,))
        comments = await cursor.fetchall()

        await cursor.close()

        # Convert Row objects to dictionaries for JSON serialization
        comments_list = [dict(comment) for comment in comments]
        return {"image_name": image_name, "comments": comments_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        if db:
            await db.close()

# --- Main execution ---
# To run this app:
# 1. Install FastAPI and Uvicorn: pip install fastapi "uvicorn[standard]" aiosqlite
# 2. Save the code as, e.g., vulnerable_main.py
# 3. Run Uvicorn: uvicorn vulnerable_main:app --reload --port 8001
#    (Use a different port like 8001 if 8000 is common)

if __name__ == "__main__":
    # This block is for running with `python vulnerable_main.py`
    # Uvicorn is the recommended way to run FastAPI apps.
    import uvicorn
    print("Starting server with Uvicorn. Recommended: run 'uvicorn vulnerable_main:app --reload --port 8001'")
    uvicorn.run(app, host="127.0.0.1", port=8001)
