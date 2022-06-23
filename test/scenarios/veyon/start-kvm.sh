#!/bin/bash

set -x
set -e

cfg_file="$(mktemp)"
export UCS_ENV_VEYON_WINDOWS_HOST="${UCS_ENV_VEYON_WINDOWS_HOST:=3}"
export KVM_BUILD_SERVER="${KVM_BUILD_SERVER:=ranarp.knut.univention.de}"
export HALT=false

# extra label for instances names so that the instances
# are user specific
UCS_ENV_MY_USERNAME="$USER"
if [ -n "$BUILD_URL" ]; then
	# -> if started via jenkins "...-username"
	my_name="$(curl -k -s "$BUILD_URL/api/json" | awk -F '"userId":"' '{print $2}'| awk -F '"' '{print $1}')"
	export UCS_ENV_MY_USERNAME="${my_name}"
fi
export UCS_ENV_MY_USERNAME="$UCS_ENV_MY_USERNAME"

./scenarios/veyon/create_veyon_cfg.py  \
	-w "$UCS_ENV_VEYON_WINDOWS_HOST" \
	-v kvm > "$cfg_file"
cat "$cfg_file"
exec ./utils/start-test.sh "$cfg_file"
