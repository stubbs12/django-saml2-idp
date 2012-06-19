"""
Functions for creating XML output.
"""
import logging
import string
from xml_signing import get_signature_xml
from xml_templates import ASSERTION_GOOGLE_APPS, ASSERTION_SALESFORCE, RESPONSE

def _get_in_response_to(params):
    """
    Insert InResponseTo if we have a RequestID.
    Modifies the params dict.
    """
    #NOTE: I don't like this. We're mixing templating logic here, but the
    # current design requires this; maybe refactor using better templates, or
    # just bite the bullet and use elementtree to produce the XML; see comments
    # in xml_templates about Canonical XML.
    request_id = params.get('REQUEST_ID', None)
    if request_id:
        params['IN_RESPONSE_TO'] = 'InResponseTo="%s" ' % request_id
    else:
        params['IN_RESPONSE_TO'] = ''

def _get_assertion_xml(template, parameters, signed=False):
    # Reset signature.
    params = {}
    params.update(parameters)
    params['ASSERTION_SIGNATURE'] = ''
    template = string.Template(template)

    _get_in_response_to(params)

    unsigned = template.substitute(params)
    logging.debug('Unsigned:')
    logging.debug(unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(unsigned, params['ASSERTION_ID'])
    params['ASSERTION_SIGNATURE'] = signature_xml
    signed = template.substitute(params)

    logging.debug('Signed:')
    logging.debug(signed)
    return signed

def get_assertion_googleapps_xml(parameters, signed=False):
    return _get_assertion_xml(ASSERTION_GOOGLE_APPS, parameters, signed)

def get_assertion_salesforce_xml(parameters, signed=False):
    return _get_assertion_xml(ASSERTION_SALESFORCE, parameters, signed)

def get_response_xml(parameters, signed=False):
    """
    Returns XML for response, with signatures, if signed is True.
    """
    # Reset signatures.
    params = {}
    params.update(parameters)
    params['RESPONSE_SIGNATURE'] = ''
    _get_in_response_to(params)

    template = string.Template(RESPONSE)
    unsigned = template.substitute(params)

    logging.debug('Unsigned:')
    logging.debug(unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(unsigned, params['RESPONSE_ID'])
    params['RESPONSE_SIGNATURE'] = signature_xml
    signed = template.substitute(params)

    logging.debug('Signed:')
    logging.debug(signed)
    return signed