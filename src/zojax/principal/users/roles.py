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
from zope import interface
from zope.component import getUtility
from zope.security.interfaces import IMemberGetterGroup
from zope.app.security.interfaces import IAuthentication
from zope.app.security.settings import Allow, Unset
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.app.authentication.interfaces import IFoundPrincipalFactory

from zojax.security.interfaces import IPrincipalGroups


class LocalPrincipalRoleMap(object):
    interface.implements(IPrincipalRoleMap)

    def __init__(self, context):
        folder = context.__parent__

        pinfo = folder.principalInfo(folder.prefix + context.__name__)
        self.principal = IFoundPrincipalFactory(pinfo)(getUtility(IAuthentication))
        self.groups = IPrincipalGroups(self.principal)

    def getPrincipalsForRole(self, role_id):
        if role_id == 'content.Owner':
            return (self.principal.id, Allow),
        return ()

    def getRolesForPrincipal(self, principal_id):
        if principal_id == self.principal.id:
            return ('content.Owner', Allow),

        for group in self.groups.getGroups():
            if principal_id in getattr(group, 'leaders', ()):
                return (('team.Leader', Allow),
                        ('team.Member', Allow))
            elif IMemberGetterGroup.providedBy(group) and principal_id in group.getMembers():
                return (('team.Member', Allow),)

        return ()

    def getSetting(self, role_id, principal_id):
        return Unset

    def getPrincipalsAndRoles(self):
        pass
