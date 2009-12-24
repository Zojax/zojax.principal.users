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
from zope import component, event, interface
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.lifecycleevent import ObjectCreatedEvent
from zope.session.interfaces import ISession
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import \
    IAuthentication, IUnauthenticatedPrincipal
from zope.app.container.interfaces import INameChooser

from openid.consumer.consumer import Consumer

from zojax.layoutform import button, Fields, PageletForm

from zojax.authentication.utils import updateCredentials
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.authentication.interfaces import ILoginService
from zojax.principal.password.interfaces import IPasswordTool
from zojax.principal.password.browser.interfaces import IPrincipalPasswordForm

from zojax.principal.registration.interfaces import STATUS_CONTINUE
from zojax.principal.registration.interfaces import IPortalRegistration
from zojax.principal.registration.interfaces import IMemberRegisterAction
from zojax.principal.registration.interfaces import IMemberRegistrationForm
from zojax.principal.registration.interfaces import IMemberRegistrationAction
from zojax.principal.registration.interfaces import IMailAuthorizationAware

from zojax.principal.users.interfaces import \
    _, IPrincipal, IUsersPlugin, IOpenIdCredentialsPlugin
from zojax.principal.users.plugin import \
    SESSION_KEY, getReturnToURL, normalizeIdentifier
from zojax.principal.users.principal import Principal

from interfaces import IRegistrationForm


class OpenIdSignIn(object):

    def __call__(self, *args, **kw):
        request = self.request
        context = self.context
        siteURL = u'%s/'%absoluteURL(context, request)

        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            self.redirect(siteURL)
            return u''

        if not 'openid_form_submitted' in request:
            self.redirect(siteURL)
            return u''

        identifier = request.get('openid_identifier')
        if not identifier or identifier == 'http://':
            IStatusMessage(request).add(
                _(u"Please specify your OpenID identifier."))
            self.redirect(u'%slogin.html'%siteURL)
            return u''

        authenticator = getUtility(IUsersPlugin)
        session = ISession(request)[SESSION_KEY]
        consumer = Consumer(session, authenticator.store)

        try:
            authRequest = consumer.begin(identifier)
            redirectURL = authRequest.redirectURL(
                siteURL, getReturnToURL(request))
        except Exception, err:
            IStatusMessage(request).add(err, 'error')
            self.redirect(u'%slogin.html'%siteURL)
            return u''

        self.redirect(redirectURL)
        return u''


class CompleteOpenIdSignIn(PageletForm):
    interface.implements(IPrincipalPasswordForm, IMailAuthorizationAware)

    label = _("Register new user")

    ignoreContext = True
    fields = Fields(IRegistrationForm, IPrincipalPasswordForm)

    registeredPrincipal = None

    def update(self):
        self.registration = getUtility(IPortalRegistration)

        super(CompleteOpenIdSignIn, self).update()

        request = self.request

        self.portalURL = u'%s/'%absoluteURL(self.context, request)
        self.loginURL = u'%s@@completeOpenIdSignIn'%self.portalURL

        if 'form.zojax-auth-login' in request:
            principal = request.principal
            if IUnauthenticatedPrincipal.providedBy(principal):
                IStatusMessage(request).add(_('Login failed.'), 'warning')
            else:
                principal = IPrincipal(principal)
                principal.identifiers = \
                    principal.identifiers + (self.data['identifier'],)

                del self.data['reqregister']
                del self.data['identifier']

                IStatusMessage(request).add(_('You successfully logged in.'))
                self.redirect('./')

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
        authprincipal = auth.getPrincipal(auth.prefix + plugin.prefix + name)

        status = self.registration.registerPrincipal(authprincipal, request)
        if status == STATUS_CONTINUE:
            updateCredentials(request, login, data['password'])

            principal.identifiers = \
                principal.identifiers + (self.data['identifier'],)

            del self.data['reqregister']
            del self.data['identifier']

            IStatusMessage(request).add(
                _('You have been successfully registered.'))
            self.redirect(absoluteURL(getSite(), request))

        # IMemberRegistrationForm attribute
        self.registeredPrincipal = authprincipal

    def __call__(self, *args, **kw):
        self.data = ISession(self.request)[SESSION_KEY]

        if not self.data.get('reqregister', False):
            self.redirect(
                u'%s/successOpenIdSignIn?processed=1'%absoluteURL(
                    self.context, self.request))
            return u''

        return super(CompleteOpenIdSignIn, self).__call__(*args, **kw)


class SuccessOpenIdSignIn(object):

    def __call__(self, *args, **kw):
        context = self.context
        request = self.request
        principal = request.principal
        auth = getUtility(IAuthentication)

        if IUnauthenticatedPrincipal.providedBy(principal):
            msg = auth.loginMessage
            if not msg:
                msg = _('Login failed.')

            IStatusMessage(request).add(msg, 'warning')

            self.redirect(u'%s/login.html'%absoluteURL(context, request))
        elif 'processed' in request:
            if getMultiAdapter((auth, request), ILoginService).success():
                return u''

        self.redirect(u'%s/'%absoluteURL(getSite(), request))
        return u''
