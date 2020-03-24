ShushDB
=======

ShushDB is a scalable secrets store (key-value database) made for Go Build It. It is based on having Writers (web servers that can write secrets) and Readers (job servers that can read secrets). It makes use of TPMs and HSMs to secure and authenticate data.

Secrets are identified by an opaque string ID. There is no enumeration. It is expected that the application will store the secret identifier in a conventional database.

Supported operations:
* Create/Update a secret
* Bundle secrets (create a token for the job server)
* Receive bundle

Modes of authentication:
* Writer: Global keypair
* Reader: Per-node cryptographic authentication combined with bundle token

Authorizations:
* Writer: Can write secrets and create bundles
* Reader: Can receive bundles

Note that while a Writer can create a bundle, the resulting token is useless without the Reader's per-node key.

In addition, the secrets themselves are encrypted in transit:

A Writer encrypts the secret with the global keypair and sends it to the shush server. The shush server stores until a Reader retreives it, where it is re-encrypted in an enclave (HSM) to the Reader's individual keypair and sent to it.

There is a lot of use of secure enclaves, preferably in dedicated hardware (HSMs, TPMs, etc):

* Shush Servers use an enclave to re-encrypt secrets from the global key to the Reader's key
* Readers use an enclave to sign the bundle token (cryptographic authentication) and decrypt the bundle

Writers do not use an enclave--they are expected to take secrets in the clear, and are meant to run in a variety of circumstances (serverless, heroku, containers, etc).

Key management (PKI)
--------------------

* Writers: Hold the global public key
* Shush Servers: Hold the global private key and copies of each Reader's public key
* Readers: Hold an individual private key

(TODO: Using a CA would mean that Shush Servers only need to be configured with the signing key, not each Reader's key. But using CAs. And using TLS certificates.)

Transport
---------

HTTP over TLS

Routes:

* `GET /`: no-op, returns a `204 No Conent`, no authentication is performed (TODO: Authentication debug)
* `POST /`: Creates a new secret and has the server assign an ID, returns a `201 Created` with a `Location` header
* `PUT /<secret id>`: Writes a secret, returning a `202 Accepted` (Future: `409 Conflict`)
* `GET /<secret id>`: Gets a secret
* `POST /b`: Creates a bundle. The request body should be a JSON list of strings (`Content-Type: application/x.bundle+json`) or newline-separated list (`Content-Type: application/x.bundle`). The response will be an `text/plain` with the bundle token.
* `GET /b`: Gets a bundle. Returns a `application/x.bundle` or `application/x.bundle+json` with the list of secrets that are in the bundle.

Secret bodies may be either raw bytes (`Content-Type: application/x.secret`) or base64 (`Content-Type: application/x.secret+base64`).

All endpoints may issue a `403 Forbidden` if the authentication token is invalid or expired or a `404 Not Found` or `405 Method Not Allowed` if authorization fails.

Authentication is provided by opaque token. Writers use a globally-configured, long-lived token. Readers use the bundle token.

Scaling
-------

TODO
