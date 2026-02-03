from pydantic  import BaseModel,field_validator,ValidationError
from typing import Optional
import re



class extracttext(BaseModel):
    irn : Optional[str] = re.compile(r"^[A-Za-z0-9]{64}$")
    ack_no : Optional[int] =  re.compile(r"^[0-9]{15}$")
    ack_date : Optional[str] = re.compile(r"^(\d{2}-\d{2}-\d{4})$")
    invoice_no : Optional[str] = re.compile(r"^[A-Z0-9]$")
    invoice_date : Optional[str] = re.compile(r"^(\d{2}-\d{2}-\d{4})$")
    taxable_value : Optional[float] = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")
    cgst_amount : Optional[float] 
    sgst_utgst_amount : Optional[float] 
    igst_amount : Optional[float] 
    total_invoice_value : Optional[float] = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")
    dealer_code : Optional[str] 
    hiib_misp_code : Optional[str] = re.compile(r"^(HIIB|)(-| )MHY(-| )[0-9]{4}$")
    account_holders_name : Optional[str] 
    bank_name : Optional[str] 
    account_no : Optional[int] = re.compile(r"^[0-9]{14}$")
    branch : Optional[str] 
    bank_ifsc : Optional[str] = re.compile(r"^[A-Za-z]{4}[0-9]{7}$")
    micr_code : Optional[int] 
    hiib_gstin : Optional[str] = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{2}$") 
    dealer_gstin :Optional[str] = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{2}$")
    hiib_pincode: Optional[int] 
    dealer_pincode : Optional[int] 
    hiib_state_code : Optional[int] = re.compile(r"^[0-9]{2}$")
    dealer_state_code : Optional[int] = re.compile(r"^[0-9]{2}$")
    msme_code : Optional[str]
    dealer_pan : Optional[str] = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    sac : Optional[int] = re.compile(r"^[0-9]{6}$")
    consigner_details : Optional[str] 
    consigner_address : Optional[str] 
    consigner_pincode : Optional[int] 
    consigner_place_of_supply : Optional[str]
    buyer_name : Optional[str] 
    buyer_address : Optional[str] 
    buyer_pincode :Optional[int] 
    buyer_place_of_supply : Optional[str] 
    description_of_service : Optional[str]
    oem : Optional[str] 
    quantity : Optional[int] 
    period_of_service : Optional[str]


    class Config:
        from_attributes=True

def validate_response(final: dict):
    invalidate_rows=[]
    try:
        if "irn" in final:
            "irn" == final["irn"].replace("-","")

        for field, regex in extracttext.items():
            if field in final:
                if not re.fullmatch(regex, str(final[field])):
                    invalidate_rows.append(field)
            return final,invalidate_rows
    
    except ValidationError as err:
        print(err) 

    




    
    
