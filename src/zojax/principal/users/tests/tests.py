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
import os
import unittest, doctest
from zope import interface, component
from zope.app.testing import setup
from zope.app.testing.functional import ZCMLLayer
from zope.app.rotterdam import Rotterdam
from zope.app.component.site import SiteManagerAdapter
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import FoundPrincipalFactory

from zojax.content.type.testing import setUpContents
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.authentication.tests.install import installAuthentication
from zojax.principal.password.passwordtool import PasswordTool
from zojax.principal.users import foundsubscriber, adapters


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


zojaxPrincipalUsers = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxPrincipalUsers', allow_teardown=True)


def setUp(test):
    site = setup.placefulSetUp(True)
    site.__name__ = u'portal'
    setup.setUpTestAsModule(test, name='zojax.principal.users.TESTS')

    setUpContents()

    pau = PluggableAuthentication('xyz_')
    component.provideUtility(pau, IAuthentication)
    component.provideAdapter(SiteManagerAdapter)
    component.provideAdapter(FoundPrincipalFactory)

    component.provideAdapter(foundsubscriber.getInternalPrincipal)
    component.provideHandler(foundsubscriber.foundPrincipalCreated)

    component.provideAdapter(adapters.PrincipalLogin)
    component.provideAdapter(adapters.PasswordChanger)
    component.provideAdapter(adapters.PrincipalMailAddress)

    component.provideUtility(adapters.PrincipalByLogin(),
                             name='zojax.principal.users.principals')
    component.provideUtility(adapters.PrincipalByEMail(),
                             name='zojax.principal.users.principals')

    ptool = PasswordTool()
    ptool.passwordManager = 'MD5'
    component.provideUtility(ptool)


def tearDown(test):
    setup.placefulTearDown()
    setup.tearDownTestAsModule(test)


def test_suite():
    configlet = doctest.DocFileSuite(
        "testbrowser.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    configlet.layer = zojaxPrincipalUsers

    openid = doctest.DocFileSuite(
        "openid.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    openid.layer = zojaxPrincipalUsers

    return unittest.TestSuite((
            openid, configlet,
            doctest.DocFileSuite(
                'base.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'plugin.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'zojax.principal.users.namechooser',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
