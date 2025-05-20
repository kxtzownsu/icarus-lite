#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
SCRIPT_DIR=${SCRIPT_DIR:-"."}
VERSION=1.0.0

cat <<EOF
httpmitm - "rewritten" by kxtz!
v$VERSION-g$(git log -n 1 --pretty=format:%h -- $SCRIPT_DIR)
--------------------------------
EOF

CERT_PATH="${SCRIPT_DIR}/certs/google.com.pem"
CA_PATH="${SCRIPT_DIR}/myCA"

if [[ ! -f "$CA_PATH.pem" || ! -f "$CA_PATH.key" ]]; then
    echo "CA certificates missing!"
    echo "checked path: $CA_PATH.(pem/key)"
    exit 1
fi

if [[ ! -f "$CERT_PATH" ]]; then
    echo "m.google.com certificate missing!"
    echo "checked path: $CERT_PATH"
    exit 1
fi

EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_PATH" | cut -d= -f2)
EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_TIMESTAMP=$(date +%s)

if [[ "$EXPIRY_TIMESTAMP" -lt "$CURRENT_TIMESTAMP" ]]; then
    echo "Certificate expired. Regenerating..."
    bash "${SCRIPT_DIR}/generate_certs.sh"
    mv "${SCRIPT_DIR}/google.com.pem" "${SCRIPT_DIR}/certs/google.com.pem"
    mv "${SCRIPT_DIR}/google.com.key" "${SCRIPT_DIR}/certs/google.com.key"
    mv "${SCRIPT_DIR}/extfile" "${SCRIPT_DIR}/certs"
    mv "${SCRIPT_DIR}/in.csr" "${SCRIPT_DIR}/certs"
fi

cd $SCRIPT_DIR
if [ ! -e ".venv" ]
then
	python3 -m venv .venv
fi
source $SCRIPT_DIR/.venv/bin/activate
pip3 install requests protobuf
python3 main.py
