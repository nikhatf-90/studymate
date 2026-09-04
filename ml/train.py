"""Reproducible synthetic demonstration model; do not treat it as a validated predictor."""
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
rng=np.random.default_rng(42); n=1200
X=pd.DataFrame({"internal_marks":rng.uniform(20,100,n),"attendance":rng.uniform(40,100,n),"previous_score":rng.uniform(25,100,n),"study_hours":rng.uniform(.5,8,n),"difficulty":rng.integers(1,6,n)})
y=np.clip(.42*X.internal_marks+.25*X.attendance+.18*X.previous_score+2.5*X.study_hours-3*X.difficulty+rng.normal(0,5,n),0,100)
xa,xb,ya,yb=train_test_split(X,y,test_size=.2,random_state=42)
models={"random_forest":RandomForestRegressor(n_estimators=200,random_state=42),"gradient_boosting":GradientBoostingRegressor(random_state=42)}; scores={}
for name,m in models.items():
 m.fit(xa,ya); p=m.predict(xb); scores[name]={"MAE":mean_absolute_error(yb,p),"RMSE":mean_squared_error(yb,p)**.5,"R2":r2_score(yb,p)}
best=min(scores,key=lambda n:scores[n]["MAE"]); Path("ml/models").mkdir(parents=True,exist_ok=True); joblib.dump(models[best],"ml/models/performance_model.joblib"); pd.DataFrame(X).assign(final_score=y).to_csv("ml/data/synthetic_student_performance.csv",index=False); print({"selected":best,"metrics":scores})
