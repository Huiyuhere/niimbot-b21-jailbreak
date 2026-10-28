# B21 calibrated photobooth release — 28 October 2026

The owner accepted the physical Test L results ("they are perfect now") and requested production publication. This release promotes that same command order and the approved full-height layout. The exact number of labels in the final successful run was not recorded; this is owner-observed validation on the tested device/roll, not a long-run certification of every B21 or paper stock.

## Printing sequence

Tested device: B21 C2B model 775, hardware 40.10, stock firmware 40.36, Bluetooth, third-party 50 × 80 mm die-cut labels with approximately 6 mm backing gaps.

1. Connect, manually calibrate using `8E / 01`, require `8F / 01`, then have the operator confirm the gap at the tear edge. Reconnection invalidates that confirmation.
2. For each manual Print click, initialize a fresh B1 task at density 3 with label type 3 (continuous). This avoids the ordinary gap-mode RFID start path.
3. After PrintStart and before PageStart/image upload, send `23 / 01` (gap mode). Require `33 / 01`, read label type back as 1, and check a clean zero-page job status.
4. Upload the complete 384 × 640 raster with no extra vertical offset. Copies are submitted in the same task with matching total-page and copy counts.
5. Wait for the requested page count and 100% print/feed completion with no reported error, then require PrintEnd acknowledgement. The next new photo strip starts a new task using the same sequence.

The SDK does not reject a roll solely because `paperRfidSuccess` is false. Actual printer errors, disconnections, lid/paper failures and uncertain acknowledgements still stop the operation. There is no automatic retry or fallback to a different feed. Manual Recalibrate now can explicitly cancel a pending task and request positioning, without a lifetime test-count cap. A failed/ambiguous cancellation retains the pending state.

## Shared layout

| Part | Dimensions / position |
| --- | --- |
| Paper | 50 × 80 mm (400 × 640 design dots at 8 dots/mm) |
| Thermal head | 384 dots wide, centred on the paper |
| Three photo slots | 44 × 20 mm each; whole source image contained, no cropping/stretching |
| Top and side padding | 3 mm |
| Photo gaps | 0.5 mm each |
| Last photo → logo | 3 mm |
| Footer | 10 mm: logo about 11.9 × 4 mm, message/date about 1.5 mm visible ink height |
| Date → bottom | 3 mm |

Camera preview, saved images, QR export and thermal preview share these dimensions. Production has an empty editable message by default, with no Test L banner or test-parameter text. Experimental URL flags remain development-only.

## Lessons from earlier tests

- F's 586-row / 40-dot offset worked for the shorter 17 mm photos but could not contain the full requested footer with 20 mm photos.
- K2's 688-row continuous feed advanced 99 mm between corresponding photo tops on an 86 mm label pitch: 13 mm drift. Pause/resume prevented some idle errors but did not fix that advance.
- Increasing a continuous raster to fit artwork changed repeated feed. Shrinking/clipping artwork or adding a fixed per-job offset did not solve registration for the full layout.
- Ordinary gap-mode PrintStart hit WriteRfidFail (20). Test L changes when gap mode is selected, retaining the full artwork while using gap handling during printing. No firmware flash, RFID rewrite, USB motor command or SDK error suppression is used.

## Validation and operation

Focused tests cover separate new-photo jobs, multi-copy batches, untagged paper, command ordering, full raster dimensions, no retries on errors, pending-task recovery, reconnect calibration and shared footer/export geometry. Unit tests do not themselves establish physical alignment.

Keep one printer client connected. After deployment, permissions are specific to the website origin: select B21, calibrate once and confirm positioning. Retake and print new photos without recalibrating between successful strips. Recalibrate after reconnecting or manually moving/reloading the roll. Firmware/roll changes and long unattended runs remain outside the final owner-observed evidence.

## Implementation and offline evidence

- [Production driver](https://github.com/Huiyuhere/yourtypemixer/blob/main/photobooth/client/src/helpers/b21Driver.ts)
- [Command-sequence implementation](https://github.com/Huiyuhere/yourtypemixer/blob/main/photobooth/client/src/helpers/lateGapTest.ts)
- [Hash-locked, offline firmware probe](https://github.com/Huiyuhere/yourtypemixer/blob/main/photobooth/experiments/b21_late_gap_probe.py)
- [Chronological registration measurements](https://github.com/Huiyuhere/yourtypemixer/blob/main/docs/photobooth-print-registration.md)

The offline probe validates handler ordering on the exact stock image. Its hardware-ready stubs do not prove motor travel or physical alignment; the owner's subsequent Test L result supplies physical acceptance. Firmware binaries, private photographs and device-specific logs are not published.
