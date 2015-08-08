# -*- test-case-name: mimic.test.test_glance -*-
"""
Defines a list of images from glance
"""

import json
from uuid import uuid4
from six import text_type
from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.python.urlpath import URLPath

from mimic.canned_responses.glance import get_images
from mimic.rest.mimicapp import MimicApp
from mimic.catalog import Entry
from mimic.catalog import Endpoint
from mimic.imimic import IAPIMock


@implementer(IAPIMock, IPlugin)
class GlanceApi(object):
    """
    Rest endpoints for mocked Glance Api.
    """
    def __init__(self, regions=["ORD", "DFW", "IAD"]):
        """
        Create a GlanceApi.
        """
        self._regions = regions

    def catalog_entries(self, tenant_id):
        """
        List catalog entries for the Glance API.
        """
        return [
            Entry(
                tenant_id, "image", "cloudImages",
                [
                    Endpoint(tenant_id, region, text_type(uuid4()), prefix="v2")
                    for region in self._regions
                ]
            )
        ]

    def resource_for_region(self, region, uri_prefix, session_store):
        """
        Get an :obj:`twisted.web.iweb.IResource` for the given URI prefix;
        implement :obj:`IAPIMock`.
        """
        return GlanceMock(self, uri_prefix, session_store, region).app.resource()


class GlanceMock(object):
    """
    Glance Mock
    """
    def __init__(self, api_mock, uri_prefix, session_store, name):
        """
        Create a glance region with a given URI prefix.
        """
        self.uri_prefix = uri_prefix
        self._api_mock = api_mock
        self._session_store = session_store
        self._name = name

    def url(self, suffix):
        """
        Generate a URL to an object within the Glance URL hierarchy, given the
        part of the URL that comes after.
        """
        return str(URLPath.fromString(self.uri_prefix).child(suffix))

    def _region_collection_for_tenant(self, tenant_id):
        """
        Get the given server-cache object for the given tenant, creating one if
        there isn't one.
        """
        return (self._api_mock._get_session(self._session_store, tenant_id)
                .collection_for_region(self._name))

    app = MimicApp()

    @app.route('/v2/<string:tenant_id>/images', methods=['GET'])
    def get_images(self, request, tenant_id):
        """
        Returns a list of glance images. Currently there is no provision
        for shared versus unshared images in the response
        """
        return json.dumps(get_images())
