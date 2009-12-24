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
from zope import schema, interface
from zojax.principal.registration.fields import NewEMailLoginField

from zojax.principal.users.interfaces import _


class IRegistrationForm(interface.Interface):

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

    login = NewEMailLoginField(
        title = _(u'E-mail/Login'),
        description = _(u'This is the username you will use to log in. '\
            'It must be an email address. <br /> Your email address will not '\
            'be displayed to any user or be shared with anyone else.'),
        required = True)
