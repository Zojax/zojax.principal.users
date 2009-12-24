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
from zope import component, interface
from zope.component import getUtility, getUtilitiesFor
from zope.security import checkPermission
from zope.security.proxy import removeSecurityProxy
from zope.security.interfaces import IPrincipal
from zope.app.security.interfaces import IAuthentication

from zojax.mail.interfaces import IMailAddress, IPrincipalByEMail

from zojax.authentication.interfaces import IPrincipalLogin
from zojax.authentication.interfaces import IPrincipalByLogin
from zojax.principal.password.interfaces import IPasswordTool
from zojax.principal.password.interfaces import IPasswordChanger

from interfaces import IPrincipal, IUsersPlugin, IPrincipalMarker


class PrincipalByEMail(object):
    interface.implements(IPrincipalByEMail)

    def getPrincipal(self, email):
        for name, plugin in getUtilitiesFor(IUsersPlugin):
            id = plugin.getPrincipalByLogin(email)
            if id is not None:
                auth = getUtility(IAuthentication)
                return auth.getPrincipal(auth.prefix + plugin.prefix + id)


class PrincipalByLogin(object):
    interface.implements(IPrincipalByLogin)

    def getPrincipalByLogin(self, login):
        auth = getUtility(IAuthentication)

        for name, plugin in getUtilitiesFor(IUsersPlugin):
            plugin = removeSecurityProxy(plugin)
            name = plugin.getPrincipalByLogin(login)
            if name is not None:
                return auth.getPrincipal(
                    removeSecurityProxy(auth).prefix + plugin.prefix + name)


class PrincipalLogin(object):
    component.adapts(IPrincipalMarker)
    interface.implements(IPrincipalLogin)

    def __init__(self, principal):
        self.login = principal.login


class PrincipalMailAddress(object):
    component.adapts(IPrincipalMarker)
    interface.implements(IMailAddress)

    def __init__(self, principal):
        self.address = removeSecurityProxy(IPrincipal(principal)).login


class PasswordChanger(object):
    component.adapts(IPrincipalMarker)
    interface.implements(IPasswordChanger)

    def __init__(self, principal):
        self.internal = removeSecurityProxy(IPrincipal(principal))

    def checkPassword(self, password):
        ptool = getUtility(IPasswordTool)
        return ptool.checkPassword(self.internal.password, password)

    def changePassword(self, password):
        self.internal.password = password
