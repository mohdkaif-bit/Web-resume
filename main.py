from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import spacy
import fitz  # PyMuPDF
import docx
import re

# Load your custom NER model
nlp = spacy.load("output_ner_model3")

app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_with_regex(text):
    """Extract contact information using regex patterns"""
    # LinkedIn profile URL patterns
    linkedin_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-_]+\/?',
        r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/company\/[a-zA-Z0-9\-_]+\/?',
        r'linkedin\.com\/in\/[a-zA-Z0-9\-_]+\/?',
        r'linkedin\.com\/company\/[a-zA-Z0-9\-_]+\/?'
    ]
    
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Phone number patterns
    phone_patterns = [
        r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}',
        r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}'
    ]
    
    results = {
        "linkedin": [],
        "email": [],
        "phone": []
    }
    
    # Extract LinkedIn URLs
    for pattern in linkedin_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            url = match.group(0)
            if not url.startswith('http'):
                url = 'https://' + url
            if url not in results["linkedin"]:
                results["linkedin"].append(url)
    
    # Extract emails
    email_matches = re.finditer(email_pattern, text)
    for match in email_matches:
        if match.group(0) not in results["email"]:
            results["email"].append(match.group(0))
    
    # Extract phone numbers
    for pattern in phone_patterns:
        phone_matches = re.finditer(pattern, text)
        for match in phone_matches:
            if match.group(0) not in results["phone"]:
                results["phone"].append(match.group(0))
    
    return results

def group_entities(entities):
    """Group entities into logical categories based on labels"""
    grouped = {
        "tech_stack": [],
        "education": [],
        "experience": [],
        "personal_info": [],
        "other": []
    }
    
    for entity in entities:
        label = entity["label"]
        text = entity["text"]
        
        # Tech Skills
        if label == "TECH_SKILL":
            grouped["tech_stack"].append(entity)
        
        # Education (Institute and Degree)
        elif label in ["INSTITUTE", "DEGREE", "GRAD_YEAR"]:
            grouped["education"].append(entity)
        
        # Experience (Company and Designation)
        elif label in ["COMPANY", "DESIGNATION"]:
            grouped["experience"].append(entity)
        
        # Personal Information
        elif label in ["NAME", "DOB", "GENDER", "NATIONALITY"]:
            grouped["personal_info"].append(entity)
        
        else:
            grouped["other"].append(entity)
    
    return grouped

@app.get("/", response_class=HTMLResponse)
def form_home(request: Request):
    """Render the upload form"""
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "result": None,
        "grouped_entities": None,
        "regex_results": None
    })

@app.post("/", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile = File(...)):
    """Handle file upload and process the content"""
    file_bytes = await file.read()
    
    # Extract text based on file type
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(file.file)
    else:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "result": "❌ Unsupported file type",
            "grouped_entities": None,
            "regex_results": None
        })

    # NER extraction
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    # Group entities
    grouped_entities = group_entities(entities)
    
    # Regex extraction
    regex_results = extract_with_regex(text)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "result": entities,
        "grouped_entities": grouped_entities,
        "regex_results": regex_results
    })
