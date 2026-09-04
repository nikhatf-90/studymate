from datetime import date, timedelta
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .ai.gemini import generate
from .config import settings
from .database import Base, engine, get_db
from .models import Prediction, StudentProfile, StudyPlan, StudySession, Subject, User
from .schemas import ChatIn, Login, PlanGenerate, ProfileIn, ProfileOut, QuestionIn, Register, SessionIn, SubjectIn, SubjectOut, Token
from .security import current_user, hash_password, token_for, verify_password
from .services.prediction import estimate
Base.metadata.create_all(bind=engine)
app=FastAPI(title="StudyMate AI",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(","),allow_origin_regex=r"https://([a-z0-9-]+\.)?vercel\.app$|https?://(localhost|127\.0\.0\.1)(:\d+)?$",allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.on_event("startup")
def startup(): Base.metadata.create_all(bind=engine)
@app.get("/")
def root(): return {"name":"StudyMate AI","status":"ok","docs":"/docs","health":"/api/health"}
@app.get("/api/health")
def health(): return {"status":"ok","ai_configured":bool(settings.gemini_api_key)}
@app.post("/api/auth/register",response_model=Token,status_code=201)
def register(data:Register,db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=data.email.lower()).first(): raise HTTPException(409,"An account with this email already exists")
    user=User(email=data.email.lower(),password_hash=hash_password(data.password)); db.add(user); db.flush(); db.add(StudentProfile(user_id=user.id,name=data.name)); db.add_all([Subject(user_id=user.id,name="Sample: Mathematics",current_marks=58,max_marks=100,attendance=72,previous_score=60,difficulty=4,progress=20),Subject(user_id=user.id,name="Sample: Python",current_marks=82,max_marks=100,attendance=88,previous_score=78,difficulty=3,progress=45),Subject(user_id=user.id,name="Sample: AI Fundamentals",current_marks=67,max_marks=100,attendance=76,previous_score=65,difficulty=4,progress=30)]); db.commit(); return Token(access_token=token_for(user))
@app.post("/api/auth/login",response_model=Token)
def login(data:Login,db:Session=Depends(get_db)):
    user=db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return Token(access_token=token_for(user))
@app.get("/api/profile",response_model=ProfileOut)
def profile(user:User=Depends(current_user)): return user.profile
@app.put("/api/profile",response_model=ProfileOut)
def update_profile(data:ProfileIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    for k,v in data.model_dump().items(): setattr(user.profile,k,v)
    db.commit(); db.refresh(user.profile); return user.profile
@app.get("/api/subjects",response_model=list[SubjectOut])
def subjects(user:User=Depends(current_user),db:Session=Depends(get_db)): return db.query(Subject).filter_by(user_id=user.id).all()
@app.post("/api/subjects",response_model=SubjectOut,status_code=201)
def add_subject(data:SubjectIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=Subject(user_id=user.id,**data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row
@app.put("/api/subjects/{subject_id}",response_model=SubjectOut)
def update_subject(subject_id:int,data:SubjectIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.get(Subject,subject_id)
    if not row or row.user_id!=user.id: raise HTTPException(404,"Subject not found")
    for k,v in data.model_dump().items(): setattr(row,k,v)
    db.commit(); return row
@app.delete("/api/subjects/{subject_id}",status_code=204)
def delete_subject(subject_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.get(Subject,subject_id)
    if not row or row.user_id!=user.id: raise HTTPException(404,"Subject not found")
    db.delete(row); db.commit()
@app.post("/api/predictions")
def predictions(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=[]
    for subject in db.query(Subject).filter_by(user_id=user.id):
        score,category,risk,confidence=estimate(subject,user.profile.study_hours_per_day); p=Prediction(user_id=user.id,subject_id=subject.id,score=score,category=category,risk=risk,confidence=confidence); db.add(p); rows.append({"subject_id":subject.id,"subject":subject.name,"score":score,"category":category,"risk":risk,"confidence":confidence})
    db.commit(); return {"predictions":rows,"note":"Educational planning estimates; not scientifically validated forecasts."}
@app.get("/api/predictions")
def prediction_history(user:User=Depends(current_user),db:Session=Depends(get_db)): return [{"subject_id":p.subject_id,"score":p.score,"category":p.category,"risk":p.risk,"confidence":p.confidence,"created_at":p.created_at} for p in db.query(Prediction).filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).limit(20)]
@app.post("/api/study-plan/generate")
def make_plan(data:PlanGenerate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    db.query(StudyPlan).filter_by(user_id=user.id,completed=False).delete(); subs=db.query(Subject).filter_by(user_id=user.id).all()
    if not subs: raise HTTPException(400,"Add at least one subject before generating a plan")
    today=date.today(); start="07:00" if user.profile.preferred_time.lower()=="morning" else "18:00"
    for offset in range(data.days):
        ranked=sorted(subs,key=lambda s: ((s.current_marks/s.max_marks)*100+s.attendance-s.difficulty*8),reverse=False)
        target=ranked[offset%len(ranked)]; db.add(StudyPlan(user_id=user.id,subject_id=target.id,scheduled_for=today+timedelta(days=offset),start_time=start,duration_minutes=int(user.profile.study_hours_per_day*60)))
    db.commit(); return study_plan(user,db)
@app.get("/api/study-plan")
def study_plan(user:User=Depends(current_user),db:Session=Depends(get_db)): return [{"id":p.id,"subject_id":p.subject_id,"subject":db.get(Subject,p.subject_id).name,"scheduled_for":p.scheduled_for,"start_time":p.start_time,"duration_minutes":p.duration_minutes,"completed":p.completed} for p in db.query(StudyPlan).filter_by(user_id=user.id).order_by(StudyPlan.scheduled_for).all()]
@app.put("/api/study-plan/{plan_id}")
def update_plan(plan_id:int,completed:bool,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.get(StudyPlan,plan_id)
    if not row or row.user_id!=user.id: raise HTTPException(404,"Plan item not found")
    row.completed=completed; db.commit(); return {"id":row.id,"completed":row.completed}
@app.delete("/api/study-plan/{plan_id}",status_code=204)
def delete_plan(plan_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.get(StudyPlan,plan_id)
    if not row or row.user_id!=user.id: raise HTTPException(404,"Plan item not found")
    db.delete(row); db.commit()
@app.post("/api/study-session",status_code=201)
def session(data:SessionIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    subject=db.get(Subject,data.subject_id)
    if not subject or subject.user_id!=user.id: raise HTTPException(404,"Subject not found")
    db.add(StudySession(user_id=user.id,**data.model_dump())); subject.progress=min(100,subject.progress+10); db.commit(); return {"message":"Study session recorded"}
@app.get("/api/progress")
def progress(user:User=Depends(current_user),db:Session=Depends(get_db)):
    sessions=db.query(StudySession).filter_by(user_id=user.id).all(); subs=db.query(Subject).filter_by(user_id=user.id).all(); return {"weekly_hours":round(sum(s.duration_minutes for s in sessions if s.completed_at.date()>=date.today()-timedelta(days=7))/60,1),"subject_progress":[{"name":s.name,"progress":s.progress} for s in subs],"quiz_average":round(sum(s.quiz_score for s in sessions if s.quiz_score is not None)/max(1,len([s for s in sessions if s.quiz_score is not None])),1)}
@app.get("/api/analytics")
def analytics(user:User=Depends(current_user),db:Session=Depends(get_db)):
    subs=db.query(Subject).filter_by(user_id=user.id).all(); return {"subjects":[{"name":s.name,"marks":round(s.current_marks/s.max_marks*100,1),"attendance":s.attendance,"progress":s.progress} for s in subs]}
@app.post("/api/ai/chat")
def chat(data:ChatIn,user:User=Depends(current_user)): return {"answer":generate("You are StudyMate, a careful study assistant. Do not invent facts. Explain concisely and mention uncertainty. Student asks: "+data.message)}
@app.post("/api/questions/generate")
def questions(data:QuestionIn,user:User=Depends(current_user)): return {"content":generate(f"Create {data.count} {data.difficulty} practice questions on {data.topic} for {data.subject}. Include MCQs and short answers with answers and brief explanations. Do not claim sources you do not have.")}
