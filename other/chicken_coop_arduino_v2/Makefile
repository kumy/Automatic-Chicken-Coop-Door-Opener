
# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

all: build stop_daemon upload start_daemon

build: ## build code
	arduino-cli compile --fqbn arduino:avr:diecimila chicken-coop-arduino

upload: ## upload firmware
	arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:diecimila chicken-coop-arduino

start_daemon: ## start flask daemon
	sudo systemctl start chicken-coop.service

stop_daemon: ## stop flask daemon
	sudo systemctl stop chicken-coop.service

restart_daemon: stop_daemon start_daemon ## restart flask daemon

journal_daemon: ## stop flask daemon
	journalctl -f -u chicken-coop.service
