import xml.etree.ElementTree as ET
from lxml import etree
import requests

class ESEFiXBRLValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.namespaces = {
            'ix': 'http://www.xbrl.org/2013/inlineXBRL',
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'xhtml': 'http://www.w3.org/1999/xhtml',
            'link': 'http://www.xbrl.org/2003/linkbase',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
        self.tree = None
        self.root = None
        self.errors = []

    def validate(self):
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        
        self._validate_taxonomy()
        self._validate_mandatory_elements()
        self._validate_contexts()
        self._validate_units()
        self._validate_facts()
        
        return self.errors

    def _validate_taxonomy(self):
        # For demonstration, we'll just check if the IFRS taxonomy is referenced
        schema_refs = self.root.findall('.//link:schemaRef', self.namespaces)
        ifrs_taxonomy_found = any('http://www.ifrs.org/xbrl/taxonomy' in ref.get('{http://www.w3.org/1999/xlink}href', '') for ref in schema_refs)
        if not ifrs_taxonomy_found:
            self.errors.append("IFRS taxonomy not referenced")

    def _validate_mandatory_elements(self):
        mandatory_elements = [
            'ifrs-full:NameOfReportingEntityOrOtherMeansOfIdentification',
            'ifrs-full:DomicileOfEntity',
            'ifrs-full:LegalFormOfEntity',
            'ifrs-full:CountryOfIncorporation',
            'ifrs-full:PrincipalPlaceOfBusiness'
        ]
        for element in mandatory_elements:
            if not self.root.find(f'.//ix:nonNumeric[@name="{element}"]', self.namespaces):
                self.errors.append(f"Mandatory element missing: {element}")

    def _validate_contexts(self):
        contexts = self.root.findall('.//xbrli:context', self.namespaces)
        for context in contexts:
            if not context.get('id'):
                self.errors.append("Context without id found")
            if not context.find('.//xbrli:period', self.namespaces):
                self.errors.append(f"Context {context.get('id')} missing period")

    def _validate_units(self):
        units = self.root.findall('.//xbrli:unit', self.namespaces)
        for unit in units:
            if not unit.get('id'):
                self.errors.append("Unit without id found")
            if not unit.find('.//xbrli:measure', self.namespaces):
                self.errors.append(f"Unit {unit.get('id')} missing measure")

    def _validate_facts(self):
        facts = self.root.findall('.//ix:nonNumeric', self.namespaces) + self.root.findall('.//ix:nonFraction', self.namespaces)
        for fact in facts:
            if not fact.get('name'):
                self.errors.append("Fact without name attribute found")
            if not fact.get('contextRef'):
                self.errors.append(f"Fact {fact.get('name')} missing contextRef")
            if fact.tag.endswith('nonFraction') and not fact.get('unitRef'):
                self.errors.append(f"Numeric fact {fact.get('name')} missing unitRef")

# Usage
validator = ESEFiXBRLValidator('sample_esef.xhtml')
errors = validator.validate()
print("Validation Errors:", errors)