Sign pkpass
------------

Check old signature:

	openssl pkcs7 -in signature -inform DER -noout -print_certs
	subject=C = US, O = Apple Inc., OU = Apple Worldwide Developer Relations, CN = Apple Worldwide Developer Relations Certification Authority

	issuer=C = US, O = Apple Inc., OU = Apple Certification Authority, CN = Apple Root CA


	subject=UID = pass.com.urboapp.urbo, CN = Pass Type ID: pass.com.urboapp.urbo, OU = WFH24T74H5, O = UPASS OOD, C = BG

	issuer=CN = Apple Worldwide Developer Relations Certification Authority, OU = G4, O = Apple Inc., C = US

Check pass.json:

	"passTypeIdentifier" : "pass.com.urboapp.urbo",

Generate self-signed cert:

	openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj "/UID=pass.com.urboapp.urbo/CN=Pass Type ID: pass.com.urboapp.urbo/OU=WFH24T74H5/O=UPASS OOD/C=BG"

Sign pkpass:

	openssl smime -binary -sign -signer ../pkpass/cert.pem -inkey ../pkpass/key.pem -in manifest.json -out signature -outform DER

and zip:

	zip ../t3.pkpass *
