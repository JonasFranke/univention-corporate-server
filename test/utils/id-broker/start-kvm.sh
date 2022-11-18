#!/bin/bash

set -x
set -e

export KVM_BUILD_SERVER="${KVM_BUILD_SERVER:=ranarp.knut.univention.de}"
export HALT=false
export DOCKER=true
export UCS_ENV_IDBROKER_DOMAIN=broker.test
export UCS_ENV_TRAEGER1_DOMAIN=traeger1.test
export UCS_ENV_TRAEGER2_DOMAIN=traeger2.test
export KVM_KEYPAIR_PASSPHRASE=univention
export UCS_ENV_PASSWORD=univention
export UCS_TEST_RUN=false

# user specific instances "username_..."
if [ -n "$BUILD_USER_ID" ]; then
	export KVM_OWNER="$BUILD_USER_ID"
fi

exec ./utils/start-test.sh scenarios/autotest-247-ucsschool-id-broker.cfg
