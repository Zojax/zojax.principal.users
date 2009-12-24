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
from rwproperty import getproperty, setproperty

from zope import interface, component
from zojax.principal.profile.interfaces import IPrincipalInformation

from interfaces import IPrincipal, IPrincipalMarker


class PrincipalInformation(object):
    component.adapts(IPrincipalMarker)
    interface.implements(IPrincipalInformation)

    readonly = False

    def __init__(self, principal):
        self.principal = IPrincipal(principal)

    @property
    def title(self):
        return self.principal.title

    @getproperty
    def firstname(self):
        return self.principal.firstname

    @getproperty
    def lastname(self):
        return self.principal.lastname

    @getproperty
    def email(self):
        return self.principal.login

    @setproperty
    def firstname(self, value):
        self.principal.firstname = value

    @setproperty
    def lastname(self, value):
        self.principal.lastname = value

    @setproperty
    def email(self, value):
        self.principal.login = value
