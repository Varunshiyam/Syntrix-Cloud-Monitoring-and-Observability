#!/bin/bash
TOKEN=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://syntrix-gateway-541833001986.asia-south1.run.app")
curl -s -H "Authorization: Bearer $TOKEN" https://syntrix-gateway-541833001986.asia-south1.run.app/health
