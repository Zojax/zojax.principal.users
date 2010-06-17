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
from openid.consumer.consumer import Consumer, SuccessResponse

from zope import event, interface, component
from zope.component import getUtility
from zope.security import checkPermission
from zope.security.checker import ProxyFactory
from zope.security.proxy import removeSecurityProxy
from zope.session.interfaces import ISession
from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy
from zope.app.component.hooks import getSite
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import DuplicateIDError, IObjectRemovedEvent
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import IFoundPrincipalFactory

from zojax.content.type.container import ContentContainer
from zojax.principal.password.interfaces import IPasswordTool
from zojax.authentication.interfaces import ISimpleCredentials
from zojax.authentication.interfaces import PrincipalRemovingEvent
from zojax.authentication.interfaces import PrincipalInitializationFailed
from zojax.authentication.factory import AuthenticatorPluginFactory

from openidstore import ZopeStore
from interfaces import _, \
    IPrincipalInfo, IUsersPlugin, IPrincipalMarker, IOpenIdCredentials

SESSION_KEY = 'zojax.principal.users'


class PrincipalInfo(object):
    interface.implements(IPrincipalInfo)

    def __init__(self, id, internal):
        self.id = id
        self.login = internal.login
        self.title = internal.title
        self.description = internal.description
        self.internalId = internal.__name__

    def __repr__(self):
        return 'PrincipalInfo(%r)' % self.id


class UsersPlugin(ContentContainer):
    """A Persistent Principal Folder and Authentication plugin.

    See plugin.txt for details.
    """
    interface.implements(IUsersPlugin, IAuthenticatorPlugin)

    def __init__(self, title=_('Users'), description='', prefix='zojax.pf'):
        self.prefix = unicode(prefix)
        self.__id_by_login = self._newContainerData()

        super(UsersPlugin, self).__init__(
            title=title, description=description)

    @Lazy
    def store(self):
        self.store = ZopeStore()
        self._p_changed = True
        return self.store

    @Lazy
    def __id_by_identifier(self):
        self.__id_by_identifier = self._newContainerData()
        self._p_changed = True
        return self.__id_by_identifier

    def getPrincipalByLogin(self, login):
        if login in self.__id_by_login:
            return self.__id_by_login.get(login)

    def getPrincipalByOpenIdIdentifier(self, identifier):
        if identifier in self.__id_by_identifier:
            return self.__id_by_identifier.get(identifier)

    def notifyLoginChanged(self, oldLogin, principal):
        """Notify the Container about changed login of a principal.
        We need this, so that our second tree can be kept up-to-date.
        """
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError('Principal Login already taken!, '+principal.login)

        del self.__id_by_login[oldLogin]
        self.__id_by_login[principal.login] = principal.__name__

    def notifyIdentifierChanged(self, identifiers, principal):
        name = principal.__name__

        for identifier in identifiers:
            if identifier in self.__id_by_identifier:
                del self.__id_by_identifier[identifier]

        for identifier in principal.identifiers:
            self.__id_by_identifier[identifier] = name

    def notifyLoginsChanged(self, oldLogins, principal):
        """Notify the Container about changed secondary logins of a principal"""
        # A user with the new login already exists
        for login in principal.logins:
            if (login not in oldLogins) and (login in self.__id_by_login):
                raise ValueError('Principal Login already taken!, '+ login)

        for login in oldLogins:
            del self.__id_by_login[login]

        for login in principal.logins:
            self.__id_by_login[login] = principal.__name__

    def __setitem__(self, id, principal):
        # A user with the new login already exists
        for login in (principal.login,) + principal.logins:
            if login in self.__id_by_login:
                raise DuplicateIDError('Principal Login already taken!, '+login)

        super(UsersPlugin, self).__setitem__(id, principal)

        # add logins
        self.__id_by_login[principal.login] = id

        for login in principal.logins:
            self.__id_by_login[login] = id

        # add openid identifier
        for identifier in principal.identifiers:
            self.__id_by_identifier[identifier] = identifier

    def __delitem__(self, id):
        # notify about principal removing
        internal = self[id]

        auth = getUtility(IAuthentication)
        info = PrincipalInfo(self.prefix+id, internal)
        info.credentialsPlugin = None
        info.authenticatorPlugin = self
        principal = IFoundPrincipalFactory(info)(auth)
        principal.id = auth.prefix + self.prefix + id
        event.notify(PrincipalRemovingEvent(principal))

        # actual remove
        super(UsersPlugin, self).__delitem__(id)

        # remove logins
        del self.__id_by_login[internal.login]

        for login in internal.logins:
            del self.__id_by_login[login]

        # remove openid mapping
        for identifier in internal.identifiers:
            del self.__id_by_identifier[identifier]

    def authenticateCredentials(self, credentials):
        # simple login
        if ISimpleCredentials.providedBy(credentials):
            if credentials.principalinfo is not None and \
                    IPrincipalInfo.providedBy(credentials.principalinfo) and \
                    credentials.principalinfo.internalId in self:
                return credentials.principalinfo

            if not credentials.login:
                return None

            id = self.__id_by_login.get(credentials.login)
            if id is None:
                id = self.__id_by_login.get(credentials.login.lower())

            if id is None:
                return None
            internal = self[id]
            password = getattr(
                internal, 'password', getattr(internal, '_password', ''))
            ptool = getUtility(IPasswordTool)
            if not ptool.checkPassword(password, credentials.password):
                return None

            pinfo = PrincipalInfo(self.prefix + id, internal)
            credentials.principalinfo = pinfo

            return pinfo

        # openid login
        if IOpenIdCredentials.providedBy(credentials):
            if credentials.failed:
                return None

            if credentials.principalInfo is not None \
                    and credentials.principalInfo.internalId in self:
                return credentials.principalInfo

            request = credentials.request
            consumer = Consumer(ISession(request)[SESSION_KEY], self.store)

            returnto = credentials.parameters.get(
                'openid.return_to', getReturnToURL(request))

            response = consumer.complete(
                credentials.parameters, returnto.split('?')[0])

            if isinstance(response, SuccessResponse):
                identifier = normalizeIdentifier(response.identity_url)
                principalId = self.getPrincipalByOpenIdIdentifier(identifier)

                if principalId is None:
                    # Principal does not exist
                    data = ISession(request)[SESSION_KEY]
                    data['reqregister'] = True
                    data['identifier'] = identifier
                    credentials.failed = True
                    return None

                principalInfo = self.principalInfo(self.prefix + principalId)
                credentials.principalInfo = principalInfo
                return principalInfo

            else:
                raise PrincipalInitializationFailed(response.message)

    def principalInfo(self, id):
        if id.startswith(self.prefix):
            internal = self.get(id[len(self.prefix):])
            if internal is not None:
                return PrincipalInfo(id, internal)


@component.adapter(IUsersPlugin, IObjectRemovedEvent)
def pluginRemovedHandler(plugin, event):
    plugin = removeSecurityProxy(plugin)

    for id in tuple(plugin.keys()):
        del plugin[id]


def getReturnToURL(request):
    return absoluteURL(getSite(), request) + '/@@completeOpenIdSignIn'


def normalizeIdentifier(identifier):
    identifier = identifier.lower()

    if not identifier.startswith('http://') and \
            not identifier.startswith('https://'):
        identifier = 'http://' + identifier

    if not identifier.endswith('/'):
        identifier = identifier + '/'

    return unicode(identifier)


factory = AuthenticatorPluginFactory(
    'principal.users', UsersPlugin, ((IUsersPlugin, ''),),
    _('Standard users'), _('Protal users with main login as email.'))
