from utils import extract_image_from_pdf,extract_text
from fastapi import FastAPI,File,UploadFile,HTTPException
from services import extracttext
app=FastAPI()

@app.get("/")
def root():
    return {"message":"Fastapi is working"}


@app.post("/uploadfile/")
def upload(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=415, detail='Unsupported file !!!')

        result,_=extract_image_from_pdf(file)
        raw=extract_text(result,_)
        # return raw

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'error in upload  : {e}')
    
    return extracttext(**raw)

   
       

   

