@0x82ef20cff05af797;

struct Record {
    # Handle into the database, exists primarily to be saved/restored.

    blob @0 :Data;
    # Opaque blob used by the server.
}

interface Writable {
    # A writable version of the database

    create @0 (text :Data) -> (record :Record);
    # Create a new record in the database.

    replace @1 (record :Record, text :Data) -> (record :Record);
    # Replace an old record with a new one.

    delete @2 (record :Record) -> ();
    # Delet a record

    bundle @3 (records :List(Record)) -> (bundle :SealedBundle);
    # Create a bundle from a collection of records to send to a worker.

    struct Ref {
        # Ref type for saving/restoring. This ref is meant to be created by clients.
        
        token @0 :Text;
        # Authentication token
    }
}

interface SealedBundle {
    # A bundle of secrets that can be handed from the web node to the job node

    open @0 () -> (bundle :OpenedBundle);
    # Unlock a bundle, allowing it to be read.
    # TODO: Do a new version that does crypto stuff.

    struct Ref {
        # Ref type for saving/restoring. Meant to be passed around opaquely.

        blob @0 :Data;
        # Opaque blob used by the server.
    }
}

interface OpenedBundle {
    # A bundle of secrets that can be used by the job node to read the secrets

    read @0 (record :Record) -> (text :Data);
    # Read a record from the bundle
}

struct ObjRef {
    # Struct for saving/restoring objects. Some types are meant to be created by
    # the client. Others should only be created by the server.

    union {
        database @1 :Writable.Ref;
        # Writable database access. Meant to be synthesized by the client.

        bundle @2 :SealedBundle.Ref;
        # A secrets bundle. Should only be created by the server.
    }
}
