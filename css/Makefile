SHELL=bash
SRC:=$(shell find scss -type f -iregex "[^_].*\.scss")
CSS:=$(patsubst scss/%.scss,css/%.css,$(SRC))
MINCSS:=$(patsubst scss/%.scss,css/%.min.css,$(SRC))

all: $(CSS) $(MINCSS)

$(MINCSS): css/%.min.css : scss/%.scss $(shell find bootstrap/scss -type f)
	sass --update scss/$*.scss:$@ --style compressed --embed-sources

$(CSS): css/%.css: scss/%.scss $(shell find bootstrap/scss -type f)
	sass --update scss/$*.scss:$@
