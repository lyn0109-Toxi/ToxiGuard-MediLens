"""DailyMed SPL composition: preserve source quantities; never infer missing mass."""
from __future__ import annotations
import json
import math
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import certifi
from ingredient_evidence import narrative_sections

NS = {'h': 'urn:hl7-org:v3'}
BASE = 'https://dailymed.nlm.nih.gov/dailymed/services/v2'
MASS = {'kg': Decimal('1000000'), 'g': Decimal('1000'), 'mg': Decimal(1), 'ug': Decimal('.001'), 'mcg': Decimal('.001'), 'µg': Decimal('.001')}
VOLUME = {'L': Decimal(1000), 'mL': Decimal(1), 'uL': Decimal('.001')}

class SourceError(Exception):
    pass

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MediLensComposition/1.0', 'Accept': 'application/json, application/xml'})
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context(cafile=certifi.where())) as response:
            return response.read(12_000_001)
    except Exception as exc:
        raise SourceError('DailyMed request failed. Please retry or open the original source.') from exc

def search_labels(name, organization='', role='manufacturer', page=1):
    name = name.strip()
    if len(name) < 2:
        raise ValueError('Enter at least two characters.')
    params = {'drug_name': name, 'name_type': 'both', 'pagesize': 30, 'page': int(page)}
    if organization.strip():
        if role not in ('manufacturer', 'labeler'):
            raise ValueError('Unknown organization role')
        params[role] = organization.strip()
    url = BASE + '/spls.json?' + urllib.parse.urlencode(params)
    try:
        result = json.loads(fetch(url))
        if not isinstance(result, dict):
            raise ValueError('Invalid search response')
        data, metadata = result.get('data', []), result.get('metadata', {})
        if not isinstance(data, list) or not isinstance(metadata, dict) or any(not isinstance(r, dict) or not r.get('setid') or not r.get('title') for r in data):
            raise ValueError('Invalid search structure')
        return {'data': data, 'metadata': metadata, 'url': url}
    except (ValueError, TypeError) as exc:
        raise SourceError('DailyMed returned an unreadable search response.') from exc

def txt(node, path, default=''):
    el = node.find(path, NS)
    return ''.join(el.itertext()).strip() if el is not None else default

def attr(node, path, key, default=''):
    el = node.find(path, NS)
    return el.get(key, default) if el is not None else default

def quantity(ingredient):
    return {k: {'value': attr(ingredient, 'h:quantity/h:' + k, 'value'), 'unit': attr(ingredient, 'h:quantity/h:' + k, 'unit')} for k in ('numerator', 'denominator')}

def number(value):
    try:
        d = Decimal(value)
        return d if d.is_finite() and d > 0 else None
    except (InvalidOperation, TypeError, ValueError):
        return None

def strength(item):
    q = item['quantity']; n, d = q['numerator'], q['denominator']
    if number(n['value']) is None or number(d['value']) is None or not n['unit'] or not d['unit']:
        return None
    denominator_unit = "unit" if d["unit"] == "1" else d["unit"]
    return f"{n['value']} {n['unit']} / {d['value']} {denominator_unit}"

def parse_spl(raw, source_url='', retrieved_at=None):
    if len(raw) > 12_000_000 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise SourceError('Unsupported label XML.')
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise SourceError('DailyMed returned invalid XML.') from exc
    labeler = txt(root, 'h:author/h:assignedEntity/h:representedOrganization/h:name')
    sections = []
    for section in root.findall('.//h:section', NS):
        # Direct section text preserves the original wording, without conflating tables with structured values.
        text_node = section.find('h:text', NS)
        if text_node is not None:
            sections.append({'title': txt(section, 'h:title'), 'text': ' '.join(' '.join(text_node.itertext()).split())})
    products = []
    for p in root.findall('.//h:manufacturedProduct/h:manufacturedProduct', NS):
        ingredients = []
        for i in p.findall('h:ingredient', NS):
            code = i.get('classCode', '')
            if code not in ('ACTIB', 'ACTIM', 'ACTIR', 'IACT'):
                continue
            name = txt(i, 'h:ingredientSubstance/h:name')
            moieties = [x.text or '' for x in i.findall('h:ingredientSubstance/h:activeMoiety/h:activeMoiety/h:name', NS)]
            reference = txt(i, 'h:ingredientSubstance/h:asEquivalentSubstance/h:definingSubstance/h:name')
            basis = name if code == 'ACTIB' else ('; '.join(moieties) if code == 'ACTIM' else reference if code == 'ACTIR' else name)
            ingredients.append({'name': name, 'unii': attr(i, 'h:ingredientSubstance/h:code', 'code') if attr(i, 'h:ingredientSubstance/h:code', 'codeSystem') == '2.16.840.1.113883.4.9' else None, 'class_code': code, 'active': code.startswith('ACT'), 'active_moieties': moieties, 'reference_substance': reference, 'basis': basis or None, 'quantity': quantity(i), 'original_xml': ET.tostring(i, encoding='unicode')})
        if not ingredients:
            continue
        form = attr(p, 'h:formCode', 'displayName')
        # Release follows the product's structured dosage form, never absence of an ER keyword.
        f = form.upper()
        release = 'extended' if 'EXTENDED RELEASE' in f else 'delayed' if 'DELAYED RELEASE' in f else 'immediate' if 'IMMEDIATE RELEASE' in f else 'unspecified'
        manufacturers = [txt(x, 'h:manufacturerOrganization/h:name') for x in p.findall('h:asManufacturedProduct', NS)]
        products.append({'name': txt(p, 'h:name'), 'generic': txt(p, 'h:asEntityWithGeneric/h:genericMedicine/h:name'), 'ndc': attr(p, 'h:code', 'code'), 'form': form, 'release': release, 'manufacturer': ', '.join(filter(None, manufacturers)) or None, 'labeler': labeler or None, 'ingredients': ingredients})
    return {'setid': attr(root, 'h:setId', 'root'), 'version': attr(root, 'h:versionNumber', 'value'), 'effective_date': attr(root, 'h:effectiveTime', 'value'), 'title': txt(root, 'h:title'), 'retrieved_at': retrieved_at or datetime.now(timezone.utc).isoformat(), 'source_url': source_url, 'products': products, 'sections': sections, 'inactive_narrative': narrative_sections(root)}

def load_label(setid):
    import re
    if not re.fullmatch(r'[a-fA-F0-9-]{36}', setid):
        raise ValueError('Invalid SPL identifier')
    url = BASE + '/spls/' + setid + '.xml'
    record = parse_spl(fetch(url), url)
    if record['setid'].lower() != setid.lower():
        raise SourceError('Returned label does not match the selected SPL identifier.')
    return record

def chart_groups(ingredients, basis='normalized'):
    """Only mass strengths with known basis and identical/convertible denominators."""
    if basis not in ('label', 'normalized'):
        raise ValueError('Unknown display basis')
    groups = defaultdict(list)
    for i in ingredients:
        if not i['active'] or not i.get('basis'):
            continue
        q = i['quantity']; n, d = q['numerator'], q['denominator']
        nv, dv = number(n['value']), number(d['value'])
        if nv is None or dv is None or n['unit'] not in MASS:
            continue
        try:
            if d['unit'] in VOLUME:
                key, divisor = (f"mg / {d['value']} {d['unit']}", Decimal(1)) if basis == 'label' else ('mg / mL', dv * VOLUME[d['unit']])
            elif d['unit'] == '1':
                key, divisor = (f"mg / {d['value']} unit", Decimal(1)) if basis == 'label' else ('mg / unit', dv)
            else:
                # Unknown denominator units are intentionally excluded.
                continue
        except ArithmeticError:
            continue
        # Decimal source quantities can exceed the finite range of browser/chart floats.
        # Keep original evidence, but never chart overflow, underflow-to-zero or NaN.
        try:
            amount = float(nv * MASS[n['unit']] / divisor)
        except (ArithmeticError, ValueError):
            continue
        if not math.isfinite(amount) or amount <= 0:
            continue
        groups[key].append({'ingredient': i['name'], 'basis': i['basis'], 'amount': amount, 'original_strength': strength(i), 'unii': i.get('unii')})
    return dict(groups)
