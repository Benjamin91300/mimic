"""
Dummy classes that can be shared across test cases
"""

from __future__ import absolute_import, division, unicode_literals

from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.web.resource import Resource

from mimic.catalog import Entry
from mimic.catalog import Endpoint
from mimic.imimic import IAPIMock, IAPIDomainMock, IExternalAPIMock


class ExampleResource(Resource):
    """
    Simple resource that returns a string as the response
    """
    isLeaf = True

    def __init__(self, response_message):
        """
        Has a response message to return when rendered
        """
        self.response_message = response_message

    def render_GET(self, request):
        """
        Render whatever message was passed in
        """
        return self.response_message


@implementer(IAPIMock, IPlugin)
class ExampleAPI(object):
    """
    Example API that returns NoResource
    """
    def __init__(self, response_message="default message", regions_and_versions=[('ORD', 'v1')]):
        """
        Has a dictionary to store information from calls, for testing
        purposes
        """
        self.store = {}
        self.regions_and_versions = regions_and_versions
        self.response_message = response_message

    def catalog_entries(self, tenant_id):
        """
        List catalog entries for the Nova API.
        """
        endpoints = [Endpoint(tenant_id, each[0], 'uuid', each[1]) for each in self.regions_and_versions]
        return [Entry(tenant_id, "serviceType", "serviceName", endpoints)]

    def resource_for_region(self, region, uri_prefix, session_store):
        """
        Return no resource.
        """
        self.store['uri_prefix'] = uri_prefix
        return ExampleResource(self.response_message)


@implementer(IAPIDomainMock, IPlugin)
class ExampleDomainAPI(object):
    """
    Example domain API the return nothing.
    """

    def __init__(self, domain=u"api.example.com", response=b'"test-value"'):
        """
        Create an :obj:`ExampleDomainAPI`.

        :param text_type domain: the domain to respond with
        :param bytes response: the HTTP response body for all contained
            resources
        """
        self._domain = domain
        self._response = response

    def domain(self):
        """
        The domain for the ExampleDomainAPI.
        """
        return self._domain

    def resource(self):
        """
        The resource for the ExampleDomainAPI.
        """
        example_resource = ExampleResource(self._response)
        return example_resource


@implementer(IExternalAPIMock, IPlugin)
class ExampleExternalAPI(object):
    """
    Example external API the return nothing
    """

    def __init__(self, name=u"example",
                 regions_and_versions=[
                     ('EXTERNAL', 'v1',
                      'https://api.external.example.com:8080')]):
        """
        Create an :obj:`ExampleExternalAPI`.

        :param text_type name: name of the external API
        """
        self.name_key = name
        self.regions_and_versions = regions_and_versions

    def catalog_entries(self, tenant_id):
        """
        List catalog entries for the Example API.
        """
        endpoints = [Endpoint(tenant_id, each[0], 'uuid', each[1]) for each in self.regions_and_versions]
        return [Entry(tenant_id, "externalServiceType", "externalServiceName", endpoints)]

    def uri_for_service(self, region, service_id):
        """
        Return the URI for the service in the given region.
        """
        for r, u in [(each[0], each[2]) for each in self.regions_and_versions]:
            if r == region:
                return u
        return u""
