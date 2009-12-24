##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope.app.pagetemplate import ViewPageTemplateFile

from zojax.mail.service import getMailAddress
from zojax.authentication.utils import getPrincipals
from zojax.principal.users.interfaces import _, IPrincipalMarker


class InformationViewlet(object):

    template = ViewPageTemplateFile("userinfo.pt")

    def update(self):
        principal = self.context

        self.title = principal.title
        self.description = principal.description
        self.email = principal.login
        #self.logins = ', '.join(getattr(info, 'logins', ()))
