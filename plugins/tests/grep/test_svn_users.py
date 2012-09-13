'''
test_svn_users.py

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
import core.data.constants.severity as severity


class TestSVNUsers(PluginTest):
    
    svn_users_url = 'http://moth/w3af/grep/svn_users/'
    
    _run_configs = {
        'cfg1': {
            'target': svn_users_url,
            'plugins': {
                'grep': (PluginConfig('svn_users'),),
                'crawl': (
                    PluginConfig('web_spider',
                                 ('onlyForward', True, PluginConfig.BOOL)),
                )         
                
            }
        }
    }
    
    def test_found_vuln(self):
        cfg = self._run_configs['cfg1']
        self._scan(cfg['target'], cfg['plugins'])
        vulns = self.kb.get('svn_users', 'users')
        
        self.assertEquals(1, len(vulns))
        
        v = vulns[0]
        self.assertEquals(severity.LOW, v.getSeverity())
        self.assertEquals('SVN user disclosure vulnerability', v.getName() )
        self.assertEqual(self.svn_users_url + 'svn_user.html', v.getURL().url_string)
        
        