'''
test_http_auth_detect.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import unittest

import core.data.kb.knowledgeBase as kb

from core.data.url.httpResponse import httpResponse
from core.data.request.fuzzable_request import fuzzable_request
from core.data.parsers.urlParser import url_object
from core.controllers.core_helpers.fingerprint_404 import fingerprint_404_singleton
from plugins.grep.http_auth_detect import http_auth_detect


class test_http_auth_detect(unittest.TestCase):
    
    def setUp(self):
        fingerprint_404_singleton( [False, False, False] )
        self.url = url_object('http://www.w3af.com/') 
        self.request = fuzzable_request(self.url, method='GET')
        self.plugin = http_auth_detect()
        kb.kb.cleanup()
        
    def tearDown(self):
        self.plugin.end()
            
    def test_http_auth_detect_negative(self):
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, '' , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'auth')), 0 )
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'userPassUri')), 0 )
        
    def test_http_auth_detect_negative_long(self):
        body = 'ABC ' * 10000
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'auth')), 0 )
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'userPassUri')), 0 )
    
    def test_http_auth_detect_uri(self):
        body = 'ABC ' * 100
        body += 'http://abc:def@www.w3af.com/foo.bar'
        body += '</br> ' * 50
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'auth')), 0 )
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'userPassUri')), 1 )
    
    def test_http_auth_detect_non_rfc(self):
        body = ''
        headers = {'content-type': 'text/html'}
        response = httpResponse(401, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'non_rfc_auth')), 1 )
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'userPassUri')), 0 )
    
    def test_http_auth_detect_simple(self):
        body = ''
        headers = {'content-type': 'text/html', 'www-authenticate': 'realm-w3af'}
        response = httpResponse(401, body , headers, self.url, self.url)
        self.plugin.grep(self.request, response)
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'auth')), 1 )
        self.assertEqual( len(kb.kb.get('http_auth_detect', 'userPassUri')), 0 )