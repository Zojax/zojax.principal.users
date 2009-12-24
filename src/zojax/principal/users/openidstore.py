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
import time
from zc.blist import BList
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OITreeSet

from openid.association import Association
from openid.store.nonce import SKEW
from openid.store.interface import OpenIDStore


class ZopeStore(OpenIDStore):
    """Zope OpenID store.

    This class implements an OpenID store which uses the ZODB."""
    def __init__(self):
        self.handles = OOBTree()
        self.nonces = OITreeSet()
        self.associations = OOBTree()

        self.noncetimeline = BList()
        self.assoctimeline = BList()

    def getAssociationKey(self, server_url, handle):
        """Generate a key used to identify an association in our storage."""
        if handle is None:
            return self.handles[server_url][0]

        return (server_url, handle)

    def storeAssociation(self, server_url, association):
        key = self.getAssociationKey(server_url, association.handle)
        self.associations[key] = association.serialize()

        now = time.time()
        def getKey(item):
            return self.getAssociation(
                item[0], item[1], remove=False).getExpiresIn(now)

        lst = self.handles.get(server_url, [])
        lst.append(key)
        lst.sort(key=getKey)
        self.handles[server_url] = lst

        self.assoctimeline.append(
            (association.issued + association.lifetime, key))

    def getAssociation(self, server_url, handle=None, remove=True):
        try:
            key=self.getAssociationKey(server_url, handle)
            assoc=Association.deserialize(self.associations[key])
        except KeyError:
            return None

        if remove and assoc.getExpiresIn()==0:
            self.removeAssociation(server_url, handle)
            return None

        return assoc

    def removeAssociation(self, server_url, handle):
        key = self.getAssociationKey(server_url, handle)
        try:
            assoc = Association.deserialize(self.associations[key])
            del self.associations[key]

            lst = self.handles[server_url]
            lst.remove(key)
            self.handles[server_url]=lst

            self.assoctimeline.remove((assoc.issued + assoc.lifetime, key))
            return True
        except KeyError:
            return False

    def useNonce(self, server_url, timestamp, salt):
        nonce = (salt, server_url)
        if nonce in self.nonces:
            return False

        self.nonces.insert(nonce)
        self.noncetimeline.append((timestamp, nonce))

        return True

    def cleanupNonces(self):
        cutoff = time.time()+SKEW
        count = 0
        for (timestamp, nonce) in self.noncetimeline:
            if timestamp < cutoff:
                self.noncetimeline.remove((timestamp, nonce))
                self.nonces.remove(nonce)
                count += 1

        return count

    def cleanupAssociations(self):
        now = time.time()
        count = 0

        expired=(key for (timestamp, key) in self.assoctimeline
                if timestamp<=now)
        for key in expired:
            self.removeAssociation(*key)
            count+=1

        return count
