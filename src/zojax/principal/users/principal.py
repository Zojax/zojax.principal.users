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
"""Persistent principal

$Id$
"""
from rwproperty import getproperty, setproperty

import persistent
from zope import interface, component
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.app.security.interfaces import IAuthentication
from zope.app.container.interfaces import IObjectAddedEvent
from zope.cachedescriptors.property import Lazy
from zojax.content.type.searchable import ContentSearchableText

from base import Principal
from interfaces import IPrincipal


class Principal(Principal, persistent.Persistent):
    """ persistent principal """
    interface.implements(IPrincipal)

    @Lazy
    def id(self):
        self.id = '%s%s%s'%(
            getUtility(IAuthentication, context=self).prefix,
            self.__parent__.prefix, self.__name__)
        self._p_changed = True
        return self.id

    @Lazy
    def _identifiers(self):
        self._identifiers = ()
        self._p_changed = True
        return self._identifiers

    @getproperty
    def identifiers(self):
        return self._identifiers

    @setproperty
    def identifiers(self, identifiers):
        oldidentifiers = self.identifiers
        self._identifiers = tuple(identifiers)

        if self.__parent__ is not None:
            self.__parent__.notifyIdentifierChanged(oldidentifiers, self)


@component.adapter(IPrincipal, IObjectAddedEvent)
def principalAddedHandler(principal, ev):
    removeAllProxies(principal).id = '%s%s%s'%(
        getUtility(IAuthentication, context=principal).prefix,
        principal.__parent__.prefix, principal.__name__)


class PrincipalSearchableText(ContentSearchableText):
    component.adapts(IPrincipal)

    def getSearchableText(self):
        return self.content.firstname + u' ' + \
            self.content.lastname + u' ' + self.content.getLogin() + \
            u' ' + u' '.join(self.content.getLogins())
