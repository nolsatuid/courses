from django.test import TestCase
from http.cookies import SimpleCookie


class CourseTestCase(TestCase):

    def setUp(self):
        sessionid_dummy = "pvo9ye9rrqo0wsv9yv7k6g2t0j6254xtqd"
        self.client.cookies = SimpleCookie({'sessionid': sessionid_dummy})
