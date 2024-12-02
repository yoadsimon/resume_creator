from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os
from run_all import create_resume_for_job_application

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Application started! You can access the API docs at: http://127.0.0.1:8000/docs")


@app.post("/generate_resume")
async def generate_resume(
        resume_file: UploadFile = File(...),
        accomplishments_file: UploadFile = File(None),
        job_description_link: str = Form(...),
        company_base_link: str = Form(...),
        company_name: str = Form(None),
        force_run_all: bool = Form(False),
        use_o1_model: bool = Form(False)
):
    if force_run_all and os.path.exists('temp'):
        shutil.rmtree('temp')

    os.makedirs('temp', exist_ok=True)
    os.makedirs('result', exist_ok=True)

    resume_file_path = f"temp/{resume_file.filename}"
    with open(resume_file_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)
    accomplishments_file_path = None
    if accomplishments_file is not None:
        accomplishments_file_path = f"temp/{accomplishments_file.filename}"
        with open(accomplishments_file_path, "wb") as buffer:
            shutil.copyfileobj(accomplishments_file.file, buffer)

    create_resume_for_job_application(
        resume_file_path=resume_file_path,
        accomplishments_file_path=accomplishments_file_path,
        job_description_link=job_description_link,
        company_base_link=company_base_link,
        company_name=company_name,
        force_run_all=force_run_all,
        use_o1_model=use_o1_model
    )

    result_file = 'result/resume.docx'
    if os.path.exists(result_file):
        return FileResponse(
            path=result_file,
            filename='resume.docx',
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    else:
        return {"error": "Resume generation failed."}
