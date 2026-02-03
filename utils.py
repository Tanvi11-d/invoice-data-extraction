import os
from dotenv import load_dotenv
from groq import Groq
from fastapi import HTTPException
import json
import base64
from pdf2image import convert_from_path
from services import extracttext
import pathlib
import jwt
from qreader import QReader
import cv2
import Levenshtein


qreader=QReader()

load_dotenv()
API_KEY=os.getenv("GROQ_API_KEY")


def extract_image_from_pdf(file):
    try:

        file_path=file.filename
        pathlib.Path("all_pdf/").mkdir(parents=True, exist_ok=True)

        # open pdf file
        with open("all_pdf/"+file_path,"wb") as temp:
                temp.write(file.file.read())
        
                #convert pdf into image 
                images = convert_from_path("all_pdf/"+file_path,poppler_path=r"C:\Users\BitCoding Solutions\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin")
                    
                pathlib.Path("images/").mkdir(parents=True, exist_ok=True)
                
                for count,img in enumerate(images):
                    image_path =f"{file_path}{count+1}.png"
                    img.save("images/" +image_path,format='png')

        with open("images/"+image_path, "rb") as image_file:
                encoded_images = base64.b64encode(image_file.read()).decode("utf-8")



        # Use the detect_and_decode function to get the decoded QR data
        image=cv2.imread("images/"+image_path)
        decode_qr_text = qreader.detect_and_decode(image=image)
        decoded_payload=jwt.decode(decode_qr_text[0],options={"verify_signature": False})
        qr_data=json.loads(decoded_payload['data'])
       
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'facing error in extract_image_from_pdf function : {e}')
    
    return encoded_images,qr_data


def extract_text(encoded_images:str,qr_data:str) -> dict:
    try:
        prompts=f""" 
                    - Extract the information which define in pydantic model.
                    - Respond only with JSON format.
                    - strictly follow the '*' sign rules.
                    * In any pydentic model field don't changes of position/charcater in output value.
                    - "IRN" field output value give only 64 charcter length.
                    - In account_holder_name not take bank name value in output.take only if output value is present otherwise return null in output. 
                    - if you can't find any input value then write null in output.Do not write anything instead of it.
                    - you don't change position of alphanumeric char in irn field.
                    - Give proper details present in image, if not found any of deatils then return null instead of  details.
                    - given all date only dd-mm-yyyy format.
                    - length of "irn" number is 64 length and it is alphanumeric and remove "-"(Hyphen) in output value.
                    - ack_no or acknowledgement_no both are same and ack_date or acknowledgement_date both are same.Buyer or Billed to both are same.
                    - cgst_amount,sgst_utgst_amount and igst_amount are different.consigner_pincode and dealer_pincode are different.
                    - if you can't find account_holders_name in image or must be bank details then put null in output value.
                    - check the value as per validation of all the field, if value does not as per validation then write value as null.
                    - "hiib" is "HYUNDAI INDIA INSURANCE BROKING".so,extract the hiib output  details in "HYUNDAI INDIA INSURANCE BROKING" table.
                    - In only consigner_address show address.
                    - Buyer or consignee or Recipient is who buys the service or product.
                    - dealer or consigner or seller or supplier or service provide is who sells the service or product.
                    - Take total_invoice_value with Round Off Amount.
                    - micr_code is starting with 'UDYAM'.
                    - "Quantity" and "sac" are natural number.

                      
                """
        
        client = Groq(api_key=API_KEY)
        response = client.chat.completions.create(
                    model="meta-llama/llama-4-maverick-17b-128e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text":  prompts
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{encoded_images}",
                                    }
                                }
                            ]
                        }
                    ],

                          
            # response_format={"type": "json_object"}
            response_format={
                "type": "json_schema",
                "json_schema": {
                "name": "extracttext",
                "schema": extracttext.model_json_schema()}} 
                  
        )
        response_text = response.choices[0].message.content
        response_result = json.loads(response_text)
      
        try:                              
            irn_text = Levenshtein.distance(response_result["irn"], qr_data["Irn"])
            if 0<= irn_text <= 3:
                response_result["irn"] = qr_data["Irn"]
            print("response_irn:",response_result['irn'])
            print("qr_data_irn:",qr_data['Irn'])
                
            gstin=Levenshtein.distance(response_result["hiib_gstin"], qr_data["BuyerGstin"])
            if gstin <= 2:
                response_result["hiib_gstin"] = qr_data["BuyerGstin"]
            print("response_hiib_gstin:",response_result['hiib_gstin'])
            print("qr_data_buyergstin:",qr_data['BuyerGstin'])
            

            gstin_num=Levenshtein.distance(response_result["dealer_gstin"], qr_data["SellerGstin"])
            if gstin_num <= 2:
                response_result["dealer_gstin"] = qr_data["SellerGstin"]
            print("response_gstin_dealer:",response_result['dealer_gstin'])
            print("qr_data_gstin_seller:",qr_data['SellerGstin'])

        except Exception as e:
            raise HTTPException(status_code=400,  detail=f'error in string similarity : {e}')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'error in extract_text : {e}')
    
    return response_result
   

