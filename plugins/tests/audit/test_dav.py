'''
test_dav.py

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

from ..helper import PluginTest, PluginConfig


class TestDav(PluginTest):
    
    target_vuln_all = 'http://moth/w3af/audit/dav/write-all/'
    target_no_privs = 'http://moth/w3af/audit/dav/no-privileges/'
    target_safe_all = 'http://moth/w3af/audit/eval/'
    
    _run_configs = {
        'cfg': {
            'target': None,
            'plugins': {
                 'audit': (PluginConfig('dav',),),                 
                 }
            },
        }
    
    def test_found_all_dav(self):
        cfg = self._run_configs['cfg']
        self._scan( self.target_vuln_all, cfg['plugins'])
        
        vulns = self.kb.get('dav', 'dav')
        
        EXPECTED_NAMES = set(['Insecure DAV configuration'] * 2)
        
        self.assertEquals( EXPECTED_NAMES,
                           set([v.getName() for v in vulns])
                          )
        
        self.assertEquals( set(['PUT', 'PROPFIND']),
                           set([v.get_method() for v in vulns]))
        
        self.assertTrue( all([self.target_vuln_all == str(v.getURL().getDomainPath()) for v in vulns]))
    
    def test_no_privileges(self):
        '''
        DAV is configured but the directory doesn't have the file-system permissions
        to allow the Apache process to write to it.
        '''
        cfg = self._run_configs['cfg']
        self._scan( self.target_no_privs, cfg['plugins'])
        
        vulns = self.kb.get('dav', 'dav')
        
        self.assertTrue( len(vulns), 1)
        
        vuln = vulns[0]
        
        self.assertEquals( 'DAV insufficient privileges',
                           vuln.getName() )
        
        self.assertEquals( self.target_no_privs, 
                           str(vuln.getURL().getDomainPath() ) )
        
    
    def test_not_found_dav(self):
        cfg = self._run_configs['cfg']
        self._scan( self.target_safe_all, cfg['plugins'])
        
        vulns = self.kb.get('dav', 'dav')
        self.assertEquals(0, len(vulns))
        