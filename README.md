# B21 C2B third-party paper investigation

Target: NIIMBOT B21 C2B, model 775, hardware 40.10, firmware 40.36, third-party 50 × 80 mm labels with approximately 6 mm gaps.

**Current outcome, 28 October 2026:** the owner accepted Test L physical output on the tested third-party roll and requested its release. Start each B1 print job in continuous mode, then select gap mode **after PrintStart and before photo upload**. This preserves the full three 44 × 20 mm photos and Type footer on an 80 mm label. Firmware remains unchanged; this is a command-sequence workaround.

See [registered-gap printing](docs/REGISTERED-GAP-PRINTING.md) for the exact order, dimensions, prior drift measurements and validation limits. The final successful run's exact count was not supplied. Earlier continuous-feed and ordinary gap-start failures remain documented; they are not the released profile.

## Current documentation

- [Accepted registered-gap print sequence](docs/REGISTERED-GAP-PRINTING.md)
- [Methodology and evidence standards](docs/METHODOLOGY.md)
- [Calibration, reload recovery and margin limits](docs/CALIBRATION.md)
- [Style C filters, density and DPI](docs/FILTERS-AND-DPI.md)
- [Photobooth source and deployment instructions](https://github.com/Huiyuhere/yourtypemixer/blob/main/docs/photobooth-calibrated-release.md)

## Branches

- `original`: frozen diagnostic baseline, stock image manifest, recovery limits and prior results.
- `flash`: experiments, analysis tools and chronological results. Its name does not mean firmware has been flashed.

No firmware changes have been made. Factory data has not been backed up. Official firmware files are local and ignored; their source and checksums are recorded for retrieval. Do not treat an official update image as a complete device backup.

## Confirmed constraints

Earlier label allowances were session-specific and are not standing authorization. Obtain a fresh explicit budget before hardware tests; count blank feeds as well as printed labels, and test one operation at a time. Current scope excludes firmware changes, factory reset and hardware modification. Preserve the working driver and exact request/reply/error/physical-result records.

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
