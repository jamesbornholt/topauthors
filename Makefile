.PHONY: deploy

HOST := bornholt@recycle.cs.washington.edu
ROOT := public_html/confs/
RSYNC_ARGS := --compress --recursive --checksum --itemize-changes --filter='- .DS_Store' -e ssh

deploy:
	rsync $(RSYNC_ARGS) output/* $(HOST):$(ROOT)
