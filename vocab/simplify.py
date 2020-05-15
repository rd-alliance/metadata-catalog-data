#! /usr/bin/env python3

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import SKOS, RDF

orig = Graph()
orig.parse('unesco-thesaurus.ttl', format='turtle')

g = Graph(namespace_manager=orig.namespace_manager)
g.bind('uno', 'http://vocabularies.unesco.org/ontology#')
UNO = Namespace('http://vocabularies.unesco.org/ontology#')
UNT = Namespace('http://vocabularies.unesco.org/thesaurus/')
unt = URIRef('http://vocabularies.unesco.org/thesaurus')
msct = URIRef('http://rdamsc.bath.ac.uk/thesaurus')
g.bind('msc', 'http://rdamsc.bath.ac.uk/thesaurus/')
MSC = Namespace('http://rdamsc.bath.ac.uk/thesaurus/')


def expunge(node: URIRef):
    '''Remove a node and all descendent nodes.'''
    children = g.objects(node, SKOS.narrower)
    for child in children:
        expunge(child)
    g.remove((node, None, None))
    g.remove((None, None, node))


def prune(node: URIRef):
    '''Removes a node, makes all child nodes descend directly
    from the parent.'''
    parents = g.objects(node, SKOS.broader)
    parent = None
    for p in parents:
        if parent is not None:
            print(f"Could not get unique parent for {node}.")
            return
        parent = p
    children = g.objects(node, SKOS.narrower)
    for child in children:
        g.add((parent, SKOS.narrower, child))
        g.add((child, SKOS.broader, parent))
    g.remove((node, None, None))
    g.remove((None, None, node))


def replace(old: URIRef, new: URIRef, label: str):
    '''Removes old node, gives new node the same type and relationships
    as the old one, and gives it the new preferred label.'''
    g.add((new, RDF.type, SKOS.Concept))
    g.add((new, SKOS.prefLabel, Literal(label, lang='en')))
    for p in [SKOS.broader, SKOS.narrower]:
        for o in g.objects(old, p):
            g.add((new, p, o))
        for s in g.subjects(p, old):
            g.add((s, p, new))
    g.remove((old, None, None))
    g.remove((None, None, old))


def subsume(old: URIRef, new: URIRef):
    '''Removes old node, copying its has-narrower/is-broader-than
    relationships to apply to the new node.'''
    for o in g.objects(old, SKOS.narrower):
        g.add((new, SKOS.narrower, o))
    for s in g.subjects(SKOS.broader, old):
        g.add((s, SKOS.broader, new))
    g.remove((old, None, None))
    g.remove((None, None, old))


g.add((msct, RDF.type, SKOS.ConceptScheme))
g.add((msct, SKOS.prefLabel, Literal("RDA MSC Thesaurus", lang='en')))
g.add((UNT.domain0, RDF.type, UNO.Domain))
g.add((UNT.domain0, SKOS.prefLabel, Literal("Multidisciplinary", lang='en')))

print('Cherry-picking the triples used by the app...')
labels = orig.triples((None, SKOS.prefLabel, None))
for s, p, o in labels:
    if o.language == 'en':
        g.add((s, p, o))
g += orig.triples((None, RDF.type, SKOS.Concept))
g += orig.triples((None, RDF.type, UNO.MicroThesaurus))
g += orig.triples((None, RDF.type, UNO.Domain))

# Among the concepts, these are the ones we use
g += orig.triples((None, SKOS.broader, None))
g += orig.triples((None, SKOS.narrower, None))

# We convert domains to top-level concepts
for s, p, o in orig.triples((None, SKOS.member, None)):
    if (o, RDF.type, SKOS.Concept) in orig and (
            o, SKOS.topConceptOf, unt) not in orig:
        continue
    g.add((s, SKOS.narrower, o))
    g.add((o, SKOS.broader, s))

# Now rename domains into RDA MSC namespace:
id_map = {
    'domain3': "Arts and humanities",  # was Culture
    'domain7': "National and regional standards",  # was Countries and country groupings
    }
for d in g.subjects(RDF.type, UNO.Domain):
    label = str(g.preferredLabel(d, lang='en')[0][1])
    id = str(d.n3(g.namespace_manager)).replace(':', '')
    # Apply exceptions...
    label = id_map.get(id, label)
    replace(UNT[id], MSC[id], label)
    g.add((MSC[id], SKOS.topConceptOf, msct))

expunge(UNT['mt3.35'])  # Languages (family tree of specific ones)
subsume(UNT['mt2.65'], UNT['mt2.55'])  # Natural resources -> Environmental sciences and engineering
id_map = {
    'mt2.70': "Biological sciences",  # was Biology
    'mt6.35': "Agriculture and related",  # was Agriculture
    'mt1.65': "Educational assessment",  # was Educational evaluation
    'mt1.10': "Educational policy and development",  # was Educational policy
    'mt3.25': "Historical studies",  # was History
    'mt2.80': "Medicine and health",  # was Medical sciences
    'mt2.45': "Atmospheric sciences",  # was Meteorology
    }
for mt in g.subjects(RDF.type, UNO.MicroThesaurus):
    label = str(g.preferredLabel(mt, lang='en')[0][1])
    id = str(mt.n3(g.namespace_manager)).replace(':', '')
    newid = id.replace('mt', 'subdomain').replace('.', '')
    # Apply exceptions...
    label = id_map.get(id, label)
    replace(UNT[id], MSC[newid], label)

# Prune and ensure all remaining labels are unique
for s, p, o in orig.triples((None, SKOS.scopeNote, None)):
    if o.language == 'en':
        do_not_use = "Use more specific descriptor."
        if do_not_use in str(o):
            prune(s)
prune(UNT.concept688)  # Africa
prune(UNT.concept813)  # Asia and the Pacific
prune(UNT.concept49)   # Curriculum
prune(UNT.concept157)  # Earth sciences
prune(UNT.concept594)  # Economic and social development
prune(UNT.concept585)  # Economics
prune(UNT.concept21)   # Educational administration
prune(UNT.concept95)   # Educational facilities
prune(UNT.concept44)   # Educational institutions
prune(UNT.concept31)   # Educational management
prune(UNT.concept14)   # Educational planning
prune(UNT.concept901)  # Europe
prune(UNT.concept434)  # Family
prune(UNT.concept557)  # Human rights
prune(UNT.concept188)  # Hydrology
prune(UNT.concept608)  # Industry
prune(UNT.concept484)  # Information industry
prune(UNT.concept455)  # Information sciences
prune(UNT.concept503)  # Information sources
prune(UNT.concept575)  # International relations
prune(UNT.concept683)  # Labour
prune(UNT.concept367)  # Leisure
prune(UNT.concept310)  # Linguistics
prune(UNT.concept328)  # Literature
prune(UNT.concept365)  # Museums
prune(UNT.concept233)  # Natural sciences
prune(UNT.concept251)  # Pathology
prune(UNT.concept355)  # Performing arts
prune(UNT.concept680)  # Personnel management
prune(UNT.concept428)  # Population
prune(UNT.concept392)  # Psychology
prune(UNT.concept289)  # Religion
prune(UNT.concept104)  # Science
prune(UNT.concept409)  # Social problems
prune(UNT.concept380)  # Social sciences
prune(UNT.concept402)  # Social systems
prune(UNT.concept154)  # Space sciences
prune(UNT.concept347)  # Visual arts

print('Writing simplified thesaurus.')
g.serialize('simplified-thesaurus.ttl', format='turtle')

unique_labels = list()
labelholders = dict()

for d in g.subjects(SKOS.topConceptOf, msct):
    label = str(g.preferredLabel(d, lang='en')[0][1])
    id = str(d.n3(g.namespace_manager))
    if label not in unique_labels:
        unique_labels.append(label)
        labelholders[label] = [id]
    else:
        labelholders[label].append(id)
    for mt in g.objects(d, SKOS.narrower):
        label = str(g.preferredLabel(mt, lang='en')[0][1])
        id = str(mt.n3(g.namespace_manager))
        if label not in unique_labels:
            unique_labels.append(label)
            labelholders[label] = [id]
        else:
            labelholders[label].append(id)
        for c in g.objects(mt, SKOS.narrower):
            label = str(g.preferredLabel(c, lang='en')[0][1])
            id = str(c.n3(g.namespace_manager))
            if label not in unique_labels:
                unique_labels.append(label)
                labelholders[label] = [id]
            else:
                labelholders[label].append(id)

print("Duplicates:")
print()

for label in sorted(labelholders.keys()):
    ids = labelholders[label]
    if len(ids) > 1:
        print(label)
        print()
        for id in ids:
            print(f"- {id}")
        print()


def termtree(parent_uri: URIRef=None, level=0):
    tree = list()
    if parent_uri:
        uris = g.objects(parent_uri, SKOS.narrower)
    else:
        uris = g.subjects(SKOS.topConceptOf, msct)
    if not uris:
        return tree
    entries = list()
    for uri in uris:
        label = str(g.preferredLabel(uri, lang='en')[0][1])
        id = str(uri.n3(g.namespace_manager))
        entries.append((uri, label, id))
    entries.sort(key=lambda k: k[1])
    for uri, label, id in entries:
        tree.append(f"{'  ' * level}- {label} ({id})\n")
        children = termtree(uri, level + 1)
        if children:
            tree.extend(children)
    return tree


print("Writing out test hierarchy...")
with open('keyword_tree.md', 'w') as f:
    f.writelines(termtree())
