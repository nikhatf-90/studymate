from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
class Register(BaseModel): email: EmailStr; password: str=Field(min_length=8,max_length=128); name: str=Field(min_length=2,max_length=120)
class Login(BaseModel): email: EmailStr; password: str
class Token(BaseModel): access_token: str; token_type: str="bearer"
class ProfileIn(BaseModel): name: str=Field(min_length=2); course: str=""; semester: str=""; study_hours_per_day: float=Field(default=2,gt=0,le=16); preferred_time: str="Evening"
class ProfileOut(ProfileIn): model_config=ConfigDict(from_attributes=True); id:int
class SubjectIn(BaseModel): name:str=Field(min_length=2,max_length=120); current_marks:float=Field(ge=0); max_marks:float=Field(gt=0); attendance:float=Field(ge=0,le=100); previous_score:float=Field(default=0,ge=0,le=100); difficulty:int=Field(default=3,ge=1,le=5); exam_date:date|None=None; progress:float=Field(default=0,ge=0,le=100)
class SubjectOut(SubjectIn): model_config=ConfigDict(from_attributes=True); id:int
class PlanGenerate(BaseModel): days:int=Field(default=7,ge=1,le=28)
class SessionIn(BaseModel): subject_id:int; duration_minutes:int=Field(gt=0,le=960); quiz_score:float|None=Field(default=None,ge=0,le=100)
class ChatIn(BaseModel): message:str=Field(min_length=2,max_length=6000)
class QuestionIn(BaseModel): subject:str=Field(min_length=2); topic:str=Field(min_length=2); difficulty:str; count:int=Field(default=5,ge=1,le=10)
