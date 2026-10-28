> Current update (28 October): [owner-accepted registered-gap printing](REGISTERED-GAP-PRINTING.md) supersedes the earlier continuous-mode layout and unresolved full-height drift notes below. Historical measurements are retained unchanged.

# Stock-firmware printing methodology — 26 October 2026

## Scope and evidence

Tested unit: B21 C2B model 775, hardware 40.10, firmware 40.36. Third-party die-cut labels measured 50 × 80 mm with approximately 6 mm gaps (86 mm pitch). These results are specific to this device/stock. B21 Pro model 785 firmware, offsets and sensor assumptions are not transferable.

No firmware flashing, reset, RFID/tag writing or hardware modification was performed. A local software snapshot is not a complete printer backup. Keep original recovery restrictions in RECOVERY.md.

Evidence has three levels: transmitted command/response; device-reported completion; owner-observed physical output. Only the last establishes actual printing and positioning. Acknowledgement alone never establishes calibration. Raw later test logs remain in the separate local photobooth checkout, not this repository; this document summarizes them without publishing photos or private identifiers.

## Printing sequence

1. Close competing NIIMBOT/Bluetooth/USB clients. Read model, versions, density, label type and heartbeat paper/lid state.
2. Standard gap-mode job start (type 1) previously returned printer error 0xDB / payload 0x14, decoded as WriteRfidFail (20). Paper-present can be true while RFID recognition is false.
3. On this stock firmware, continuous mode (type 3) allowed the normal B1-style print job to run with the third-party roll. Do not describe this as generic RFID disabling.
4. Send one page, validate completion/status, end the job, restore gap mode and read back. If timeout or ambiguous completion occurs, inspect the physical label before any retry.
5. The tested production raster is 384 × 576 dots, about 48 × 72 mm. Observed cleanup feed is approximately 14 mm, so total advance can approach the 86 mm pitch. This is an empirical model, not a configurable or universal hardware constant.

## Controlled testing

Change one variable at a time and keep source photos, physical size and paper constant. Log settings, exact frames, errors, physical measurements and consumed labels including blanks. Compare upper/lower reference marks to distinguish scale from translation. Compare consecutive prints to detect drift, and reload/restart separately to test recovery. Stop at the explicit per-session paper budget; historical allowances do not authorize new tests.

Approved current experiments remain in the separate photobooth checkout. Diagnostic tools on this branch reflect earlier work; do not assume their old flags implement the later positioning procedure. See the linked photobooth source for that harness.

## Integration source

[Photobooth release 428bbf4](https://github.com/Huiyuhere/yourtypemixer/commit/428bbf4) contains operating/deployment instructions, the bounded USB feedback harness, default style C, three-photo printing, original-versus-dotted preview, connection UI and best-effort cancellation. Publication does not mean live deployment. Calibration is not automatically invoked by the public Print button.
