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
from zojax.principal.users import plugin
from zojax.principal.users.browser import openidsignin


class Consumer(object):

    def __init__(self, session, store):
        self.session = session
        self.store = store

    def begin(self, identifier):
        return AuthRequest(identifier)

    def complete(self, params, returnto):
        return Response(params['id'])


class AuthRequest(object):

    def __init__(self, identifier):
        self.identifier = identifier

    def redirectURL(self, siteURL, url):
        if self.identifier == 'https://google.com/1/':
            url = '%s?openid.mode=id_res&openid.return_to='%url

        if self.identifier == 'https://google.com/2/':
            url = '%s?openid.mode=id_res&openid.return_to='%url

        if self.identifier == 'https://google.com/3/':
            url = '%s?openid.mode=id_res&openid.return_to='%url

        if self.identifier == 'https://google.com/4/':
            url = '%s?openid.mode=cancel&openid.return_to='%url

        if self.identifier == 'https://google.com/5/':
            raise ValueError('Error during processing')

        return '%s&id=%s'%(url, self.identifier)


class Response(object):

    def __init__(self, returnto):
        self.identity_url = u'%s?identifier=1'%returnto


openidsignin.Consumer = Consumer

plugin.Consumer = Consumer
plugin.SuccessResponse = Response
