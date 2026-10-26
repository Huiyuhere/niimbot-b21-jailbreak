# Gap positioning and alignment

## Observed positioning command

On model 775 / HW40.10 / FW40.36, send `8E` with payload `01`:

```
TX 55 55 8e 01 01 8e aa aa
RX command 8f, payload 01
```

This is a positioning candidate, not a documented persistent sensor-enable switch. First preflight reported continuous type 3; after calibration, a later read reported gap type 1. No mode write was sent in that calibration operation, but causation was not isolated. The reload trial started in gap type 1. RFID remained unrecognized. Calibration succeeded physically without starting a gap-mode print job.

| Step | Owner-observed result | Labels consumed |
| --- | --- | --- |
| Positioning | One label advanced; gap at tear edge | 1 |
| 72 mm raster test, marks at raster 5/55 mm | Marks at sticker 0/50 mm | 1 |
| Identical next print | Upper mark missing; lower still 50 mm | 1 |
| Open/reload, positioning again | One label advanced; gap at tear edge | 1 |
| Recovery print | Lower mark again 50 mm, 30 mm above bottom | 1 |

All five labels were consumed. Owner accepted the two consecutive lower-marker measurements for repeatability and prioritized reload recovery over a third uninterrupted print. Final upper-mark visibility was not resolved beyond at-edge/missing. This supports one successful reload-recovery trial; it does not prove long-run registration, automatic gap sensing between continuous jobs, or restart recovery.

## Operator procedure supported by the trial

Load stock, close lid, read identity/paper state, send one positioning command, then physically confirm gap position and feed amount. Run one measured print before event use. Treat manually moved/reloaded stock as requiring positioning again. A fresh origin/device connection may need pairing. Use one connection at a time.

The app should report “Positioning command accepted — check the label” until the operator confirms the physical result. There is no validated raw gap-sensor signal in the current heartbeat decoder; paper presence and RFID status are not a measured gap location. Exact sensor placement for this C2B revision has not been verified from a manufacturer diagram. No automatic lid-change calibration is implemented.

## Margin correction and longer-area limit

The 72 mm test's 5 mm raster mark physically landed at the top edge: approximately -5 mm offset. The production three-photo layout now starts at raster y=80 (10 mm), targeting 5 mm physical top padding. Photo slots are 128 dots high with 134-dot spacing, full image contained without stretching. Owner measured about 5 mm above the photos and 15 mm below the text.

A separate 82 mm / 656-row test used marks at raster 10 and 80 mm; owner measured 3 and 73 mm on the sticker. Separation was correct at 70 mm. Feed amount and final stop position were not confirmed, and the final taller real-photo job was not recorded. Do not ship this as repeatable equal-margin printing. Increasing raster height can alter subsequent starting position because job-end feed still occurs. No confirmed B21-specific final-feed compensation was established.

## Sources and reproduction

- [Protocol reference](https://printers.niim.blue/interfacing/proto/) — positioning command, label types and error packets.
- [NIIMBLUE API](https://libdocs.niim.blue/classes/API.NiimbotProtocol.html#labelPositioningCalibration) — reported B1 behavior is not proof for B21.
- [Local-test harness at 428bbf4](https://github.com/Huiyuhere/yourtypemixer/tree/428bbf4/photobooth/experiments/gap-sensor) — logs-before-write, explicit attempt guards, physical feedback and budget accounting. Device-local logs/baseline snapshots are excluded from Git. Historical exhausted-budget guard state must not be treated as a reusable one-click production calibration system.

No further hardware test is implied by publishing this document. Reopening/restart recovery, repeated load cycles, equal margins and safe automation need new explicit label budgets.
