import uvicorn 
from fastapi import FastAPI, Form, File, UploadFile, Header, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

import auth
from utils.util import load_config
from starlette.requests import Request
import time
import os
from utils.extract_text import pdf_extract, doc_extract
from utils.gemini_service import extract_feature_text
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
@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...), api_key: str = Security(verify_api_key)):
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
    print("data",extract_feature_text(resume_text))
    # dicts = {}
    print("Processing ", time.time()-t0)
    os.unlink(file.filename)
    return extract_feature_text(resume_text)

@app.post("/generate_api_keys")
async def generate_api_keys(account_name: str = Form(...), account_password: str = Form(...)):
    return auth.generate_api_key(account_name, account_password)

@app.post("/create_account")
async def create_account(account_name: str = Form(...), account_password: str = Form(...)):
    return auth.create_account(account_name, account_password)

if __name__ == "__main__":
	print("* Starting web service...")
	uvicorn.run(app, host=config["HOST"], port=9000 )#config["PORT"])