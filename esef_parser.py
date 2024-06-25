import xml.etree.ElementTree as ET
import re
from collections import defaultdict

class ESEFiXBRLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.namespaces = {
            'ix': 'http://www.xbrl.org/2013/inlineXBRL',
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        self.tree = None
        self.root = None
        self.facts = defaultdict(list)

    def parse(self):
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        self._extract_facts()
        return self.facts

    def _extract_facts(self):
        for elem in self.root.findall('.//ix:nonNumeric', self.namespaces):
            name = elem.get('name')
            value = elem.text
            context_ref = elem.get('contextRef')
            self.facts[name].append({'value': value, 'context': context_ref})

        for elem in self.root.findall('.//ix:nonFraction', self.namespaces):
            name = elem.get('name')
            value = elem.text
            context_ref = elem.get('contextRef')
            unit_ref = elem.get('unitRef')
            self.facts[name].append({'value': value, 'context': context_ref, 'unit': unit_ref})

    def get_contexts(self):
        contexts = {}
        for context in self.root.findall('.//xbrli:context', self.namespaces):
            context_id = context.get('id')
            period = context.find('.//xbrli:period', self.namespaces)
            instant = period.find('xbrli:instant', self.namespaces)
            if instant is not None:
                contexts[context_id] = {'period': 'instant', 'date': instant.text}
            else:
                start_date = period.find('xbrli:startDate', self.namespaces).text
                end_date = period.find('xbrli:endDate', self.namespaces).text
                contexts[context_id] = {'period': 'duration', 'start_date': start_date, 'end_date': end_date}
        return contexts

    def get_units(self):
        units = {}
        for unit in self.root.findall('.//xbrli:unit', self.namespaces):
            unit_id = unit.get('id')
            measure = unit.find('.//xbrli:measure', self.namespaces).text
            units[unit_id] = measure
        return units

# Usage example
parser = ESEFiXBRLParser('sample_esef.xhtml')
facts = parser.parse()
contexts = parser.get_contexts()
units = parser.get_units()

print("Extracted Facts:", facts)
print("Contexts:", contexts)
print("Units:", units)
