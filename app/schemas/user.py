from pydantic import BaseModel

def UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str