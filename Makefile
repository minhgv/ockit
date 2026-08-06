# ockit Makefile — OpenCode Kit Command Automation

.PHONY: test doctor verify sync clean

test:
	PYTHONPATH=src:tests python3 -m unittest discover -s tests/unit -p "test_*.py"

doctor:
	ockit doctor

verify:
	ockit verify

sync:
	ockit sync --sync

clean:
	rm -rf build/ dist/ *.egg-info
