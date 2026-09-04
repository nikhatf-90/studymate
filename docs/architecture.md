# StudyMate AI architecture

```text
[Student browser] → React + Vite dashboard → FastAPI JWT/API validation
                                             ├─ SQLite / PostgreSQL SQLAlchemy
                                             ├─ ML model / estimates
                                             └─ Gemini API (server key in .env)
```

Registration hashes passwords before persistence. Login returns a signed JWT, and academic endpoints resolve the current user from that token. Gemini credentials never reach the browser.
