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


Transport
---------

________ over TLS


Scaling
-------

TODO
