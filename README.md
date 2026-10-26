# B21 C2B third-party paper investigation

Target: NIIMBOT B21 C2B, model 775, hardware 40.10, firmware 40.36, 50 x 80 mm third-party labels. Success requires a physically verified print through the photobooth and a demonstrated return to stock if firmware is modified. A working jailbreak has NOT been produced.

## Branches

- `original`: frozen diagnostic baseline, stock image manifest, recovery limits and prior results.
- `flash`: experiments, analysis tools and chronological results. Its name does not mean firmware has been flashed.

No firmware changes have been made. Factory data has not been backed up. Official firmware files are local and ignored; their source and checksums are recorded for retrieval. Do not treat an official update image as a complete device backup.

## Confirmed constraints

Owner permits up to ten labels, one job at a time. Opening the case is allowed. Soldering, erasing, factory reset and removal of chip protection are excluded. Preserve original heat/current protections. Stop before firmware writes if restoration cannot be established.

## Reproduce read-only identity check

Use Python with `requirements.txt` installed in an isolated environment:

```sh
python -m unittest discover -s tests -v
python tools/b21_probe.py --port /dev/cu.usbmodem101 --output evidence/new-probe.json
```

Port names may change. Close other software holding that port first. The probe only allows connection negotiation, selected identity/settings reads, and status reads. It never requests the serial number, Bluetooth address or RFID identifier. Output files are never overwritten.

The corrected USB baseline cross-checks version fields against heartbeat identity. The first baseline JSON is retained as evidence of a decoder error; its 102.76 / 102.50 interpreted values are invalid. Read `2026-10-26-usb-baseline-corrected.json` for the verified 40.36 / 40.10 values. Battery level 4 maps to 100% in this protocol.

## Method and references

[B21 Pro reference](https://github.com/doctormord/Niimbot-B21-Pro-Jailbreak): use its approach to tracing RFID validation, absent-tag density defaults, and image integrity. Locate B21-specific instructions and structures independently. Pro addresses, values and recovery claims are not transferable without evidence.

[Protocol and firmware documentation](https://printers.niim.blue/) and [NIIMBLUE library](https://github.com/MultiMote/niimbluelib) inform the read-only packet probe. [Stock firmware API](https://printers.niim.blue/other/niimbot-cloud/) provides model/version metadata.

See [test plan](docs/PLAN.md), [experiment log](docs/EXPERIMENTS.md), and [recovery limits](docs/RECOVERY.md).
