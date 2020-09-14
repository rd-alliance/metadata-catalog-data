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
    """Implementation of Perl's autovivification feature."""
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

old_db_file = os.path.join(default_source, 'db.json')
new_db_file = os.path.join(default_dest, 'db.json')

# Warning screen
# --------------

print(f"This utility will read the MSC v1 database located at {old_db_file}")
print(f"and write out the equivalent MSC v2 database to {new_db_file}.")
print(f"The process requires the RDF Turtle file at {kw_mapping}.")
print("Do you wish to continue?")
reply = input ("(yes/NO) > ")
if reply.lower() not in ["y", "yes"]:
    print("Okay, aborting.")
    sys.exit(0)

# Load mappings
# -------------

table_map = {
    "metadata-schemes": "m",
    "organizations": "g",
    "tools": "t",
    "mappings": "c",
    "endorsements": "e",
}

kw_map = dict()
try:
    with open(kw_mapping, 'r') as f:
        current_url = None
        for line in f:

            m = re.match(r'^([\S]+) a skos:Concept', line)
            if m:
                if m.group(1).startswith('msc:'):
                    current_url = m.group(1).replace(
                        'msc:', 'http://rdamsc.bath.ac.uk/thesaurus/')
                else:
                    current_url = m.group(1).replace(
                        ':', 'http://vocabularies.unesco.org/thesaurus/')
                continue

            m = re.match(r'^    skos:prefLabel "([^"]+)"@en .', line)
            if m:
                kw_map[m.group(1)] = current_url
                continue

except FileNotFoundError:
    print("Please use the tools provided to generate the MSC v2 vocabulary "
          f"Turtle file at {kw_mapping}.")
    sys.exit(1)

# Variables for populating new tables
# -----------------------------------

# These are the datatypes we know about:
datatype_labels = ['Catalog', 'Dataset']
datatype_table = dict()

relations = AutoDict()

# Perform migration
# -----------------

# Load v1 database:
try:
    with open(old_db_file, 'r') as f:
        old_db = json.load(f)
except FileNotFoundError:
    print(f"Please put a copy of the MSC v1 database at {old_db_file}.")
    sys.exit(1)

new_db = {
    "_default": {},
    "m": dict(),
    "g": dict(),
    "t": dict(),
    "c": dict(),
    "e": dict(),
    "rel": dict(),
}

# Iterate through records in each table in turn:
for in_table, out_table in table_map.items():
    in_records = old_db.get(in_table, dict())

    # `i` will hold the doc_id of the last record in the table:
    i = 0
    for record_key in in_records.keys():
        record_num = int(record_key)
        if record_num > i:
            i = record_num

    # `j` will be the doc_id of the record being migrated:
    for j in range(1, i + 1):
        in_record = in_records[f"{j}"]
        out_record = dict()

        for k, v in in_record.items():
            # Most fields are unchanged, but here are the exceptions:
            if k == "keywords":
                # Keywords are now identified by URI:
                old_v = v[:]
                v = list()
                for kw in old_v:
                    kwurl = kw_map.get(kw)
                    if kwurl is None:
                        print(f"Unmapped keyword: {kw}")
                        continue
                    v.append(kwurl)
            elif k == 'relatedEntities':
                # Relations between entities are in a separate table. We collect
                # the information here and will convert it to a table later:
                for ent in v:
                    if relations.get(f"msc:{out_table}{j}", dict()).get(
                            f"{ent['role']}s") is None:
                        relations[f"msc:{out_table}{j}"][
                            f"{ent['role']}s"] = list()
                    relations[f"msc:{out_table}{j}"][f"{ent['role']}s"].append(
                        ent['id'])
                continue
            elif k == 'dataTypes':
                # Datatypes are in a separate table and identified by MSC IDs
                old_v = v[:]
                v = list()
                for datatype in old_v:
                    label = datatype.get('label')
                    uri = datatype.get('url')
                    n = 0
                    if label is not None:
                        for n, datatype_label in enumerate(datatype_labels, 1):
                            if label == datatype_label:
                                break
                        else:
                            datatype_labels.append(label)
                            n = len(datatype_labels)
                        v.append(f"msc:datatype{n}")
                        if f"{n}" not in datatype_table:
                            datatype_table[f"{n}"] = {
                                "id": uri,
                                "label": label
                            }
            elif k == 'versions':
                # Dates of validity are now split into start/end fields:
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

# Write the relations table
# -------------------------

i = 1
for k, v in relations.items():
    item = {"@id": k}
    for vk, vv in v.items():
        item[vk] = sorted(vv, key=lambda k: k[:5] + k[5:].zfill(5))
    new_db["rel"][f"{i}"] = item
    i += 1

# Dump result to file
# -------------------

if not os.path.isdir(default_dest):
    os.mkdir(default_dest)
with open(new_db_file, 'w') as f:
    json.dump(new_db, f, indent=1, ensure_ascii=False)

# We print the datatypes we collected to the screen instead for manual editing:
if datatype_table:
    sorted_datatypes = {"datatype": dict()}
    for k in sorted(datatype_table.keys(), key=lambda k: int(k)):
        sorted_datatypes["datatype"][k] = datatype_table[k]
    print("Please add the following table to the terms.json database:")
    print(json.dumps(sorted_datatypes, ensure_ascii=False, indent=1))

print('Finished!')
