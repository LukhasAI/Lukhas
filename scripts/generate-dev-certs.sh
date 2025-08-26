#!/bin/bash

# Generate development SSL certificates for HTTPS localhost
# Required for WebAuthn development

set -e

CERT_DIR="certs"
KEY_FILE="$CERT_DIR/localhost.key"
CERT_FILE="$CERT_DIR/localhost.crt"

# Create certs directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist
if [[ -f "$KEY_FILE" && -f "$CERT_FILE" ]]; then
    echo "✅ Development certificates already exist at:"
    echo "   Key:  $KEY_FILE"
    echo "   Cert: $CERT_FILE"
    exit 0
fi

echo "🔐 Generating development SSL certificates..."

# Generate private key
openssl genpkey \
    -algorithm RSA \
    -out "$KEY_FILE" \
    -pkcs8 \
    -outform PEM \
    2048

# Generate certificate signing request config
cat > "$CERT_DIR/localhost.conf" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Development
L = Localhost
O = LUKHAS AI Development
OU = Security Team
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Generate self-signed certificate
openssl req \
    -new \
    -x509 \
    -key "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 365 \
    -config "$CERT_DIR/localhost.conf" \
    -extensions v3_req

# Set appropriate permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

# Clean up config file
rm "$CERT_DIR/localhost.conf"

echo "✅ Development certificates generated successfully!"
echo "   Key:  $KEY_FILE"
echo "   Cert: $CERT_FILE"
echo ""
echo "⚠️  SECURITY WARNING:"
echo "   These are self-signed certificates for development only."
echo "   Your browser will show security warnings - this is expected."
echo "   Never use these certificates in production."
echo ""
echo "🔧 To trust the certificate in your system (optional):"
echo "   macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $CERT_FILE"
echo "   Linux: sudo cp $CERT_FILE /usr/local/share/ca-certificates/lukhas-dev.crt && sudo update-ca-certificates"
echo ""
echo "🌐 Next.js will automatically use these certificates when DEV_HTTPS_ENABLED=true"
