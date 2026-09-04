from math import exp
def estimate(subject, study_hours:float):
    marks=(subject.current_marks/subject.max_marks)*100
    # Transparent deterministic fallback; ML artifact can replace this in production.
    score=max(0,min(100,.43*marks+.22*subject.attendance+.2*subject.previous_score+.09*study_hours*10-.06*(subject.difficulty-1)*10))
    confidence=round(min(92,62+subject.attendance*.22),1)
    category="Excellent" if score>=85 else "Good" if score>=70 else "Average" if score>=50 else "Needs Improvement"
    risk="Low" if score>=70 else "Medium" if score>=50 else "High"
    return round(score,1),category,risk,confidence
