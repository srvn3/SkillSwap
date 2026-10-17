import os, sqlite3, hashlib, hmac, secrets
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB = os.path.join(os.path.dirname(__file__), "skillswap.db")
app = FastAPI(title="SkillSwap API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER);
        CREATE TABLE IF NOT EXISTS skills(id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, description TEXT, skill_type TEXT);
        CREATE TABLE IF NOT EXISTS swaps(id INTEGER PRIMARY KEY, requester_id INTEGER, receiver_id INTEGER, offered_skill_id INTEGER, wanted_skill_id INTEGER, message TEXT, status TEXT DEFAULT 'pending');
        """)
init()

def auth(authorization):
    token = (authorization or "").removeprefix("Bearer ").strip()
    with db() as c:
        u = c.execute("SELECT users.id,users.name,users.email FROM sessions JOIN users ON users.id=sessions.user_id WHERE sessions.token=?", (token,)).fetchone()
    if not u:
        raise HTTPException(401, "Please log in")
    return dict(u)

def pw_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    return salt + ":" + hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120000).hex()

class Register(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class Skill(BaseModel):
    name: str
    description: str = ""
    skill_type: str = "offered"

class Swap(BaseModel):
    receiver_id: int
    offered_skill_id: int
    wanted_skill_id: int
    message: str = ""

@app.get("/")
def home():
    return {"message": "SkillSwap API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/auth/register")
def register(x: Register):
    if not x.name.strip() or len(x.password) < 4:
        raise HTTPException(400, "Enter name and password of at least 4 characters")
    try:
        with db() as c:
            c.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)", (x.name.strip(), x.email.strip().lower(), pw_hash(x.password)))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Email already registered")
    return login(Login(email=x.email, password=x.password))

@app.post("/api/auth/login")
def login(x: Login):
    with db() as c:
        u = c.execute("SELECT * FROM users WHERE email=?", (x.email.strip().lower(),)).fetchone()
        if not u:
            raise HTTPException(401, "Invalid email or password")
        try:
            salt, stored = u["password"].split(":")
            valid = hmac.compare_digest(pw_hash(x.password, salt).split(":")[1], stored)
        except Exception:
            valid = False
        if not valid:
            raise HTTPException(401, "Invalid email or password")
        token = secrets.token_urlsafe(32)
        c.execute("INSERT INTO sessions VALUES(?,?)", (token, u["id"]))
    return {"access_token": token, "token_type": "bearer", "user": {"id": u["id"], "name": u["name"], "email": u["email"]}}

@app.get("/api/profile/me")
def me(authorization: Optional[str] = Header(None)):
    return auth(authorization)

@app.get("/api/skills")
def skills():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT s.*,u.name owner_name FROM skills s JOIN users u ON u.id=s.user_id ORDER BY s.id DESC")]

@app.get("/api/skills/mine")
def mine(authorization: Optional[str] = Header(None)):
    u = auth(authorization)
    return [s for s in skills() if s["user_id"] == u["id"]]

@app.post("/api/skills")
def add(x: Skill, authorization: Optional[str] = Header(None)):
    u = auth(authorization)
    if x.skill_type not in ("offered", "wanted") or not x.name.strip():
        raise HTTPException(400, "Invalid skill")
    with db() as c:
        cur = c.execute("INSERT INTO skills(user_id,name,description,skill_type) VALUES(?,?,?,?)", (u["id"], x.name.strip(), x.description.strip(), x.skill_type))
    return {"id": cur.lastrowid}

@app.delete("/api/skills/{sid}")
def delete_skill(sid: int, authorization: Optional[str] = Header(None)):
    u = auth(authorization)
    with db() as c:
        s = c.execute("SELECT * FROM skills WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "Skill not found")
        if s["user_id"] != u["id"]:
            raise HTTPException(403, "Not your skill")
        if c.execute("SELECT 1 FROM swaps WHERE offered_skill_id=? OR wanted_skill_id=?", (sid, sid)).fetchone():
            raise HTTPException(409, "Skill used in a swap")
        c.execute("DELETE FROM skills WHERE id=?", (sid,))
    return {"ok": True}

@app.post("/api/swaps")
def request(x: Swap, authorization: Optional[str] = Header(None)):
    u = auth(authorization)
    with db() as c:
        offered = c.execute("SELECT * FROM skills WHERE id=?", (x.offered_skill_id,)).fetchone()
        wanted = c.execute("SELECT * FROM skills WHERE id=?", (x.wanted_skill_id,)).fetchone()
        if not offered or not wanted or offered["user_id"] != x.receiver_id or wanted["user_id"] != u["id"] or offered["skill_type"] != "offered" or wanted["skill_type"] != "wanted" or x.receiver_id == u["id"]:
            raise HTTPException(400, "Choose another student's offered skill and your wanted skill")
        cur = c.execute("INSERT INTO swaps(requester_id,receiver_id,offered_skill_id,wanted_skill_id,message) VALUES(?,?,?,?,?)", (u["id"], x.receiver_id, x.offered_skill_id, x.wanted_skill_id, x.message))
    return {"id": cur.lastrowid, "status": "pending"}

@app.get("/api/swaps")
def get_swaps(authorization: Optional[str] = Header(None)):
    u = auth(authorization)
    with db() as c:
        return [dict(r) for r in c.execute("""
            SELECT s.*,a.name requester_name,b.name receiver_name,
                   o.name offered_name,w.name wanted_name
            FROM swaps s
            JOIN users a ON a.id=s.requester_id
            JOIN users b ON b.id=s.receiver_id
            JOIN skills o ON o.id=s.offered_skill_id
            JOIN skills w ON w.id=s.wanted_skill_id
            WHERE s.requester_id=? OR s.receiver_id=?
            ORDER BY s.id DESC
        """, (u["id"], u["id"]))]

@app.patch("/api/swaps/{sid}")
def decide(sid: int, decision: str, authorization: Optional[str] = Header(None)):
    u = auth(authorization)
    if decision not in ("accepted", "rejected"):
        raise HTTPException(400, "Invalid decision")
    with db() as c:
        s = c.execute("SELECT * FROM swaps WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "Request not found")
        if s["receiver_id"] != u["id"]:
            raise HTTPException(403, "Only receiver can respond")
        if s["status"] != "pending":
            raise HTTPException(409, "Already decided")
        c.execute("UPDATE swaps SET status=? WHERE id=?", (decision, sid))
    return {"status": decision}
