# Recovery evidence and limits

The photobooth software snapshot dated 2026-10-26 18:20 Singapore time contains 1,223 verified source files, Git bundle, dependencies and build output. It was restored into a separate folder and its source hashes checked. Base source commit: e004d7b755aad1e4aa861d9b30263a545d38896f. It is a Mac software backup only.

Exact installed printer revision is confirmed by USB information and heartbeat: B21 C2B 775, HW 40.10, FW 40.36. Official API supplied a stock 40.36 image URL; see evidence manifests. No printer flash has been performed.

Still unproven: acceptance of an identical-version stock update, downgrade behaviour, interrupted-update recovery, factory-data preservation, and recovery if patched application code cannot start. No complete bootloader/factory-data dump exists.

[B21 C2B recovery documentation](https://printers.niim.blue/hardware/NIIMBOT-B21_C2B/niimbot-b21-c2b-unbrick/) describes a destructive recovery route that loses factory data. That route violates the owner's no-erasing requirement and is excluded. The Pro project's recovery assertions must not be assumed to apply here.

Firmware writes remain gated on credible restoration evidence. No mass erase, read-protection removal, factory reset or guessed memory writes. Preserve local stock bytes and manifest permanently; never overwrite the original file with a patched image.
