# Stylesheets

Version 1 of the Metadata Standards Catalog used Bootstrap version 3. That
stylesheet can be generated using the configuration file `v3_config.json` with
the [Bootstrap v3 customization tool][bscustom].

[bscustom]: https://getbootstrap.com/docs/3.4/customize/

Version 2 of the Metadata Standards Catalog uses Bootstrap version 4.

  - The upstream sources for Bootstrap are kept as distributed in the
    `bootstrap` directory. (Current version: 4.5)

  - The Metadata Standards Catalog stylesheet source code is in the `scss`
    directory. It loads and customizes the upstream SCSS code as necessary

  - The final CSS code, if and when generated, should be in the `css` directory.
    This is excluded from version control so won't appear on GitHub.

To compile the SCSS to CSS you will need a SASS compiler. The code has been
tested with Ruby Sass 3.7.3 and Dart Sass 1.26.5 but other compilers should work
as well. Suggestions for [how to install SASS][sass] may be found on the SASS
website.

[sass]: https://sass-lang.com/install

From this directory:

```bash
sass --update scss/msc.scss:css/msc.css
sass --update scss/msc.scss:css/msc.min.css --style compressed
```

Alternatively, you can use the included `Makefile`:

```bash
make
```
