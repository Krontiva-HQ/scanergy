"""
Scarnergy Report Engine — PDF generation via WeasyPrint + Jinja2.
See docs/13-INSPECTION-WORKFLOW.md for report templates.
"""
from fastapi import FastAPI

app = FastAPI(title="Scarnergy Report Engine", version="2.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/generate/{inspection_id}")
async def generate_report(inspection_id: str):
    return {"status": "pending", "inspection_id": inspection_id}
