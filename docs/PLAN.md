# Current plan status

The numbered plan below is historical. Firmware experimentation is not required for the demonstrated stock-firmware workaround and is not currently authorized. See [current methodology](METHODOLOGY.md), [calibration](CALIBRATION.md), and [filters/DPI](FILTERS-AND-DPI.md). Historical paper budgets are exhausted or superseded; obtain a fresh allowance before hardware tests.

# Ordered tests

1. Preserve source baseline and read-only identity evidence on original.
2. Verify model, firmware and hardware using independent protocol responses.
3. Obtain exact stock image, checksum it and investigate restoration. Download availability does not prove restoration.
4. One normal B1-sequence USB print at density 3, using one 50 x 80 mm label. Record the precise failure stage and response. Budget 1.
5. One documented continuous-paper-mode trial if applicable. Restore label settings. Stop on unexpected feeding. Budget 1.
6. Offline firmware analysis: locate the error-20 path, RFID validation, density defaults, print-head protections and update logic. Build evidence for each change.
7. Offline patch tests: exact input hash, original bytes, instruction targets, memory ranges, integrity checks, rejection of unsupported/corrupted inputs, and reversal. No hardware success claims from these tests.
8. Present the exact candidate and recovery evidence before a firmware write. If recovery requirements are met, one sparse print at normal density. Budget 1.
9. Two-photo layout, text/date, reconnect and photobooth integration trials. Budget up to 4.
10. If firmware changed, verify actual stock restoration and original operation. Reserve 3 labels, including any original-paper comparison.

Total cap: ten physical test labels under the current authorization. Count jobs conservatively until actual paper consumption is confirmed. No unattended retry loop. Keep every outcome, including failures, in the log. Stop on abnormal heat, smell, motor/feed behaviour or unresolved printer errors.
