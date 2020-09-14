# metadata-catalog-data

Support files used to generate and backup data and components for the Metadata
Standards Catalog

## Contents

  - `backup` contains an occasional public backup of the main record and
    controlled terms databases. (The subject thesaurus is read-only; see the
    `vocab` folder.)

  - `css` contains the code used to generate the Metadata Standards Catalog
    stylesheet. It is generated from [Bootstrap v4] sources with customizations
    using a SASS/SCSS compiler.

  - `dbtools` contains code for migrating data between MSD, MSCv1 and MSCv2
    databases.

  - `maintenance-mode` contains an HTML template for use when the Catalog is
    down for maintenance.

  - `users` contains code that can be used to (un)block users. It is recommended
    that the `rdamsc_userctl` module is installed into the virtual environment
    running the Catalog so all the dependency modules are at the same version
    as the Catalog itself.

  - `vocab` contains Python v3 code used to generate the Metadata Standards
    Catalog subject keyword thesaurus from the [UNESCO Thesaurus] and a starter
    set of controlled terms for recording the type of various things.

[Bootstrap v4]: https://getbootstrap.com/
[UNESCO Thesaurus]: http://vocabularies.unesco.org/
