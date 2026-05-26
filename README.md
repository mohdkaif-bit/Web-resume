# 🧠 Resume Parsing using NER (Named Entity Recognition)

An end-to-end NLP project to extract and structure information from resumes using **BERT-based Named Entity Recognition (NER)** with **relational linking**.

---

## 🚀 Overview

This project focuses on converting unstructured resume data into structured, machine-readable format. It goes beyond simple entity extraction by linking related entities (e.g., ROLE → COMPANY, PROJECT → TECH).

---

## 🎯 Problem Statement

Resumes are typically unstructured, making it difficult to:
- Extract key information (Name, Skills, Experience)
- Understand relationships between entities
- Use the data in downstream systems (HR tools, ATS, analytics)

---

## 💡 Solution

- Built a **custom NER model using BERT**
- Annotated resumes with entities and relationships
- Implemented **relational entity linking**
- Structured outputs into JSON format for real-world usage

---

## 🏗️ Pipeline

1. **Data Collection**
   - 2000+ resume samples

2. **Annotation**
   - Tools: Label Studio
   - Entities:
     - NAME, COMPANY, ROLE, DURATION
     - PROJECT_NAME, TECH_USED, RESPONSIBILITY
     - DEGREE, INSTITUTE, etc.

3. **Model Training**
   - Fine-tuned BERT for domain-specific NER

4. **Entity Linking**
   - Connected entities:
     - ROLE ➝ COMPANY  
     - RESPONSIBILITY ➝ ROLE  
     - TECH_USED ➝ PROJECT  

5. **Post-processing**
   - Converted predictions into structured JSON

---

## 📊 Results

- ✅ ~85–90% entity extraction accuracy  
- ✅ Improved structured data quality using relational linking  
- ✅ Reduced ambiguity in extracted information  

---

## 🛠️ Tech Stack

- Python  
- BERT (Transformers)  
- spaCy  
- Label Studio  
- FastAPI (for API deployment)

---

## 📂 Output Example

```json
{
  "name": "John Doe",
  "skills": ["Python", "Machine Learning"],
  "experience": [
    {
      "company": "ABC Corp",
      "role": "ML Engineer",
      "duration": "2 years",
      "responsibilities": ["Model development", "Data preprocessing"]
    }
  ]
}
