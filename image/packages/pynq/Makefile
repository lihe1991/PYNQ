PACKAGE_BUILD += ${WORKDIR}/PYNQ ${WORKDIR}/reveal.js

REVEAL_REPO ?= https://github.com/hakimel/reveal.js.git
REVEAL_COMMIT ?= 568c7516f7ff7da7824db033946619d2c7ad761f

${WORKDIR}/PYNQ:
	git_clone_checkout ${PYNQ_REPO} ${PYNQ_COMMIT} ${WORKDIR}/PYNQ

${WORKDIR}/reveal.js:
	git_clone_checkout ${REVEAL_REPO} ${REVEAL_COMMIT} ${WORKDIR}/reveal.js
