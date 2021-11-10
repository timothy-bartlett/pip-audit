import json
import xml.etree.ElementTree as ET

from pip_audit.format import CycloneDxFormat


def test_cyclonedx_inner_json(vuln_data):
    formatter = CycloneDxFormat(inner_format=CycloneDxFormat.InnerFormat.Json)

    # We don't test CycloneDX's formatting/layout decisions, only that
    # the formatter emits correct JSON when initialized in JSON mode.
    assert json.loads(formatter.format(vuln_data)) is not None


def test_cyclonedx_inner_xml(vuln_data):
    formatter = CycloneDxFormat(inner_format=CycloneDxFormat.InnerFormat.Xml)

    # We don't test CycloneDX's formatting/layout decisions, only that
    # the formatter emits correct XML when initialized in XML mode.
    assert ET.fromstring(formatter.format(vuln_data)) is not None
