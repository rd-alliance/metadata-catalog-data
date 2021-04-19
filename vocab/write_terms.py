#! /usr/bin/env python3

import json

data = {
    'location': list(),
    'type': list(),
    'id_scheme': list()}

series = {
    'm': 'scheme',
    'g': 'organization',
    't': 'tool',
    'e': 'endorsement',
    'c': 'mapping',
    }

computing_platforms = ['Windows', 'Mac OS X', 'Linux', 'BSD', 'cross-platform']

programming_languages = [
    'C', 'Java', 'PHP', 'JavaScript', 'C++', 'Python', 'Shell', 'Ruby',
    'Objective-C', 'C#', 'XML']
programming_languages.sort()

location_tuples = [
    ('website', 'website', ['m', 'g', 't']),
    ('email', 'contact email address', ['g']),
    ('document', 'specification document', ['m', 'c']),
    ('document', 'documentation', ['t']),
    ('document', 'document', ['e']),
    ('DTD', 'XML/SGML DTD', ['m']),
    ('XSD', 'XML Schema', ['m']),
    ('RDFS', 'RDF Schema', ['m']),
    ('JSON', 'JSON Schema', ['m']),
    ('RDA-MIG', 'RDA MIG Schema', ['m']),
    ('application', 'web application', ['t', 'c']),
    ('service', 'service endpoint', ['t', 'c'])]

for language in programming_languages:
    location_tuples.append(
        (f"library ({language})", f"library ({language})", ['c']))
for platform in computing_platforms:
    location_tuples.append(
        (f"executable ({platform})", f"executable ({platform})", ['c']))

for id, label, serieses in location_tuples:
    applies = [series[s] for s in serieses]
    data['location'].append(
        {'id': id, 'label': label, 'applies': applies})

type_tuples = [
    ('standards body', 'standards body', ['g']),
    ('archive', 'archive', ['g']),
    ('professional group', 'professional group', ['g']),
    ('coordination group', 'coordination group', ['g']),
    ('web application', 'web application', ['t']),
    ('web service', 'web service', ['t'])]
for platform in computing_platforms:
    type_tuples.append(
        (f"terminal ({platform})", f"terminal ({platform})", ['t']))
    type_tuples.append(
        (f"graphical ({platform})", f"graphical ({platform})", ['t']))

for id, label, serieses in type_tuples:
    applies = [series[s] for s in serieses]
    data['type'].append(
        {'id': id, 'label': label, 'applies': applies})

id_scheme_tuples = [
    ('DOI', 'DOI', ['m', 'g', 't', 'c', 'e']),
    ('Handle', 'Handle', ['m', 't', 'c', 'e']),
    ('ROR', 'ROR', ['g']),
    ]

for id, label, serieses in id_scheme_tuples:
    applies = [series[s] for s in serieses]
    data['id_scheme'].append(
        {'id': id, 'label': label, 'applies': applies})

with open('vocabulary.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
