import uvicorn 
from fastapi import FastAPI, Form,File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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
# =====================================================

# ============= Define Routes =============
@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
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
    return { extract_feature_text(resume_text)}


if __name__ == "__main__":
	print("* Starting web service...")
	uvicorn.run(app, host=config["HOST"], port=9000 )#config["PORT"])