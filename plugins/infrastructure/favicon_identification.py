'''
favicon_identification.py

Copyright 2009 Vlatko Kosturjak
Plugin based on wordpress_fingerprint.py and pykto.py

More information to be found here:
    http://www.owasp.org/index.php/Category:OWASP_Favicon_Database_Project
    http://kost.com.hr/favicon.php

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
import re
import hashlib
import os.path

import core.controllers.outputManager as om
import core.data.kb.knowledgeBase as kb
import core.data.kb.info as info

from core.controllers.plugins.infrastructure_plugin import InfrastructurePlugin
from core.controllers.misc.decorators import runonce
from core.controllers.core_helpers.fingerprint_404 import is_404
from core.controllers.w3afException import w3afException, w3afRunOnce


class favicon_identification(InfrastructurePlugin):
    '''
    Identify server software using favicon.
    @author: Vlatko Kosturjak  <kost@linux.hr> http://kost.com.hr
    '''

    def __init__(self):
        InfrastructurePlugin.__init__(self)
        
        # Internal variables
        self._version = None

        # User configured parameters
        self._db_file = os.path.join('plugins', 'infrastructure', 'favicon', 
                                     'favicon-md5')

    @runonce(exc_class=w3afRunOnce)
    def discover(self, fuzzable_request ):
        '''
        Identify server software using favicon.   
        
        @param fuzzable_request: A fuzzable_request instance that contains 
                                (among other things) the URL to test.
        '''
        domain_path = fuzzable_request.getURL().getDomainPath()
        
        # TODO: Maybe I should also parse the html to extract the favicon location?
        favicon_url = domain_path.urlJoin('favicon.ico' )
        response = self._uri_opener.GET( favicon_url, cache=True )
        remote_fav_md5 = hashlib.md5(response.getBody()).hexdigest()

        if not is_404(response):
        
            # check if MD5 is matched in database/list
            for md5part, favicon_desc in self._read_favicon_db():
                
                if md5part == remote_fav_md5:
                    # Save it to the kb!
                    i = info.info()
                    i.setPluginName(self.getName())
                    i.setName('Favicon identification')
                    i.setURL( favicon_url )
                    i.set_id( response.id )
                    desc = 'Favicon.ico file was identified as "%s".' % favicon_desc
                    i.setDesc( desc )
                    kb.kb.append( self, 'info', i )
                    om.out.information( i.getDesc() )
                    break
            else:
                #
                #   Report to the kb that we failed to ID this favicon.ico 
                #   and that the md5 should be sent to the developers.
                #
                i = info.info()
                i.setPluginName(self.getName())
                i.setName('Favicon identification failed')
                i.setURL( favicon_url )
                i.set_id( response.id )
                desc = 'Favicon identification failed. If the remote site is using'
                desc += ' framework that is being exposed by its favicon, please send'
                desc += ' an email to w3af-develop@lists.sourceforge.net including'
                desc += ' this md5 hash "'+remote_fav_md5+'"'
                desc += ' and what server or Web application it represents. New fingerprints'
                desc += ' make this plugin more powerful and accurate.'
                i.setDesc( desc )
                kb.kb.append( self, 'info', i )
                om.out.information( i.getDesc() )
    
    def _read_favicon_db(self):
        try:
            # read MD5 database.
            db_file = open(self._db_file, "r")
        except Exception, e:
            raise w3afException('Failed to open the MD5 database. Exception: "' + str(e) + '".')
        else:
            for line in db_file:
                line = line.strip()
                md5part, favicon_desc = line.split( ":", 1 )
                yield md5part, favicon_desc
    
    def get_long_desc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin identifies software version using favicon.ico file.

        It checks MD5 of favicon against the MD5 database of favicons. See also: 
            http://www.owasp.org/index.php/Category:OWASP_Favicon_Database_Project
            http://kost.com.hr/favicon.php
        '''