# B21 registered-gap printing: method, diagnosis and calibration

Updated 28 October 2026. **Accepted profile: continuous-mode job start, then gap mode before uploading the page.** This preserves the full photo strip and was accepted after physical testing on the configuration below. The exact final-run label count was not recorded; this is operator-observed acceptance, not a long-run certification of all printers or rolls.

This document uses descriptive experiment names, with historical letter identifiers only for cross-reference. Personal names, private photographs, Bluetooth addresses, printer serial numbers, local user paths and raw device logs are excluded. Public source links identify the implementation, not the operator.

## Scope and accepted result

| Item | Tested configuration |
| --- | --- |
| Printer | NIIMBOT B21 C2B, model 775 |
| Hardware / firmware | 40.10 / stock 40.36 |
| Transport | Bluetooth |
| SDK | `@mmote/niimbluelib` 0.47.1 |
| Stock | Third-party 50 × 80 mm die-cut labels; approximately 6 mm backing gap |
| Measured label pitch | 86 mm, top of one sticker to top of the next |
| Raster | 384 × 640 dots; no added vertical offset |
| Density | 3 |
| Job lifecycle | Fresh task for every manual print request; normal completion before the next task |

Success means a first strip after calibration, another strip with **new photos and a new job**, and a multi-copy batch all remain registered. Photos and footer must stay on their own sticker, with no accumulating displacement and no unintended extra labels. Keeping the same photos or resetting calibration between every strip would not demonstrate this requirement.

The accepted method uses existing firmware commands. It does not flash firmware, write an RFID tag, use USB motor control, or suppress printer errors. The implementation and acceptance record are pinned in [R1–R4](#references).

## Reproducible printing method

Hex notation below is `command / payload`, not a complete Bluetooth packet. Packet framing and checksums remain the SDK's responsibility.

1. **Establish position.** Connect one printer client, select the calibration path and send `8E / 01`. Require response `8F / 01`, then ask the operator to confirm the gap at the tear edge. Acknowledgement proves acceptance of a command, not physical registration. Reconnect, reload or manually move the roll: invalidate that confirmation and calibrate again.
2. **Start a fresh task in continuous mode.** Configure density 3, label type 3, and the intended number of copies. Start the B1 task. Here “B1” is the SDK task class used for this B21, not a change of printer model.
3. **Switch modes before the page starts.** After PrintStart has succeeded, but before PageStart or raster upload, send `23 / 01`. Require `33 / 01`, read label type back as 1, and verify a clean zero-page task status. If any check fails, do not upload the image.
4. **Submit the full page.** Use 384 × 640 dots, offset zero. Page dimensions, task total pages and copy counts must agree. Do not append the physical backing gap as additional artwork rows.
5. **Confirm completion.** Poll status for exactly the requested page count, 100% print and 100% feed, with no device error. Require PrintEnd acknowledgement before marking the task complete. Unexpected extra pages, unknown status, disconnect or timeout stop the operation.
6. **Allow the next manual request.** Retake/new photos → Print creates another fresh task using the same sequence. Do not recalibrate between successful comparison strips. A batch is a real multi-copy task, not repeated automatic retry calls.

The relevant packet order is:

```text
SetDensity → SetLabelType(3) → PrintStart
           → SetLabelType(1) → readback/status checks
           → PageStart → SetPageSize → raster → PageEnd
           → completion polling → PrintEnd
```

The installed-SDK test checks the initial command order `21 → 23/03 → 01 → 23/01 → 03 → 13` and the full page data. [R2, R5]

### Third-party paper and recovery

`paperRfidSuccess:false` alone is not a software admission blocker in this path. Paper-present and lid checks remain active. Actual firmware errors—including RFID errors—are still reported and stop the operation. There is no automatic fallback to continuous printing and no automatic reprint after an uncertain result.

A manually confirmed **Recalibrate now** can cancel a pending task, require its acknowledgement, and then send one positioning request. It must not demand a separate “End test session” click first. If cancellation is ambiguous, retain the pending state instead of assuming the printer is idle. Concurrent operations are blocked, but manual confirmed calibration has no lifetime test-count limit. A cancelled Bluetooth chooser is a connection failure, not a calibration-command failure. [R1]

## Artwork dimensions and why the entire footer fits

Use the renderer's calibrated convention of **8 dots/mm** (203.2 nominal dpi). The manufacturer manual lists 203 dpi; do not mix `203 / 25.4` and 8 within one layout. The accepted raster was tested at 8 dots/mm. [R6]

| Element | Physical position / size | Design dots |
| --- | --- | --- |
| Label | 50 × 80 mm | 400 × 640 |
| Printable head width | 48 mm, centred; omit only the outer 1 mm on each side of the design | 384; design x = 8…392 |
| Photo 1 | x = 3 mm, y = 3…23 mm; 44 × 20 mm | x = 24, y = 24…184; 352 × 160 |
| Photo 2 | y = 23.5…43.5 mm | y = 188…348 |
| Photo 3 | y = 44…64 mm | y = 352…512 |
| Photo gaps | 0.5 mm each | 4 each |
| Last photo → visible logo | 3 mm | 24 |
| Footer block | y = 67…77 mm; 10 mm high | y = 536…616; 80 high |
| Logo | About 11.9 × 4 mm | About 95 × 32 |
| Message / date | About 1.5 mm visible ink height each | About 12 each |
| Footer internal gaps | 1.5 mm each when all three items are present | 12 each |
| Date → bottom edge | 3 mm | 24 |

Height check: `3 + (3 × 20) + (2 × 0.5) + 3 + 10 + 3 = 80 mm`.

Camera preview, colour export/QR image and thermal preview use the same geometry. Each photo is contained in its slot without stretching or cropping; mismatched source aspect ratios can leave side margins. Use visible logo/text bounds when positioning the footer, rather than transparent image padding or font line-box height. The dimensions above describe the full logo + message + date case; hidden items are handled by the shared layout. [R7]

## Investigation methodology

### Separate the three possible errors

1. **Scale:** measure a printed frame's height. A correct 20 mm frame with a displaced top edge points away from image scaling.
2. **Initial origin:** measure top-edge → first-frame distance immediately after calibration. A constant error on every label may be an origin problem.
3. **Repeated advance:** compare corresponding marks on consecutive prints without reconnecting, recalibrating or pulling the paper. An increasing error is registration/pitch drift; moving the whole image by a constant amount cannot fix it.

Measure **A**, sticker top → next sticker top, including the gap. Measure **B**, first-photo top on one strip → first-photo top on the next strip. Use the same physical reference on both strips, regardless of photo content. Next-sticker protrusion is optional: it is harder to measure and does not by itself establish where the next image will begin.

The failed full-height continuous experiment measured:

```text
A = 86 mm label pitch
B = 99 mm photo-to-photo pitch
per-transition drift = B − A = +13 mm
```

The second strip began about 16 mm from its sticker's top rather than 3 mm, while the date spilled about 4 mm onto the next sticker. Frame height stayed correct. These observations support excess advance, not a shrinking-roll-radius explanation. The mechanical cause of every individual movement was not isolated. [R4]

### Change one variable and preserve evidence

Record an anonymous run ID, profile name, firmware/hardware version, stock height/gap, density, raster rows, offset, task mode and copies. Log outgoing command order, acknowledgements, status/error bytes and completion. Persist the log across refreshes; exclude photo pixels and unique device identifiers from published records.

Compare separate manual jobs with new images as well as a batch. Keep settings and connection unchanged during each comparison. A sparse reference-line probe can isolate feed behaviour, but success with it does not validate a larger three-photo layout. Offline handler execution and mocked transport tests establish software behaviour; neither measures paper travel.

## Experiment names, observations and lessons

Historical identifiers are lookup keys, not recommended settings. Some identifiers covered more than one artwork revision; those are distinguished below. Earlier notebooks use “pending” at the time each candidate was introduced; later observations supersede those statuses. [R4]

| Descriptive experiment (historical ID) | Main change | Observed result / lesson |
| --- | --- | --- |
| Continuous baseline and retained-mode jobs (baseline, B) | About 687 rows, +40-dot offset; retain continuous mode between jobs | Second-strip top moved to 16–17 mm and content spilled. Recalibration made a first label look correct but did not establish repeated registration. |
| New-image manual jobs (C) | Explicit one-label click and new run ID; same transport settings | Second top still 17 mm. Changing the UI/job identifier was not a feed fix. |
| Short sparse feed probe (D) | 576 rows, +40 offset; one frame and a 50 mm reference mark | Reference positions 50, 49, 47.5 mm: accumulating upward drift. |
| Adjusted sparse feed probe (E) | 586 rows, +40 offset | Operator reported four separate singles and a two-label batch aligned. This evidence applies to the sparse probe. |
| Footer probe (early F) | Add branded footer to sparse artwork | Still a sparse probe; not three full photo frames. |
| Compact three-frame fit (fitted F) | Three 44 × 17 mm frames; 544 artwork rows + 40 offset = 584 within 586 | Operator confirmed separate and batch alignment. Useful empirical baseline, but did not meet the later 44 × 20 mm/full-footer requirement. |
| Taller continuous raster (G) | 648 rows, +40 offset, larger footer | Second-strip top about 11 mm: roughly +8 mm drift. Extra raster rows were not free printable space. |
| Compact footer (H) | Return to 586 rows/+40 with 20 mm frames and a very small footer | Geometric fit left the footer too small and too much unused label below it. Not accepted as the requested layout. |
| Gap mode before job start (I) | Full 640-row layout, zero offset, density 2, start directly in gap mode | `WriteRfidFail (20)` on the loaded third-party stock, including after recalibration. |
| Non-final page then cancel (J) | 688 rows/+40; cancel unused remainder instead of ordinary completion | First strip had 3 mm top/bottom and 20 mm frames, but about 11 mm of the next sticker protruded. Second-print alignment was not tested in that observation; its protocol log was lost on refresh. |
| Keep job open (K) | Avoid finishing between manual uploads | First strip looked good; subsequent flow encountered session/recalibration trouble and `PaperOutException (8)` despite loaded stock. |
| Pause and resume open job (K2) | Pause after page; upload next photos before resuming | Idle-state handling did not solve feed. Only Retake → Print produced the measured 86 mm versus 99 mm pitches and spillover. |
| Gap mode after job start (L, accepted) | Start type 3, then type 1 before page; 640 rows, zero offset, fresh task per click | Operator accepted physical output and requested release with the full 20 mm frames and footer. Exact final-run count was not recorded. |

### What the compact baseline taught us

For continuous trials, `688 − 586 = 102 dots ≈ 12.75 mm`, close to the measured 13 mm excess. Similarly, `648 − 586 = 62 dots = 7.75 mm`, close to the taller-raster trial's approximately 8 mm shift. This is a useful correlation, not a universally proven additive motor-overrun constant.

The 586-row raster with +40 offset only leaves `546 / 8 = 68.25 mm` for artwork. The approved date extends to 77 mm: its lower ink boundary plus that offset would require `616 + 40 = 656` rows. Clipping only blank bottom rows cannot recover that missing footer space. Nor is it valid to declare a 586-row page and secretly upload more rows.

The accepted method resolves this by changing the **feed mode and command timing**, not by shrinking the photos or hiding overflow.

## Failure diagnosis and corrective actions

| Symptom | Evidence-based diagnosis | Corrective action / limitation |
| --- | --- | --- |
| First label aligned; later labels move down or spill | Repeated advance differs from actual label pitch; correct frame height rules against simple scale error | Measure A/B. Use the accepted registered-gap sequence for this tested configuration; do not compensate by repeatedly recalibrating or adding a fixed offset. |
| Every label equally clipped at the top | Initial origin, stale position or wrong offset is a candidate; drift has not yet been established | Check connection/calibration state and profile. Accepted gap profile uses zero added offset. Verify first and subsequent labels before changing geometry. |
| Footer missing at 586 rows/+40 | Ink extends beyond the transmitted raster; not merely a blank margin | Check visible ink bounds against raster bounds. Full 80 mm layout uses 640 rows with the accepted gap sequence. |
| `WriteRfidFail (20)` with paper loaded | Actual firmware error during ordinary gap-mode start; not evidence that paper is absent | Start in continuous mode, then switch to gap mode before PageStart as verified here. Do not ignore the error or loop calibration. If it recurs, stop and inspect the trace. |
| `PaperOutException (8)` on the next open-job upload | Observed with the open-job experiment; a task/state issue is a candidate, not proof of an empty roll | Inspect real paper/lid state, preserve logs and recover the pending task explicitly. Use completed independent jobs for normal printing. Do not blanket-ignore error 8. |
| “Feature not supported” while reading capabilities | Optional query may be unsupported by the firmware/protocol | Report unavailable metadata; do not make that optional query a calibration prerequisite. Still enforce known model/firmware checks. |
| Calibration blocked after earlier attempts | Application lifetime counter or pending-task state can block a valid manual action | Remove lifetime count caps for manually confirmed actions; cancel pending task with acknowledgement before positioning; retain mutual exclusion while an operation is active. |
| “Connected” UI but cannot calibrate | Stale connection state or cancelled chooser can occur before a positioning packet is sent | Invalidate calibration on disconnect; reconnect through the chooser and confirm physical position afterward. Do not count a cancelled chooser as a calibration movement. |
| SDK reports success but alignment is wrong | Acknowledgement/completion does not measure geometry | Require operator measurements and record physical outcome separately from protocol completion. |

There is no verified Bluetooth reverse-feed workaround for this exact firmware in this investigation. A generic command listed for another model, or a USB-only factory motor handler, is not evidence that the B21 Bluetooth dispatcher accepts it. [R3, R8]

## Why the accepted command order is plausible

The offline investigation used stock image SHA-256:

```text
25c9ba099339b482b6ba1b515fbf9bdfb32969abf38d6712be39c7c4b294d1a0
```

For that image, handler analysis found that label type 3 at PrintStart skips the RFID-start routine called by ordinary type-1 starts. The label-type setter can then accept type 1 while the motor is idle and the transport owner matches. The motor controller consults the live paper type, providing a route to sensor-based handling after the start check.

The hash-locked probe exercises continuous select → PrintStart → gap select, intercepts responses and counts RFID-start calls. It substitutes ready hardware conditions; it does **not** emulate the real paper sensor, motor or label travel. The ordinary-gap control calls the RFID-start routine; the candidate does not. This motivated the physical test. Operator acceptance supplies the physical evidence; the probe alone would not. Addresses and behaviour are specific to this firmware image. [R3]

## Suggested calibration for other label heights

**Only 50 × 80 mm is accepted here.** The current implementation fixes the profile at 640 rows; changing the preview height alone does not create another calibrated size. The following is an engineering/test procedure, not a list of certified media sizes.

Keep width at 50 mm and the same 384-dot head mapping for this proposal. For a supported physical label height `H` and measured backing gap `G`:

```text
artwork/page rows = round(8 × H)
physical target pitch = H + G
extra raster offset = 0 initially, using the accepted gap-after-start method
```

In registered-gap mode, page rows describe the **label**, not label-plus-gap. Do not add `8 × G`, the old 40-dot offset, or an assumed 13 mm correction. The sensor registration must be tested for the new stock. Check actual printer/firmware media limits before implementing any proposed size.

### Layout calculation

With three photo slots, 3 mm top/bottom margins, two 0.5 mm photo gaps, 3 mm before the logo and a 10 mm footer:

```text
photo height = (H − 3 − 3 − 1 − 3 − 10) / 3 = (H − 20) / 3
```

| Proposed label height | Page rows at 8 dots/mm | Photo height if all other dimensions stay fixed | Status |
| --- | --- | --- | --- |
| 60 mm | 480 | About 13.33 mm | Geometry example only; media support and registration unverified |
| 70 mm | 560 | About 16.67 mm | Geometry example only; media support and registration unverified |
| 80 mm | 640 | 20 mm | Accepted configuration |
| 90 mm | 720 | About 23.33 mm | Geometry example only; media support and registration unverified |

If photos must stay **44 × 20 mm**, the complete stated layout requires 80 mm. Shorter paper requires smaller photos, fewer frames or a different footer/margin specification. Taller paper leaves extra space to allocate deliberately; changing label height must not silently stretch the photos.

Calculate all boundaries in integer dots and distribute any rounding remainder across the three slots; avoid independently rounding repeated dimensions until the sum exceeds the page. Validate visible ink bounds, preview, QR/export, thermal raster, driver page-size checks and test expectations together. Keep a proposed height behind a local test profile until physically accepted.

### Verification for a new height or roll

1. Measure actual label height, gap and pitch. Record model, firmware, stock and profile; preserve logs without personal/device identifiers.
2. Update the page rows and shared geometry together. Keep the accepted command order and start with zero added offset. Check every inked row fits without stretching or clipping.
3. Calibrate once and physically confirm positioning. Manually print one label; measure top margin, frame height and footer/bottom clearance.
4. Take new photos and manually print again without reconnecting or recalibrating. Repeat to obtain at least three separate jobs, if the preceding measurements remain acceptable. Compare A and B and look for a trend, not just one rounded ruler reading.
5. Test a two-copy batch. Then test reconnect → calibrate → first print separately as a recovery check, rather than recalibrating within the drift comparison.
6. Stop on spillover, clipping, an unexpected label, status error or increasing displacement. Save the trace and measurements before changing a variable. Each print is manually triggered; no automatic retry follows a failure.

A suggested initial ruler tolerance is ±1 mm for margins and correspondence to the physical pitch, with **no increasing trend**, no spillover and the full footer visible. This is a proposed acceptance criterion, not a manufacturer accuracy specification. Use finer measurement if a small cumulative shift is suspected. A constant origin error and a per-label pitch error require different fixes; do not fit a growing software offset to conceal drift.

## Automated verification and evidence limits

The accepted release passed 125 tests across 18 focused photobooth suites. Relevant suites include:

| Suite | What it checks |
| --- | --- |
| `photoboothLateGap.test.ts` | Mode-switch sequence, completion and stop paths |
| `photoboothSdkThirdParty.test.ts` | Installed SDK packet construction and full 640-row page with an unrecognized RFID heartbeat |
| `photoboothRasterDriver.test.ts` | Driver integration, new-photo requests and batch submission |
| `photoboothCalibration.test.ts`, `photoboothRecalibrationFlow.test.ts` | Position confirmation, pending-task recovery and explicit recalibration |
| `photoboothApprovedLayout.test.ts`, `photoboothLabelGeometry.test.ts`, `photoboothStripLayout.test.ts` | Shared dimensions, visible content and footer placement |

These are software regressions, not physical certification. Historical open-job/page-stop tests preserve diagnostics; passing them does not turn a physically rejected feed profile into a recommended one. Other firmware, label heights, gap materials, extended runs and different printer models need their own evidence.

## References

Implementation links are pinned to the accepted release commit so later changes cannot silently alter the evidence. External documentation was checked on 28 October 2026.

- **R1 — Production driver and recovery:** [b21Driver.ts](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/photobooth/client/src/helpers/b21Driver.ts). Task setup, calibration, pending state and actual error handling.
- **R2 — Accepted sequence:** [lateGapTest.ts](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/photobooth/client/src/helpers/lateGapTest.ts). Profile values, switch/readback/status ordering and completion.
- **R3 — Offline firmware experiment:** [b21_late_gap_probe.py](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/photobooth/experiments/b21_late_gap_probe.py). Hash-locked handler probe with explicit hardware stubs; not a motor simulation.
- **R4 — Chronological measurement record:** [photobooth-print-registration.md](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/docs/photobooth-print-registration.md). Original candidate progression, measurements and later acceptance; historical provisional statuses must be read chronologically.
- **R5 — SDK regression and upstream:** [installed-SDK test](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/server/photoboothSdkThirdParty.test.ts), [NiimBlueLib source](https://github.com/MultiMote/niimbluelib), [protocol API documentation](https://libdocs.niim.blue/classes/API.NiimbotProtocol.html). This release used 0.47.1; current upstream documentation may change.
- **R6 — Manufacturer specifications:** [NIIMBOT B21 Quick Start Guide, English specifications, PDF page 10](https://m.media-amazon.com/images/I/B1I20feqv3L.pdf#page=10). Manufacturer-authored manual hosted by a retailer; lists 203 dpi and 20–48 mm printing width. It does not supply the exact end-feed compensation used in this investigation.
- **R7 — Shared layout:** [labelGeometry.ts](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/photobooth/client/src/helpers/labelGeometry.ts), [stripLayout.ts](https://github.com/Huiyuhere/yourtypemixer/blob/9d1daf65341703fbf859c374fee53c66e7208c5c/photobooth/client/src/helpers/stripLayout.ts).
- **R8 — Reverse-engineered protocol reference:** [NIIMBOT Community Wiki protocol](https://printers.niim.blue/interfacing/proto/), particularly SetLabelType, PrintStart, LabelPositioningCalibration, PrintStatus and PrintEnd. This is community research, not a manufacturer command-support guarantee for every model. The successful command timing is supported by this project's firmware probe and physical observation, not claimed as an official vendor procedure.

Firmware binaries, private photographs and device-specific raw logs are not published with this document.
