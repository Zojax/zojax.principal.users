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
""" principal registration

$Id$
"""
from zope import interface, event
from zope.component import getUtility, queryUtility, getSiteManager
from zope.component.interfaces import IComponentLookup
from zope.lifecycleevent import ObjectCreatedEvent
from zope.cachedescriptors.property import Lazy
from zope.app.security.interfaces import IAuthentication
from zope.app.container.interfaces import INameChooser
from zope.app.component.hooks import getSite
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication

from zojax.layoutform import button, Fields, PageletForm
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.authentication.utils import updateCredentials
from zojax.authentication.interfaces import IPluggableAuthentication

from zojax.principal.registration.interfaces import STATUS_CONTINUE
from zojax.principal.registration.interfaces import IPortalRegistration
from zojax.principal.registration.interfaces import IMemberRegisterAction
from zojax.principal.registration.interfaces import IMemberRegistrationForm
from zojax.principal.registration.interfaces import IMemberRegistrationAction
from zojax.principal.registration.interfaces import IMailAuthorizationAware

from zojax.principal.password.interfaces import IPasswordTool
from zojax.principal.password.browser.interfaces import IPrincipalPasswordForm

from zojax.principal.users.principal import Principal
from zojax.principal.users.interfaces import _, IUsersPlugin

from interfaces import IRegistrationForm


class MemberRegistration(PageletForm):
    """ adding new principal """
    interface.implements(IPrincipalPasswordForm, IMemberRegistrationForm)

    label = _("Registration form")

    ignoreContext = True
    fields = Fields(IRegistrationForm, IPrincipalPasswordForm)

    registeredPrincipal = None

    def update(self):
        self.registration = getUtility(IPortalRegistration)

        super(MemberRegistration, self).update()

    @button.buttonAndHandler(_(u"Register"), provides=IMemberRegisterAction)
    def handle_register(self, action):
        request = self.request

        data, errors = self.extractData()
        if errors:
            IStatusMessage(request).add(self.formErrorsMessage, 'error')
            return

        plugin = queryUtility(IUsersPlugin)

        login = data['login'].lower()

        # create principal
        principal = Principal(login, data['firstname'], data['lastname'], '')

        # set password
        passwordtool = getUtility(IPasswordTool)
        principal.password = passwordtool.encodePassword(data['password'])

        event.notify(ObjectCreatedEvent(principal))

        # save principal to folder
        name = INameChooser(plugin).chooseName('', principal)

        plugin[name] = principal

        # register principal in registration tool
        auth = getUtility(IAuthentication)
        principal = auth.getPrincipal(auth.prefix + plugin.prefix + name)
        interface.alsoProvides(principal, IMailAuthorizationAware)

        status = self.registration.registerPrincipal(principal, request)
        if status == STATUS_CONTINUE:
            updateCredentials(request, login, data['password'])

            IStatusMessage(request).add(
                _('You have been successfully registered. '))
            self.redirect(absoluteURL(getSite(), request))

        # IMemberRegistrationForm attribute
        self.registeredPrincipal = principal


class RegisterAction(object):
    interface.implements(IMemberRegistrationAction)

    name = 'zojax-principalusers'

    title = _(u'Standard registration')

    def isAvailable(self):
        auth = getUtility(IAuthentication)
        plugin = queryUtility(IUsersPlugin)
        if plugin is None:
            return False
        else:
            sm = getSiteManager()

            if IComponentLookup(auth) is sm:
                if IComponentLookup(plugin) is sm:
                    return True
            else:
                return True

        return False
