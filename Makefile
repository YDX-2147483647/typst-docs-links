.PHONY := all
all: links.svg

docs.json:
	curl -LO https://ydx-typst.netlify.app/docs.json

links.json: docs.json main.py
	uv run main.py

links.dot: links.json links_to_dot.py
	uv run links_to_dot.py > links.dot

links.svg: links.dot
	dot links.dot -o links.svg -T svg -v
	sd '<svg width="\d+pt" height="\d+pt"' '<svg' links.svg
# 1. Enable verbose mode because there are many nodes and edges and it will be slow.
# 2. Remove width and height to permit automatic scaling.

.PHONY := view-docs
view-docs: docs.json
	nvim docs.json +':set nowrap' +':set foldmethod=indent'  
