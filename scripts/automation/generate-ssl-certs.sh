#!/bin/bash
if [ ! -f ssl/nginx-selfsigned.crt ]; then
    mkdir -p ssl
    openssl req -x5яй9 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/nginx-selfsigned.key \
        -out ssl/nginx-selfsigned.crt \
        -subj "/C=US/ST=California/L=San Francisco/O=LUKHAS AI/CN=localhost"
    echo "✅ Self-signed SSL certificate generated"
fi
