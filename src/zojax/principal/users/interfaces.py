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
""" ZODB-based Authentication Source
With email as principal primary login, any number of additional logins

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory
from zope.app.authentication.interfaces import IPrincipalInfo
from z3c.schema.email import RFC822MailAddress

from zojax.content.type.interfaces import IItem
from zojax.authentication.interfaces import ICredentialsPlugin

_ = MessageFactory('zojax.principal.users')


class IPrincipal(interface.Interface):
    """ Internal principal """

    firstname = schema.TextLine(
        title=_('First Name'),
        description=_(u"e.g. John. This is how users "
                      u"on the site will identify you."),
        required = True)

    lastname = schema.TextLine(
        title=_('Last Name'),
        description=_(u"e.g. Smith. This is how users "
                      u"on the site will identify you."),
        required = True)

    login = RFC822MailAddress(
        title=_("Email/Login name"),
        description=_("Enter new email. It will be used as login "
                      "name and address for email notifications."))

    password = schema.Password(
        title=_("Password"),
        description=_("The password for the user."))

    description = schema.Text(
        title=_("Description"),
        description=_("Provides a description for the principal."),
        required=False,
        missing_value='',
        default=u'')

    logins = interface.Attribute('Logins')


class IPrincipalWithLogins(IPrincipal):
    """ principla with multple logins """

    logins = schema.Tuple(
        title=_('Secondary logins'),
        description=_("Enter new email. It will be used as login name also."),
        required=False)


class IUsersPlugin(interface.Interface):
    """A container that contains internal principals."""

    title = schema.TextLine(
        title = _('Title'),
        required = False)

    prefix = schema.TextLine(
        title=_("Prefix"),
        description=_("Prefix to be added to all principal ids to assure "
                      "that all ids are unique within the authentication service"),
        missing_value=u"",
        default=u'',
        readonly=True)

    store = interface.Attribute('OpenId store')

    def getPrincipalByLogin(login):
        """ return principal info by login """

    def getPrincipalByOpenIdIdentifier(identifier):
        """ return principal info by OpenID Identifier """


class IPrincipalMarker(interface.Interface):
    """ marker interface for Principal """


class IPrincipalInfo(IPrincipalInfo):
    """ """

    internalId = interface.Attribute('Internal id')


class IPrincipalFactory(interface.Interface):
    """ principal factory """

    def add(principal, group=''):
        """ add principal to plugin """


# OpenId support

class IOpenIdCredentials(interface.Interface):
    """ open id credentials info """

    request = interface.Attribute(u"request")

    failed = interface.Attribute(u'Credentials failed')

    principalInfo = interface.Attribute('Principal info')

    parameters = schema.Dict(title=_(u"Query parameters"))


class IOpenIdCredentialsPlugin(ICredentialsPlugin):
    """ open id credentials plugin """
