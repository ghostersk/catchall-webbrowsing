#!/bin/bash
# CA Authority custom values:
CA_NAME="self.certificate" # Use your own domain name
CA_COUNTRY_Code="GB"
ca_stateOrProvinceName=England
ca_localityName="Yorkshire"
ca_orgUnitName="IT"
ca_comp_Name="Home Industry SelfSigned"

# your own values for certificate
NAME="flower.com" # Use your own domain name
COUNTRY_Code="GB"
stateOrProvinceName=England
localityName="Yorkshire"
organizationalUnitName="IT"
csr_email="myemail@$NAME"
company_Name="Adventures"

# Also edit Suj Alt names for the certificate down 2x

# folders
cert_dir="ssl"
ca_dir='ssl/myca'
if [ ! -d "$cert_dir" ]; then
    mkdir $cert_dir
fi

if [ ! -d "$ca_dir" ]; then
    mkdir $ca_dir
fi


# Check if CA certificate and key files exist
if [[ ! -f "$ca_dir/ca-cert.pem" ]]  || [[ ! -f "$ca_dir/ca-key.pem" ]]; then
    echo "CA certificate or key file not found. Creating new CA!!!"
    # Generate CA-Private Key
    openssl genrsa 2048 > "$ca_dir/ca-key.pem"
    # Generate CA certificate
    openssl req -new -x509 -nodes -days 365000 \
        -key "$ca_dir/ca-key.pem" \
        -out "$ca_dir/ca-cert.pem" \
        -subj "/C=$CA_COUNTRY_Code/ST=$ca_stateOrProvinceName/L=$ca_localityName/O=$ca_comp_Name/OU=$ca_orgUnitName/CN=$CA_NAME"
else
   echo "CA certificate and key file found. Using existing Certificate Authority!"
fi

# Server Key and request
# bellow you can set alt_names for hosname and IP you want to use with this cert
openssl req -newkey rsa:2048 -nodes -days 365000 \
   -keyout "$cert_dir/key.pem" \
   -out "$cert_dir/server-req.pem" \
   -subj "/C=$COUNTRY_Code/ST=$stateOrProvinceName/L=$localityName/O=$company_Name/OU=$organizationalUnitName/CN=$NAME/emailAddress=$csr_email" \
   -config <(cat <<-EOF
[req]
req_extensions = v3_req

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.${NAME}
DNS.2 = piserver.local
DNS.3 = localhost
IP.1 = 127.0.0.1
IP.2 = 10.100.112.254
IP.3 = 10.99.197.231
EOF
)

# Generate X509 Certificate for the server
openssl x509 -req -days 365000 -set_serial 01 \
   -in "$cert_dir/server-req.pem" \
   -out "$cert_dir/cert.pem" \
   -CA "$ca_dir/ca-cert.pem" \
   -CAkey "$ca_dir/ca-key.pem" \
   -extfile <(echo "subjectAltName = DNS:*.${NAME}, DNS:piserver.local, DNS:localhost, IP:127.0.0.1, IP:10.100.112.254, IP:10.99.197.231")
# Testing certs:
openssl verify -CAfile "$ca_dir/ca-cert.pem" \
   "$ca_dir/ca-cert.pem" \
   "$cert_dir/cert.pem"

# To add them to the CA approved list in linux:
# sudo cp $ca_dir/ca-cert.pem /usr/local/share/ca-certificates/ca-cert001.crt
# sudo update-ca-certificates
