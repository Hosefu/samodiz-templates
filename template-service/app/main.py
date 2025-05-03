from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jinja2 import Template
import os

app = FastAPI(title="Template Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TemplateRequest(BaseModel):
    template: str
    data: dict

@app.get("/api/template/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/template/render")
async def render_template(request: TemplateRequest):
    try:
        template = Template(request.template)
        rendered = template.render(**request.data)
        return {"rendered": rendered}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 