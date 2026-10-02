"""Output profiles are explicit descriptors, distinct from measured source data.

Discovery lets independent family branches add profiles without editing one global
list. A new output backend belongs in the descriptor's outputs, never in a fallback.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def load_profiles(root=ROOT):
    result = {}
    classes = set()
    for path in sorted((root / 'profiles').glob('*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        if record.get('kind') != 'wodtex-output-profile':
            continue
        style, cls = record.get('style_id', ''), record.get('class', '')
        if record.get('schema_version') != 1 or not re.fullmatch('[a-z][-a-z0-9]*', style) or not re.fullmatch('[a-z][a-z0-9]*', cls):
            raise ValueError('WODTEX_E_PROFILE_SCHEMA: ' + str(path))
        if style in result or cls in classes:
            raise ValueError('WODTEX_E_PROFILE_DUPLICATE: ' + style)
        if not record.get('outputs') or set(record['outputs']) - {'pdf', 'epub'}:
            raise ValueError('WODTEX_E_PROFILE_OUTPUT: ' + style)
        result[style] = record
        classes.add(cls)
    return result


def profile_for_class(root, class_name):
    for record in load_profiles(root).values():
        if record['class'] == class_name:
            return record
    raise ValueError('WODTEX_E_UNKNOWN_CLASS: ' + class_name)


def document_class(text):
    text = re.sub(r'(?<!\\)%[^\n]*', '', text)
    classes = re.findall(r'\\documentclass\s*(?:\[[^\]]*\]\s*)?\{([a-z][a-z0-9]*)\}', text)
    if len(classes) != 1:
        raise ValueError('WODTEX_E_DOCUMENT_CLASS: expected one literal registered class')
    return classes[0]
