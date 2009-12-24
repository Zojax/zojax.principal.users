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
from zope import interface, component
from zope.component import getUtility, queryUtility
from zope.security import checkPermission
from zope.security.interfaces import IGroup
from zope.location.location import Location
from zope.app.security.interfaces import IAuthentication
from zope.app.container.interfaces import INameChooser

from zojax.controlpanel.interfaces import IPrincipalsManagement
from zojax.principal.users.interfaces import _, IUsersPlugin, IPrincipalFactory


@component.adapter(IPrincipalsManagement, interface.Interface)
def getPrincipalFactory(context, request):
    plugin = queryUtility(IUsersPlugin)
    if plugin is not None and \
           checkPermission('zojax.principal.AddUser', plugin):
        return PrincipalFactory(context, request, plugin)


class PrincipalFactory(Location):
    interface.implements(IPrincipalFactory)

    title = _('Member')
    description = _('Create new member.')
    name = __name__ = u'+principal.user'

    def __init__(self, context, request, plugin):
        self.context = plugin
        self.request = request
        self.__parent__ = context

    def add(self, principal, group=''):
        context = self.context

        chooser = INameChooser(context)
        name = chooser.chooseName('', principal)
        chooser.checkName(name, principal)
        context[name] = principal

        auth = getUtility(IAuthentication)
        grp = None
        try:
            grp = auth.getPrincipal(group)
        except:
            pass

        principal = auth.getPrincipal(
            auth.prefix + context.prefix + principal.__name__)
        if grp is not None:
            grp.setMembers((principal.id,) + grp.getMembers())

        return principal
