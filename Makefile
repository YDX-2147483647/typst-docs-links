SHELL := /bin/bash
.DELETE_ON_ERROR:

.PHONY: all
all:
	mkdir -p build
	$(MAKE) \
		build/links-overview.svg \
		build/links-{tutorial+guide,foundations,model,text,math,layout,visualize,introspection,math}.svg \
		build/links.svg

build/docs.json:
	curl -L https://ydx-typst.netlify.app/docs.json -o $@

build/links.json: main.py build/docs.json
	uv run $<

build/links.dot: links_to_dot.py build/links.json
	uv run $< > $@
build/links-overview.dot: links_to_dot.py build/links.json
	uv run $< overview > $@
build/links-tutorial+guide.dot: links_to_dot.py build/links.json
	uv run $< /tutorial/ /guides/ > $@
build/links-%.dot: links_to_dot.py build/links.json
	uv run $< $(patsubst build/links-%.dot,/reference/%/,$@) > $@

%.svg: %.dot
	dot $< -o $@ -T svg -v
	sd '<svg width="\d+pt" height="\d+pt"' '<svg' $@
# 1. Enable verbose mode because there are many nodes and edges and it will be slow.
# 2. Remove width and height to permit automatic scaling.

.PHONY: view-docs
view-docs: build/docs.json
	nvim $< +':set nowrap' +':set foldmethod=indent'
