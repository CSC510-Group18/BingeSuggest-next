BUILT_FILE = dist/index.html

build-single-file:
	bun install
	bunx -b vite build
	echo 'Built file: $(BUILT_FILE)'

publish-to-gist:
	'gh' 'gist' 'create' $(BUILT_FILE) | sed 's/gist.github.com/g.teddysc.me/' | sed 's:/tddschn::' | tee /dev/tty | tr -d '\n' | pbcopy