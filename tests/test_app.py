import unittest
from src.app import app, db, User
from flask import url_for
import io

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.app.post('/register', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertIn("200", str(response.status_code))

    def test_login(self):
        self.app.post('/register', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertIn(b'Upload File', response.data)

    def test_upload_file(self):
        self.app.post('/register', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        data = {
            'file': (io.BytesIO(b"test file content"), 'test.txt')
        }
        response = self.app.post('/upload', data=data, follow_redirects=True, content_type='multipart/form-data')
        self.assertNotIn(b'No file part', response.data)
        self.assertNotIn(b'No selected file', response.data)

if __name__ == '__main__':
    unittest.main()
