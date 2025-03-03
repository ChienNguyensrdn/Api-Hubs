import uvicorn 
from fastapi import FastAPI, Form, File, UploadFile, Header, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

import auth
from utils.mongodb_client import MongoDbClient
from utils.util import load_config
from starlette.requests import Request
import time
import os
from utils.extract_text import pdf_extract, doc_extract
from utils.gemini_service import extract_feature_text
import recommender_system as recommender
origins = [
    "*"
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============= Define Config And Setting =============
CONFIG_PATH = "configs/config.yaml"
config = load_config(CONFIG_PATH)

API_KEY_NAME = "X-API-Key"
ACCOUNT_NAME_HEADER = "X-Account-Name"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
account_name_header = APIKeyHeader(name=ACCOUNT_NAME_HEADER, auto_error=False)

async def verify_api_key(
    api_key: str = Security(api_key_header),
    account_name: str = Security(account_name_header)
):
    if not auth.verify_message(api_key, account_name):
        raise HTTPException(status_code=403, detail="Invalid API Key or Signature")
    return api_key
# =====================================================

# ============= Define Routes =============
@app.post("/upload_resume")
async def upload_resume(request: Request, file: UploadFile = File(...), api_key: str = Security(verify_api_key)):
    '''
        Upload the file to the server
        pdf, doc, docx are allowed
        Step 1 : Save the file to the server
        Step 2 : Extract the text from the file
        Step 3 : Return json response with the extracted text 
    '''
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    
    tmp_path = file.filename
    t0 = time.time()
    ImageBase64 = ''
    if ".pdf" in str(tmp_path):
        resume_text,ImageBase64 = pdf_extract(tmp_path)
    else:
        resume_text = doc_extract(bytes(tmp_path))
    resume_text = resume_text.replace("\t", " \t")
    # print("data",extract_feature_text(resume_text, ))
    # dicts = {}
    print("Processing ", time.time()-t0)
    os.unlink(file.filename)
    return extract_feature_text(resume_text, "resume")

@app.post("/upload_capstone")
async def upload_capstone(request: Request, file: UploadFile = File(...), api_key: str = Security(verify_api_key)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    # Khởi tạo connection mongoDb
    mongodb = MongoDbClient().get_db()
    collections = mongodb["capstone_idea"]

    # Lấy Project_code
    tmp_path = file.filename
    if ".pdf" in str(tmp_path):
        resume_text,ImageBase64 = pdf_extract(tmp_path)
    else:
        resume_text = doc_extract(bytes(tmp_path.encode("utf8")))
    resume_text = resume_text.replace("\t", " \t")
    project_code = tmp_path[:9]
    print("Project Code: ", project_code)

    # Kiểm Project_code có tồn tại chưa
    found_project_code = collections.find_one({"project_code": project_code})

    if found_project_code is not None:
        raise HTTPException(status_code=400, detail="This capstone project code already exists")
    t0 = time.time()
    print("Processing ", time.time() - t0)
    os.unlink(file.filename)
    result = extract_feature_text(resume_text, "capstone")


    collections.insert_one({
        **result,
        "project_code":project_code,
    })
    return result

# class model for recommder
class CandidateInput(BaseModel):
    candidate_input: str
@app.post("/recommend_jobs")
async def recommend_jobs(data: CandidateInput, api_key: str = Security(verify_api_key)):
    return recommender.recommend_jobs(data.candidate_input)

@app.post("/recommend_users")
async def recommend_users(data: CandidateInput):
    return recommender.recommend_jobs(data.candidate_input)
@app.post("/generate_api_keys")
async def generate_api_keys(account_name: str = Form(...), account_password: str = Form(...)):
    return auth.generate_api_key(account_name, account_password)

@app.post("/create_account")
async def create_account(account_name: str = Form(...), account_password: str = Form(...)):
    return auth.create_account(account_name, account_password)

if __name__ == "__main__":
	print("* Starting web service...")
	uvicorn.run(app, host=config["HOST"], port=9000 )#config["PORT"])