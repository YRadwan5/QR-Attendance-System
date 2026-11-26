import os, sqlite3, secrets, hashlib, hmac, time, io, csv, base64, re
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import qrcode, cv2, numpy as np

ROOT=Path(__file__).resolve().parent
DB=Path(os.environ.get('ATTENDANCE_DB', ROOT/'attendance.db'))
app=FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
env=Environment(loader=FileSystemLoader(ROOT/'templates'),autoescape=select_autoescape(['html']))
def stamp(t): return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
env.filters['stamp']=stamp
@contextmanager
def db():
    c=sqlite3.connect(DB,timeout=10); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
    try:
        yield c; c.commit()
    except Exception:
        c.rollback(); raise
    finally: c.close()
def password(p,s=None):
    s=s or secrets.token_hex(16); return s+'$'+hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),600000).hex()
def verify(p,v): return hmac.compare_digest(password(p,v.split('$')[0]),v)
def digest(t): return hashlib.sha256(t.encode()).hexdigest()
def init():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE COLLATE NOCASE,student_id TEXT UNIQUE COLLATE NOCASE,role TEXT NOT NULL CHECK(role IN ('admin','instructor','student')),password TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY,name TEXT NOT NULL,code TEXT NOT NULL UNIQUE COLLATE NOCASE,instructor INTEGER NOT NULL REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS enrollments(course INTEGER REFERENCES courses(id),student INTEGER REFERENCES users(id),PRIMARY KEY(course,student));
        CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY,course INTEGER NOT NULL REFERENCES courses(id),created INTEGER NOT NULL,expires INTEGER NOT NULL,active INTEGER NOT NULL DEFAULT 1,token TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS attendance(session INTEGER REFERENCES sessions(id),student INTEGER REFERENCES users(id),recorded INTEGER NOT NULL,PRIMARY KEY(session,student));
        CREATE TABLE IF NOT EXISTS corrections(id INTEGER PRIMARY KEY,session INTEGER REFERENCES sessions(id),student INTEGER REFERENCES users(id),reason TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',created INTEGER NOT NULL,decided INTEGER,reviewer INTEGER REFERENCES users(id),decision_note TEXT,UNIQUE(session,student));
        CREATE TABLE IF NOT EXISTS logins(token TEXT PRIMARY KEY,user_id INTEGER REFERENCES users(id),expires INTEGER NOT NULL,csrf TEXT NOT NULL);
        ''')
        if not c.execute('SELECT 1 FROM users WHERE role=\'admin\'').fetchone():
            p=os.environ.get('ADMIN_PASSWORD') or secrets.token_urlsafe(15)
            if len(p)<10: raise ValueError('ADMIN_PASSWORD must be at least 10 characters')
            c.execute('INSERT INTO users(name,email,role,password) VALUES(?,?,?,?)',('Administrator','admin@example.com','admin',password(p)))
            if not os.environ.get('ADMIN_PASSWORD'): print('Initial admin password:',p,flush=True)
init()
def user(c,r):
    t=r.cookies.get('sid',''); return c.execute('SELECT u.*,l.csrf FROM logins l JOIN users u ON u.id=l.user_id WHERE l.token=? AND l.expires>?',(digest(t),int(time.time()))).fetchone()
def render(r,**kw): return HTMLResponse(env.get_template('index.html').render(**kw))
def require(condition,message):
    if not condition: raise ValueError(message)
def field(f,key,limit=200):
    v=str(f.get(key,'')).strip(); require(0<len(v)<=limit,f'Invalid {key}.'); return v
def number(f,key):
    try: return int(f.get(key,''))
    except (ValueError,TypeError): raise ValueError(f'Invalid {key}.')
def add_user(c,f,role):
    name=field(f,'name',100); email=field(f,'email',150).lower(); p=str(f.get('password','')); sid=field(f,'student_id',60) if role=='student' else None
    require(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email),'Invalid email.'); require(10<=len(p)<=128,'Password must contain 10–128 characters.')
    c.execute('INSERT INTO users(name,email,student_id,role,password) VALUES(?,?,?,?,?)',(name,email,sid,role,password(p)))
def own(c,u,course):
    require(c.execute('SELECT 1 FROM courses WHERE id=? AND instructor=?',(course,u['id'])).fetchone(),'Course not found or access denied.')
def checkin(c,u,token):
    require(u['role']=='student','Only students can check in.')
    s=c.execute('SELECT * FROM sessions WHERE token=?',(token,)).fetchone(); now=int(time.time())
    require(s,'Invalid QR code.'); require(s['active'] and s['created']<=now<s['expires'],'Session has ended or expired.')
    require(c.execute('SELECT 1 FROM enrollments WHERE course=? AND student=?',(s['course'],u['id'])).fetchone(),'You are not enrolled in this course.')
    cur=c.execute('INSERT OR IGNORE INTO attendance VALUES(?,?,?)',(s['id'],u['id'],now)); require(cur.rowcount==1,'Attendance already recorded.')
def dashboard(c,r,u,msg='',error=False):
    uid=u['id']; role=u['role']; data={}
    if role=='admin': data['users']=c.execute('SELECT id,name,email,role,student_id FROM users ORDER BY id').fetchall()
    if role=='instructor':
        data['courses']=c.execute('SELECT * FROM courses WHERE instructor=?',(uid,)).fetchall()
        data['roster']=c.execute('SELECT e.course,u.name,u.student_id FROM enrollments e JOIN users u ON u.id=e.student JOIN courses co ON co.id=e.course WHERE co.instructor=?',(uid,)).fetchall()
        data['sessions']=c.execute('SELECT s.*,co.code FROM sessions s JOIN courses co ON co.id=s.course WHERE co.instructor=? ORDER BY s.id DESC',(uid,)).fetchall()
        data['corrections']=c.execute('SELECT cr.*,u.name,co.code FROM corrections cr JOIN users u ON u.id=cr.student JOIN sessions s ON s.id=cr.session JOIN courses co ON co.id=s.course WHERE co.instructor=? ORDER BY cr.id DESC',(uid,)).fetchall()
    if role=='student':
        data['history']=c.execute('''SELECT s.id,s.created,s.active,s.expires,co.name,co.code,a.recorded,cr.status AS correction FROM enrollments e JOIN courses co ON co.id=e.course JOIN sessions s ON s.course=co.id LEFT JOIN attendance a ON a.session=s.id AND a.student=e.student LEFT JOIN corrections cr ON cr.session=s.id AND cr.student=e.student WHERE e.student=? ORDER BY s.created DESC''',(uid,)).fetchall()
        data['courses']=c.execute('SELECT co.* FROM courses co JOIN enrollments e ON co.id=e.course WHERE e.student=?',(uid,)).fetchall()
    return render(r,u=u,msg=msg,error=error,now=int(time.time()),**data)
@app.get('/',response_class=HTMLResponse)
def home(r:Request):
    with db() as c:
        u=user(c,r); return dashboard(c,r,u) if u else render(r,u=None)
@app.post('/auth')
async def auth(r:Request):
    f=await r.form()
    try:
        with db() as c:
            if f.get('action')=='register':
                add_user(c,f,'student'); return render(r,u=None,msg='Account created. Sign in.')
            email=field(f,'email',150); p=str(f.get('password','')); require(len(p)<=128,'Invalid credentials.')
            u=c.execute('SELECT * FROM users WHERE email=? OR student_id=?',(email,email)).fetchone(); require(u and verify(p,u['password']),'Invalid credentials.')
            t=secrets.token_urlsafe(32); c.execute('DELETE FROM logins WHERE expires<=?',(int(time.time()),)); c.execute('INSERT INTO logins VALUES(?,?,?,?)',(digest(t),u['id'],int(time.time())+43200,secrets.token_urlsafe(32)))
            res=RedirectResponse('/',303); res.set_cookie('sid',t,httponly=True,samesite='strict',secure=os.environ.get('HTTPS_ONLY')=='1',max_age=43200); return res
    except (ValueError,sqlite3.IntegrityError) as e: return render(r,u=None,msg=str(e) if isinstance(e,ValueError) else 'Email or student ID already exists.',error=True)
@app.post('/action')
async def action(r:Request):
    f=await r.form(); msg='Saved successfully.'
    with db() as c:
        u=user(c,r)
        if not u: return RedirectResponse('/',303)
        try:
            require(hmac.compare_digest(str(f.get('csrf','')),u['csrf']),'Invalid request. Refresh the page.'); a=f.get('action'); uid=u['id']; role=u['role']
            if a=='logout':
                c.execute('DELETE FROM logins WHERE token=?',(digest(r.cookies.get('sid','')),)); res=RedirectResponse('/',303); res.delete_cookie('sid'); return res
            if a=='profile': c.execute('UPDATE users SET name=? WHERE id=?',(field(f,'name',100),uid))
            elif a == 'delete_user':
                require(role == 'admin', 'Access denied.')

                target_id = number(f, 'user_id')

                c.execute('BEGIN IMMEDIATE')

                target = c.execute(
                    'SELECT id, role FROM users WHERE id=?',
                    (target_id,)
                ).fetchone()

                require(target, 'User not found.')
                require(target_id != uid, 'Cannot delete your own account.')
                require(target['role'] != 'admin', 'Cannot delete administrators.')

                if target['role'] == 'instructor':
                    course_count = c.execute(
                        'SELECT COUNT(*) FROM courses WHERE instructor=?',
                        (target_id,)
                    ).fetchone()[0]

                    if course_count:
                        replacement_id = number(f, 'replacement_id')

                        replacement = c.execute(
                            "SELECT id FROM users WHERE id=? AND role='instructor'",
                            (replacement_id,)
                        ).fetchone()

                        require(
                            replacement and replacement_id != target_id,
                            'Select another instructor before deleting.'
                        )

                        c.execute(
                            'UPDATE courses SET instructor=? WHERE instructor=?',
                            (replacement_id, target_id)
                        )

                c.execute(
                    'DELETE FROM corrections WHERE student=?',
                    (target_id,)
                )

                c.execute(
                    'UPDATE corrections SET reviewer=NULL WHERE reviewer=?',
                    (target_id,)
                )

                c.execute(
                    'DELETE FROM attendance WHERE student=?',
                    (target_id,)
                )

                c.execute(
                    'DELETE FROM enrollments WHERE student=?',
                    (target_id,)
                )

                c.execute(
                    'DELETE FROM logins WHERE user_id=?',
                    (target_id,)
                )

                c.execute(
                    'DELETE FROM users WHERE id=?',
                    (target_id,)
                )

                msg = 'User and associated data deleted successfully.'
            elif a=='create_user':
                require(role=='admin','Access denied.'); newrole=f.get('role'); require(newrole in ('student','instructor'),'Invalid role.'); add_user(c,f,newrole)
            elif a=='course':
                require(role=='instructor','Access denied.'); c.execute('INSERT INTO courses(name,code,instructor) VALUES(?,?,?)',(field(f,'name',100),field(f,'code',40),uid))
            elif a=='enroll':
                require(role=='instructor','Access denied.'); co=number(f,'course'); own(c,u,co); key=field(f,'student',150); st=c.execute("SELECT id FROM users WHERE role='student' AND (student_id=? OR email=?)",(key,key)).fetchone(); require(st,'Student not found.'); c.execute('INSERT INTO enrollments VALUES(?,?)',(co,st['id']))
            elif a=='session':
                require(role=='instructor','Access denied.'); co=number(f,'course'); own(c,u,co); mins=number(f,'minutes'); require(1<=mins<=180,'Duration must be 1–180 minutes.'); now=int(time.time()); c.execute('INSERT INTO sessions(course,created,expires,token) VALUES(?,?,?,?)',(co,now,now+mins*60,secrets.token_urlsafe(32)))
            elif a=='end':
                require(role=='instructor','Access denied.'); sid=number(f,'session'); s=c.execute('SELECT course FROM sessions WHERE id=?',(sid,)).fetchone(); require(s,'Session not found.'); own(c,u,s['course']); c.execute('UPDATE sessions SET active=0 WHERE id=?',(sid,))
            elif a=='checkin':
                require(role=='student','Access denied.'); token=str(f.get('token','')).strip(); upload=f.get('image')
                if upload and getattr(upload,'filename',''):
                    raw=await upload.read(5_000_001); await upload.close(); require(0<len(raw)<=5_000_000,'Image must be under 5 MB.'); img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_GRAYSCALE); require(img is not None,'Unreadable image.'); token=cv2.QRCodeDetector().detectAndDecode(img)[0]; require(token,'No readable QR code. Try again.')
                checkin(c,u,token); msg='Attendance recorded successfully.'
            elif a=='correction':
                require(role=='student','Access denied.'); sid=number(f,'session'); s=c.execute('SELECT s.* FROM sessions s JOIN enrollments e ON e.course=s.course WHERE s.id=? AND e.student=?',(sid,uid)).fetchone(); require(s,'Session not found or access denied.'); require(not s['active'] or s['expires']<=int(time.time()),'Wait until the session ends.'); c.execute('INSERT INTO corrections(session,student,reason,created) VALUES(?,?,?,?)',(sid,uid,field(f,'reason',1000),int(time.time())))
            elif a=='decide':
                require(role=='instructor','Access denied.'); cid=number(f,'correction'); cr=c.execute('SELECT cr.*,s.course FROM corrections cr JOIN sessions s ON s.id=cr.session WHERE cr.id=?',(cid,)).fetchone(); require(cr,'Request not found.'); own(c,u,cr['course']); decision=f.get('decision'); require(decision in ('approved','rejected'),'Invalid decision.'); require(cr['status']=='pending','Already decided.'); note=field(f,'note',1000); now=int(time.time()); cur=c.execute("UPDATE corrections SET status=?,decided=?,reviewer=?,decision_note=? WHERE id=? AND status='pending'",(decision,now,uid,note,cid)); require(cur.rowcount==1,'Already decided.');
                if decision=='approved': c.execute('INSERT OR IGNORE INTO attendance VALUES(?,?,?)',(cr['session'],cr['student'],now))
            else: raise ValueError('Unknown action.')
            c.commit(); return dashboard(c,r,user(c,r),msg)
        except (ValueError,sqlite3.IntegrityError,cv2.error) as e:
            c.rollback(); return dashboard(c,r,u,str(e) if isinstance(e,ValueError) else 'Duplicate or invalid data.' if isinstance(e,sqlite3.IntegrityError) else 'Unable to decode image.',True)
@app.get('/qr/{sid}')
def qr(sid:int,r:Request):
    with db() as c:
        u=user(c,r); s=c.execute('SELECT s.* FROM sessions s JOIN courses co ON co.id=s.course WHERE s.id=? AND co.instructor=?',(sid,u['id'] if u else -1)).fetchone()
        if not u or u['role']!='instructor' or not s or not s['active'] or s['expires']<=time.time(): return Response(status_code=403)
        b=io.BytesIO(); qrcode.make(s['token']).save(b,format='PNG'); return Response(b.getvalue(),media_type='image/png',headers={'Cache-Control':'no-store'})
def safe_csv(v):
    v=str(v); return "'"+v if v.startswith(('=','+','-','@','\t','\r','\n')) else v
@app.get('/export/{course}')
def export(course:int,r:Request,start:str='',end:str=''):
    with db() as c:
        u=user(c,r)
        if not u or u['role']!='instructor': return Response(status_code=403)
        try:
            own(c,u,course); lo=int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp()) if start else 0; hi=int(datetime.fromisoformat(end).replace(tzinfo=timezone.utc).timestamp())+86400 if end else 253402300799; require(lo<hi,'Invalid date range.')
        except ValueError: return Response('Invalid date range or access denied.',status_code=403)
        rows=c.execute('''SELECT u.student_id,u.name,s.id,s.created,a.recorded,s.active,s.expires FROM sessions s JOIN enrollments e ON e.course=s.course JOIN users u ON u.id=e.student LEFT JOIN attendance a ON a.session=s.id AND a.student=e.student WHERE s.course=? AND s.created>=? AND s.created<? ORDER BY s.created,u.name''',(course,lo,hi)); b=io.StringIO(); w=csv.writer(b); w.writerow(['Student ID','Name','Session','Date UTC','Status']);
        for row in rows: w.writerow([safe_csv(row['student_id']),safe_csv(row['name']),row['id'],stamp(row['created']),'Present' if row['recorded'] else 'Pending' if row['active'] and row['expires']>time.time() else 'Absent'])
        return Response('\ufeff'+b.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="course-{course}.csv"','Cache-Control':'no-store'})
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000)
