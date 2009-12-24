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
""" change login form

$Id$
"""
from zope import event, interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.schema.email import isValidMailAddress

from zojax.authentication.utils import updateCredentials
from zojax.authentication.utils import getPrincipalByLogin
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.layout.pagelet import BrowserPagelet
from zojax.principal.users.interfaces import _, IPrincipal


class ILoginPreference(interface.Interface):
    """ login preference """


class ChangeUserLogin(BrowserPagelet):
    """ change login form """

    template = ViewPageTemplateFile('login.pt')

    error_lastname = None
    error_firstname = None

    def __init_principal(self):
        principal = self.context.__principal__

        internal = IPrincipal(principal)

        self.id = principal.id
        self.principal = internal
        self.principal_first = internal.firstname
        self.principal_last = internal.lastname

        self.login = internal.login
        self.logins = internal.logins

        self.isManagement = self.request.principal.id != principal.id

    def update(self):
        self.__init_principal()
        context = self.context
        request = self.request
        response = request.response

        principal = self.principal

        service = IStatusMessage(request)

        if request.get('button.add', None):
            extra_login = request.get('extra_login', '').lower().strip()

            if not extra_login:
                self.error_extra_login = _(u'Login name is required.')
                return

            if extra_login != self.login and extra_login not in self.logins:
                p = getPrincipalByLogin(extra_login)
                if p is not None and p.id != self.id:
                    self.error_extra_login = _(u'Login name is already in use.')
                    return

                principal.logins = self.logins + (extra_login,)
                self.extra_login = ''
                event.notify(ObjectModifiedEvent(principal))

            service.add(_(u'New login has been added.'))
            self.__init_principal()

        if request.get('button.remove', None):
            removed = False
            logins = list(self.logins)
            for login in request.get('logins', ()):
                if login in logins:
                    removed = True
                    logins.remove(login)

            if not removed:
                return

            principal.logins = logins

            self.__init_principal()
            service.add(_(u'Changes has been saved.'))
            return response.redirect('./')

        if request.get('save.default', None):
            login = request.get('login', '').lower()

            if not isValidMailAddress(login):
                self.error_login = _(u'Not email.')
                return

            firstname = request.get('firstname', '').strip()
            if not firstname:
                self.error_firstname = _(u'First Name is required.')

            lastname = request.get('lastname', '').strip()
            if not lastname:
                self.error_lastname = _(u'Last Name is required.')

            if self.error_firstname or self.error_lastname:
                return

            if self.login != login:
                p = getPrincipalByLogin(login)
                if p is not None and p.id != self.id:
                    self.error_login = _(u'Login name is already in use.')
                    return

                principal.login = login

            principal.firstname = firstname
            principal.lastname = lastname

            if not self.isManagement:
                updateCredentials(request, login, request.get('password', ''))

            self.__init_principal()
            service.add(_(u'Changes has been saved.'))
            event.notify(ObjectModifiedEvent(principal))
