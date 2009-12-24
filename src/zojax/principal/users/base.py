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
from zope.location import Location
from zope.component import getUtility
from zope.app.authentication.interfaces import IPasswordManager
from zojax.content.type.item import Item

from interfaces import _, IPrincipal


class Principal(Item):
    """An internal principal."""

    firstname = u''
    lastname = u''

    def __init__(self, login, firstname, lastname,
                 password='', logins=(), description=u''):
        self._login = login
        self._logins = tuple(logins)

        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.description = description

    @property
    def title(self):
        return (u'%s %s'%(self.firstname, self.lastname)).strip()

    def getLogin(self):
        return self._login

    def setLogin(self, login):
        oldLogin = self._login
        self._login = login

        if self.__parent__ is not None:
            try:
                self.__parent__.notifyLoginChanged(oldLogin, self)
            except ValueError:
                self._login = oldLogin
                raise

    login = property(getLogin, setLogin)

    def getLogins(self):
        return self._logins

    def setLogins(self, logins):
        oldLogins = self._logins
        self._logins = tuple(logins)

        if self.__parent__ is not None:
            try:
                self.__parent__.notifyLoginsChanged(oldLogins, self)
            except ValueError:
                self._logins = oldLogins
                raise

    logins = property(getLogins, setLogins)
