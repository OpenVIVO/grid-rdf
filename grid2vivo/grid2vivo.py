#!/usr/bin/env/python

"""
    grid2vivo.py -- Read Grid data, make VIVO RDF
"""

from rdflib import Graph, Literal, RDFS, RDF, Namespace, URIRef, XSD
import json
import logging

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "Apache License 2.0"
__version__ = "0.01"

#   Constants

uri_prefix = "http://openvivo.org/a/"
vivo_prefix = "http://vivoweb.org/ontology/core#"
foaf_prefix = "http://xmlns.com/foaf/0.1/"
VIVO = Namespace(vivo_prefix)
FOAF = Namespace(foaf_prefix)

# Setup logging

logging.basicConfig()

#   Helper functions


def add_external_ids(uri, inst):
    if 'external_ids' in inst:
        if 'ISNI' in inst['external_ids']:
            for isni in inst['external_ids']['ISNI']:
                g.add((uri, VIVO.isni, Literal(isni)))
        if 'FundRef' in inst['external_ids']:
            for fund_ref in inst['external_ids']['FundRef']:
                g.add((uri, VIVO.fundRefId, Literal(fund_ref)))


def add_acronyms(uri, inst):
    if 'acronyms' in inst:
        for acronym in inst['acronyms']:
            g.add((uri, VIVO.abbreviation, Literal(acronym)))


def add_aliases(uri, inst):
    if 'aliases' in inst:
        for alias in inst['aliases']:
            g.add((uri, RDFS.label, Literal(alias)))


def add_established(uri, inst):
    if 'established' in inst and inst['established'] is not None:
        year = str(inst['established'])
        date_uri = URIRef(uri_prefix + 'date' + year)
        g.add((uri, VIVO.dateEstablished, date_uri))


def add_type(uri, inst):

    #   TODO: Handle type 'Facility' (not an organization?)

    type_table = {
        'Facility': None,
        'Company':	VIVO.Company,
        'Government': 	VIVO.GovernmentAgency,
        'Other': None,
        'Healthcare': VIVO.HealthcareOrganization,
        'Nonprofit': VIVO.NonProfitCompany,
        'Education': VIVO.EducationOrganization,
        'Archive': 	VIVO.ArchiveOrganization
    }
    if 'types' in inst:
            for grid_type in inst['types']:
                vivo_type = type_table.get(grid_type, None)
                if vivo_type is not None:
                    g.add((uri, RDF.type, vivo_type))


def add_relationships(uri, inst):
    if 'relationships' in inst:
        for relationship in inst['relationships']:
            to_uri = URIRef(uri_prefix + relationship['id'])
            relationship_type = relationship['type']
            if relationship_type == 'Affiliated':
                g.add((uri, VIVO.hasAffiliatedOrganization, to_uri))
                g.add((to_uri, VIVO.hasAffiliatedOrganization, uri))  # own inverse
            elif relationship_type == 'Child':
                g.add((uri, VIVO.hasSubOrganization, to_uri))  # sub class of BFO_0000051 (has part)
            elif relationship_type == 'Parent':
                g.add((uri, VIVO.hasSuperOrganization, to_uri))  # sub class of BFO_0000050 (part of)
            else:
                raise KeyError(relationship_type)


def add_vcard(uri, inst):

    # TODO: Handle more than one address.  For now, assume one address and put all contact info on one vcard
    # TODO: Handle geonames content.

    if 'addresses' not in inst or len(inst['addresses']) == 0:
        return

    address = inst['addresses'][0]
    url_rank = 0

    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    vcard_uri = URIRef(str(uri)+'-vcard')
    g.add((vcard_uri, RDF.type, VCARD.organization))
    g.add((uri, VIVO.hasContactInfo, vcard_uri))

    #   Add Address

    vcard_address_uri = URIRef(str(vcard_uri) + '-address')
    g.add((vcard_uri, VCARD.hasAddress, vcard_address_uri))
    if 'city' in address and address['city'] is not None and len(address['city']) > 0:
        g.add((vcard_address_uri, VCARD.locality, Literal(address['city'])))
    if 'postcode' in address and address['postcode'] is not None and len(address['postcode']) > 0:
        g.add((vcard_address_uri, VCARD.postalCode, Literal(address['postcode'])))

    lines = []
    for line in ['line_1', 'line_2', 'line_3']:
        if address[line] is not None and len(address[line]) > 0:
            lines.append(address[line])
    street_address = ';'.join(lines)
    if len(street_address) > 0:
        g.add((vcard_address_uri, VCARD.streetAddress, Literal(street_address)))

    if 'state' in address and address['state'] is not None and len(address['state']) > 0:
        g.add((vcard_address_uri, VCARD.region, Literal(address['state'])))
    if 'country' in address and address['country'] is not None and len(address['country']) > 0:
        g.add((vcard_address_uri, VCARD.country, Literal(address['country'])))

    #   Add geolocation

    if 'lat' in address and address['lat'] is not None and 'lng' in address and address['lng'] is not None:
        vcard_geo_uri = URIRef(str(vcard_uri) + '-geo')
        g.add((vcard_uri, VCARD.hasGeo, vcard_geo_uri))
        g.add((vcard_geo_uri, VCARD.geo, Literal('geo:'+str(address['lat'])+','+str(address['lng']))))

    #   Add Email

    if 'email_address' in inst and inst['email_address'] is not None:
        vcard_email_uri = URIRef(str(vcard_uri) + '-email')
        g.add((vcard_uri, VCARD.hasEmail, vcard_email_uri))
        g.add((vcard_email_uri, VCARD.email, Literal(inst['email_address'])))

    #   Add Wikipedia URL

    if 'wikipedia_url' in inst and inst['wikipedia_url'] is not None:
        url_rank += 1
        vcard_wikipedia_uri = URIRef(str(vcard_uri) + '-wikipedia')
        g.add((vcard_uri, VCARD.hasURL, vcard_wikipedia_uri))
        g.add((vcard_wikipedia_uri, VCARD.url, URIRef(inst['wikipedia_url'].strip())))
        g.add((vcard_wikipedia_uri, VIVO.rank, Literal(str(url_rank), datatype=XSD.integer)))
        g.add((vcard_wikipedia_uri, RDFS.label, Literal('Wikipedia Page')))

    # Add Links

    if 'links' in inst:
        for link in inst['links']:
            if link is not None and len(link) > 0:
                url_rank += 1
                vcard_link_uri = URIRef(str(vcard_uri) + '-link' + str(url_rank))
                g.add((vcard_uri, VCARD.hasURL, vcard_link_uri))
                g.add((vcard_link_uri, VCARD.url, URIRef(link.strip())))
                g.add((vcard_link_uri, VIVO.rank, Literal(str(url_rank), datatype=XSD.integer)))
                if link == inst['links'][0]:
                    link_text = "Home Page"
                else:
                    link_text = "Additional Link"
                g.add((vcard_link_uri, RDFS.label, Literal(link_text)))


def make_grid_rdf(inst):
    """
    Given an institute from the Grid data, add triples to the graph representing the institute

    Note:  We do not handle IP addresses.  No relevance for VIVO

    :param inst: a dict containing the institute's Grid data
    :return:
    """
    #   TODO: Handle status other than 'active' (include 'redirect')
    #   TODO: Handle 'weight'

    uri = URIRef(uri_prefix + inst['id'])

    g.add((uri, RDF.type, FOAF.Organization))
    g.add((uri, VIVO.gridId, Literal(inst['id'])))
    g.add((uri, RDFS.label, Literal(inst['name'])))

    add_external_ids(uri, inst)
    add_acronyms(uri, inst)
    add_type(uri, inst)
    add_established(uri, inst)
    add_relationships(uri, inst)
    add_aliases(uri, inst)
    add_vcard(uri, inst)  # handles wikipedia_url, links, addresses, geolocation, and email_address


g = Graph()

#   Read the Grid organization data

grid_file = open('../grid/grid.json')
grid_all = json.load(grid_file)

version = grid_all['version']
print 'Grid', version

grid = grid_all['institutes']
print len(grid), "institutes"

#   Make RDF for each active institute

count = 0
for institute in grid:
    count += 1
    if count % 100 == 0:
        print count
    if institute['status'] == 'active':
        make_grid_rdf(institute)

#   Generate the RDF file

triples_file = open('grid.rdf', 'w')
print >>triples_file, g.serialize(format='nt')
triples_file.close()
