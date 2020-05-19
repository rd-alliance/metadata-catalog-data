# Base controlled vocabulary

This directory contains resources for generating the base controlled vocabulary
for the Metadata Standards Catalog, version 2.

More precisely, it generates the files included in the data directory of the
Catalog software package, which the Catalog uses to populate its database when
it is first run.

## Subject keywords

The Metadata Standards Catalog uses subject keywords drawn from the UNESCO
Thesaurus. Version 1 used that Thesaurus as distributed, treating its Domains
and Micro-Thesauri as higher level Concepts. This caused some issues since some
of the Concepts shared labels with the Micro-Thesauri, and in one case a
Micro-Thesaurus shared its label with a Domain.

Version 2 uses a simplified version of the UNESCO Thesaurus, similar to that
used in Version 1 but ensuring that all term labels are unique. The process of
simplification is encoded in `simplify.py` but in brief it runs like this:

 1. New Concepts under the URI path `http://rdamsc.bath.ac.uk/thesaurus`
    are created to correspond with UNESCO Domains and Micro-Thesauri. Some
    labels are changed to make them distinct or clarify how they should be used
    in the context of the Catalog.

 2. The Languages Micro-Thesaurus and its associated concepts (corresponding to
    named natural languages) is removed.

 3. Any UNESCO Concepts that have labels that clash with MSC Concepts, or that
    have a scope note to say that a more specific term should be used, are
    removed from the hierarchy. When term X is removed, X's narrower terms are
    marked as being narrower than X's broader term, and vice versa: essentially
    X's descendent terms are promoted up the hierarchy.

The changes made in step 1 are these:

| UNESCO Label  | MSC Label  |
| ------------- | ---------- |
| Culture  | Arts and humanities  |
| Countries and country groupings  | National and regional standards  |
| Biology  | Biological sciences  |
| Agriculture  | Agriculture and related  |
| Educational evaluation  | Educational assessment  |
| Educational policy  | Educational policy and development  |
| History  | Historical studies  |
| Medical sciences  | Medicine and health  |
| Meteorology  | Atmospheric sciences  |
| Natural resources  | Environmental sciences and engineering  |

Note that in the last case, ‘Environmental sciences and engineering’ is also
a UNESCO Micro-Thesaurus in its own right, so the MSC Concept represents a
merger of the two UNESCO Micro-Thesauri.

The Concepts removed in step 3 on the basis of their scope notes are as follows:

- Communication
- Culture (also a UNESCO Micro-Thesaurus)
- Education (also a UNESCO Domain)
- Educational courses
- Income and wealth
- Youth

A further 38 Concepts are removed as duplicates of MSC Concepts: please see the
script for the full list (around line 135).

To run `simplify.py` you will need Python v3.6+ and the [rdflib] package from
PyPI. It reads the file `unesco-thesaurus.ttl` from [UNESCO] (the version
included is from 2020-03-03) and generates two files:

  - `simplified-unesco-thesaurus.ttl` is the file needed by the Catalog.

  - `keyword_tree.md` renders the resulting terms in a nested list for easy
    inspection. If any duplicate Concepts are introduced, they are listed at
    the end for review.

[rdflib]: http://rdflib.readthedocs.io/
[UNESCO]: http://vocabularies.unesco.org/exports/thesaurus/latest/

## Types

The Metadata Standards Catalog uses a controlled vocabulary for recording the
types of various things. In version 1, these were hard-coded in some cases and
enforced with regular expressions in others. In version 2, the vocabulary is
maintained in a database that can be edited by users, and is therefore more
strictly ‘folksonomic’.

The Python v3.6+ script `write_terms.py` generates the file `vocabulary.json`.
This contains three tables:

  - `location` contains the types of link recognized by the Catalog.

  - `type` contains the types used for describing tools and organizations.

  - `id_scheme` contains the ID schemes recognized by the Catalog.

Currently no items for seeding the list of recognized data types are provided.
