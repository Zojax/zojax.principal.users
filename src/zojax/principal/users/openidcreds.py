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
from persistent import Persistent

from zope import interface
from zope.component import getUtility, queryUtility
from zope.schema.fieldproperty import FieldProperty
from zope.security.management import queryInteraction
from zope.app.container.contained import Contained
from zojax.authentication.factory import CredentialsPluginFactory

from interfaces import _, \
    IUsersPlugin, IOpenIdCredentials, IOpenIdCredentialsPlugin


class OpenIdCredentials(object):
    interface.implements(IOpenIdCredentials)

    failed = False
    principalInfo = None
    identifier = None
    reqregister = False
    parameters = FieldProperty(IOpenIdCredentials['parameters'])

    def __init__(self, parameters):
        self.parameters = parameters

    @property
    def request(self):
        interaction = queryInteraction()

        if interaction is not None:
            for participation in interaction.participations:
                return participation


class OpenIdCredentialsPlugin(Persistent, Contained):
    interface.implements(IOpenIdCredentialsPlugin)

    def extractCredentials(self, request):
        """Tries to extract credentials from a request.

        A return value of None indicates that no credentials could be found.
        Any other return value is treated as valid credentials.
        """
        mode = request.get("openid.mode", None)

        if mode == "id_res":
            # id_res means 'positive assertion' in OpenID, more commonly
            # described as 'positive authentication'
            parameters = {}
            for field, value in request.form.iteritems():
                parameters[field] = value
            return OpenIdCredentials(parameters)

        elif mode == "cancel":
            # cancel is a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            return None

        return None


class OpenIdCredentialsPluginFactory(CredentialsPluginFactory):

    def isAvailable(self):
        return queryUtility(IUsersPlugin) is not None


factory = OpenIdCredentialsPluginFactory(
    "principal.users.credentials.openid",
    OpenIdCredentialsPlugin, ((IOpenIdCredentialsPlugin, ''),),
    _(u'OpenId credentials plugin'),
    _('This plugin allow use openid login like google, yahoo, lifejournal and many others with standard users authenticator plugin.'))
