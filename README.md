# grid-rdf
Make RDF from the Grid data for organizations, for use with Open VIVO

See http://grid.ac regarding the Grid project.  Grid is by Digital Science.  Grid data is available via CC-BY license, 
see citation below.

The download of the Grid data in this repository is a working copy.

## Goals of this work

1. Produce RDF of organizations for use with OpenVIVO -- OpenVIVO debuted at http://force16.org in Portland, 
April 17-19, 2016
1. Consider how best to provide an RDF package or service for VIVO
1. Consider how VIVO might interact with such an RDF package or service

## Data Citation

Digital-science, Data-science; Science, Digital (2016): GRID release 2016-09-14. figshare.
https://dx.doi.org/10.6084/m9.figshare.3807186
Retrieved: 14, SEP 16, 2016

## Change Log
**2016-09-14** v0.04 Fix country name in vcard -- now is vcard:country-name as expected.  Alternate labels are no
longer asserted as rdf:label, now asserted as skos:altLabel.  Primary name is now asserted as both rdfs:label and
skos:prefLabel. Skip relationship type "other".  Handle new identifier format in GRID JSON -- Fundref and ISNI now have
substructure, an "all" list and a "preferred" value.  all the values are processed.  VIVO does not have the notion of
preferred isni or preferred fundref, these are ignored.  Strips leading and trailing whitespace from identifiers.
