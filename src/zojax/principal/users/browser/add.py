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
""" Authentication plugin implementation

$Id$
"""
from zope import schema, interface
from zope.component import getUtility

from zojax.layoutform import Fields, PageletAddForm
from zojax.principal.password.interfaces import IPasswordTool
from zojax.principal.registration.interfaces import IPortalRegistration

from zojax.principal.users.interfaces import _
from zojax.principal.users.principal import Principal
from zojax.principal.users.browser.interfaces import IRegistrationForm


class INewPrincipalForm(interface.Interface):

    password = schema.TextLine(
        title = _(u'Password'),
        description = _(u'Enter new password. no spaces or special characters, should contain '
                        u'digits and letters in mixed case.'),
        required = True)

    description = schema.Text(
        title=_("Description"),
        description=_("Provides a description for the principal."),
        required=False,
        missing_value='',
        default=u'')


class NewPrincipal(PageletAddForm):
    """ adding new principal """

    label = _("Create new member")

    fields = Fields(IRegistrationForm, INewPrincipalForm)

    def create(self, data):
        principal = Principal(
            data['login'].lower(), data['firstname'], data['lastname'], '')
        principal.password = getUtility(
            IPasswordTool).encodePassword(data['password'])
        return principal

    def add(self, principal):
        self.principal = self.context.add(principal)

        # register principal in registration tool
        registration = getUtility(IPortalRegistration)
        registration.registerPrincipal(self.principal)

    def nextURL(self):
        return '../%s/'%self.principal.id

    def cancelURL(self):
        return '../'
