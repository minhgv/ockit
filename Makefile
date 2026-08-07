# ockit Makefile — OpenCode Kit Command Automation

.PHONY: test test-destructive doctor verify sync clean

test:
	PYTHONPATH=src:tests python3 -m unittest discover -s tests/unit -p "test_*.py"

# Adversarial chaos suite — JS plugin tests (vitest) via .opencode package.
# Root is Python-only; all JS tooling lives under .opencode/.
test-destructive:
	npm --prefix .opencode test

doctor:
	ockit doctor

verify:
	ockit verify

sync:
	ockit sync --sync

clean:
	rm -rf build/ dist/ *.egg-info
