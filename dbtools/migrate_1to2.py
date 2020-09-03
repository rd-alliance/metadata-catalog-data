#! /usr/bin/python3

# Dependencies
# ============

# Standard
# --------
import argparse
import os
import sys
import re
import datetime
import json

# Non-standard
# ------------
import yaml

# Initializing
# ============


class AutoDict(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


# Calculate defaults
# ------------------
script_dir = os.path.dirname(sys.argv[0])

default_source = os.path.realpath(
    os.path.join(script_dir, '..', 'old-db'))
default_dest = os.path.realpath(os.path.join(script_dir, '..', 'new-db'))
kw_mapping = os.path.realpath(os.path.join(script_dir, '..', 'vocab', 'simplified-unesco-thesaurus.ttl'))

log_file = os.path.realpath(os.path.join(script_dir, 'migration-log.txt'))
kw_file = os.path.realpath(os.path.join(script_dir, 'disciplines.yml'))

old_db_file = os.path.join(default_source, 'db.json')
new_db_file = os.path.join(default_dest, 'db.json')

# Load mappings

table_map = {
    "metadata-schemes": "m",
    "organizations": "g",
    "tools": "t",
    "mappings": "c",
    "endorsements": "e",
}

datatype_map = {
    'Catalog': 'msc:datatype1',
    'Dataset': 'msc:datatype2',
}

kw_map = dict()
with open(kw_mapping, 'r') as f:
    current_url = None
    for line in f:

        m = re.match(r'^([\S]+) a skos:Concept', line)
        if m:
            if m.group(1).startswith('msc:'):
                current_url = m.group(1).replace('msc:', 'http://rdamsc.bath.ac.uk/thesaurus/')
            else:
                current_url = m.group(1).replace(':', 'http://vocabularies.unesco.org/thesaurus/')
            continue

        m = re.match(r'^    skos:prefLabel "([^"]+)"@en .', line)
        if m:
            kw_map[m.group(1)] = current_url
            continue

# Perform migration

with open(old_db_file, 'r') as f:
    old_db = json.load(f)

new_db = {
    "_default": {},
    "m": dict(),
    "g": dict(),
    "t": dict(),
    "c": dict(),
    "e": dict(),
    "rel": dict(),
}

relations = AutoDict()

for in_table, out_table in table_map.items():
    in_records = old_db.get(in_table, dict())
    i = 0
    for record_key in in_records.keys():
        record_num = int(record_key)
        if record_num > i:
            i = record_num
    for j in range(1, i + 1):
        in_record = in_records[f"{j}"]
        out_record = dict()

        for k, v in in_record.items():
            if k == "keywords":
                old_v = v[:]
                v = list()
                for kw in old_v:
                    kwurl = kw_map.get(kw)
                    if kwurl is None:
                        print("Unmapped keyword: kw")
                        continue
                    v.append(kwurl)
            elif k == 'relatedEntities':
                for ent in v:
                    if relations.get(f"msc:{out_table}{j}", dict()).get(
                            f"{ent['role']}s") is None:
                        relations[f"msc:{out_table}{j}"][
                            f"{ent['role']}s"] = list()
                    relations[f"msc:{out_table}{j}"][f"{ent['role']}s"].append(
                        ent['id'])
                continue
            elif k == 'dataTypes':
                old_v = v[:]
                v = list()
                for datatype in old_v:
                    label = datatype.get('label')
                    if label is not None and label in datatype_map:
                        v.append(datatype_map[label])
            elif k == 'versions':
                old_v = v[:]
                v = list()
                for ver in old_v:
                    dates = ver.get('valid')
                    if dates is not None:
                        m = re.match(r'([-\d]+)(/[-\d]+)?', dates)
                        if m:
                            ver['valid'] = dict()
                            ver['valid']['start'] = m.group(1)
                            if m.group(2):
                                ver['valid']['end'] = m.group(2)[1:]
                    v.append(ver)
            out_record[k] = v

        new_db[out_table][f"{j}"] = out_record

i = 1
for k, v in relations.items():
    item = {"@id": k}
    for vk, vv in v.items():
        item[vk] = sorted(vv, key=lambda k: k[:5] + k[5:].zfill(5))
    new_db["rel"][f"{i}"] = item
    i += 1

with open(new_db_file, 'w') as f:
    json.dump(new_db, f, indent=1, ensure_ascii=False)

print('Finished!')
