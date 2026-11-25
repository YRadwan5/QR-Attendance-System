import os,tempfile,unittest,re,sqlite3,time
from pathlib import Path
TMP=tempfile.TemporaryDirectory(); os.environ['ATTENDANCE_DB']=str(Path(TMP.name)/'test.db'); os.environ['ADMIN_PASSWORD']='TestAdmin123!'
from app import app,db
from fastapi.testclient import TestClient
class Flow(unittest.TestCase):
    def test_full_workflow(self):
        admin,teacher,student,other=[TestClient(app) for _ in range(4)]
        def login(client,email,p='TestPass123!'):
            res=client.post('/auth',data={'email':email,'password':p}); self.assertEqual(res.status_code,200); self.assertIn('Sign out',res.text)
        def action(client,a,files=None,**data):
            csrf=re.search(r'name="csrf" value="([^"]+)"',client.get('/').text).group(1)
            return client.post('/action',data={'csrf':csrf,'action':a,**data},files=files).text
        self.assertIn('Invalid credentials',admin.post('/auth',data={'email':'admin@example.com','password':'wrong'}).text)
        login(admin,'admin@example.com','TestAdmin123!')
        for email in ['teacher@example.com','other@example.com']:
            self.assertIn('Saved successfully',action(admin,'create_user',role='instructor',name=email,email=email,password='TestPass123!'))
        for email,sid in [('student@example.com','S1'),('outsider@example.com','S2')]:
            self.assertIn('Account created',student.post('/auth',data={'action':'register','name':sid,'email':email,'student_id':sid,'password':'TestPass123!'}).text)
        login(teacher,'teacher@example.com'); login(student,'S1'); login(other,'other@example.com')
        self.assertIn('Saved successfully',action(teacher,'course',name='Software Engineering',code='SE101'))
        self.assertIn('Duplicate',action(teacher,'course',name='Duplicate',code='SE101'))
        self.assertIn('access denied',action(other,'enroll',course=1,student='S1'))
        self.assertIn('Saved successfully',action(teacher,'enroll',course=1,student='S1'))
        self.assertIn('Duplicate',action(teacher,'enroll',course=1,student='S1'))
        self.assertIn('Saved successfully',action(teacher,'session',course=1,minutes=15))
        qr=teacher.get('/qr/1'); self.assertEqual(qr.status_code,200); self.assertEqual(other.get('/qr/1').status_code,403)
        self.assertIn('Attendance recorded successfully',action(student,'checkin',files={'image':('qr.png',qr.content,'image/png')}))
        with db() as c: token=c.execute('SELECT token FROM sessions WHERE id=1').fetchone()[0]; original=c.execute('SELECT recorded FROM attendance').fetchone()[0]
        self.assertIn('already recorded',action(student,'checkin',token=token)); self.assertIn('Present',student.get('/').text)
        outsider=TestClient(app); login(outsider,'S2'); self.assertIn('not enrolled',action(outsider,'checkin',token=token)); self.assertNotIn('SE101',outsider.get('/').text)
        self.assertIn('Invalid QR',action(student,'checkin',token='bad')); self.assertIn('Access denied',action(student,'course',name='bad',code='bad'))
        self.assertIn('Invalid request',student.post('/action',data={'action':'profile','name':'bad'}).text)
        self.assertIn('Saved successfully',action(teacher,'end',session=1)); self.assertIn('ended or expired',action(student,'checkin',token=token))
        self.assertIn('Saved successfully',action(teacher,'session',course=1,minutes=15)); self.assertIn('Saved successfully',action(teacher,'end',session=2)); self.assertIn('Saved successfully',action(student,'correction',session=2,reason='Camera failed'))
        self.assertIn('access denied',action(other,'decide',correction=1,decision='approved',note='no'))
        self.assertIn('Saved successfully',action(teacher,'decide',correction=1,decision='approved',note='Verified'))
        self.assertIn('approved',student.get('/').text); self.assertIn('Present',teacher.get('/export/1').text); self.assertEqual(other.get('/export/1').status_code,403)
        self.assertIn('Updated',action(student,'profile',name='Updated'))
        with db() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM attendance').fetchone()[0],2); self.assertEqual(c.execute('SELECT recorded FROM attendance WHERE session=1').fetchone()[0],original)
            self.assertEqual(c.execute('SELECT role FROM users WHERE student_id=\'S1\'').fetchone()[0],'student')
        action(student,'logout'); self.assertNotIn('Sign out',student.get('/').text)
if __name__=='__main__': unittest.main(verbosity=2)
