import os
os.environ["DATABASE_URL"]="sqlite:///./test_studymate.db"
from fastapi.testclient import TestClient
from backend.app.main import app
client=TestClient(app)
def test_root_route():
    r=client.get("/")
    assert r.status_code==200
    assert r.json()["status"]=="ok"
def test_registration_login_and_protected_flow():
    r=client.post("/api/auth/register",json={"email":"student@example.com","password":"securepass1","name":"Demo Student"}); assert r.status_code in (201,409)
    r=client.post("/api/auth/login",json={"email":"student@example.com","password":"securepass1"}); assert r.status_code==200
    h={"Authorization":"Bearer "+r.json()["access_token"]}; assert client.get("/api/profile",headers=h).status_code==200
    invalid=client.post("/api/subjects",headers=h,json={"name":"Math","current_marks":80,"max_marks":100,"attendance":101}); assert invalid.status_code==422
def test_protected_route_requires_token(): assert client.get("/api/subjects").status_code==401
