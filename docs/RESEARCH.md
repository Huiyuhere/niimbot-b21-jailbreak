# Third-party label investigation — 2026-10-26

Target: B21 C2B model 775, HW 40.10, FW 40.36; third-party 50 × 80 mm gap labels. This is a research record, not a verified jailbreak. No new print jobs or firmware writes were performed during this search.

## Failure evidence and interpretation

- Historical original 40 × 30 mm NIIMBOT roll: owner confirmed a correct physical print using NIIMBLUE.
- Historical third-party 50 × 80 mm roll: UI reported `Print error 20: WriteRfidFail` (decimal 20 = hexadecimal 0x14). The exact command at which that historical error arrived has not yet been established.
- Corrected read-only USB probe: lid closed, paper present, RFID unrecognised. See `evidence/2026-10-26-usb-baseline-corrected.json`.
- Working hypothesis: a missing/unaccepted tag triggers a firmware rejection. The error name alone does not establish a defective RFID writer, nor does it prove every supported print mode fails.
- The prior USB port-lock failure was a host connection problem. The first probe's incorrect version display was our decoder bug. Neither was a printer paper error; both are retained in the experiment log.

## Source assessment

| Source | Finding | Applicability / next step |
|---|---|---|
| [B21 Pro jailbreak](https://github.com/doctormord/Niimbot-B21-Pro-Jailbreak) and [history](https://github.com/doctormord/Niimbot-B21-Pro-Jailbreak/blob/main/history.md) | Pro patch changes the RFID validity path, density default and checksum handling. History records unsuccessful energy/guard experiments. | Borrow the investigation method only. Our raw 40.36 image differs from the Pro header format; addresses and bytes cannot be copied. Preserve thermal protection. |
| [ThreeDaPrint issue 6](https://github.com/ThreeDaPrint/niimbot/issues/6) | B1 HW 5.10 / FW 5.26 reports `55 55 db 01 14 ce aa aa`, the same named WriteRfidFail error, on untagged paper. Comments discuss B1 patches/downgrades. | Strong analogous symptom, not a B21 compatibility or safe-downgrade guarantee. Trace our error-producing branch. |
| [lotabout HW6.01 branch](https://github.com/lotabout/niimbot/tree/niimbot-hw6.01) | B1 HW6.01/FW6.19 firmware patch. | Model-specific code; useful comparison, not an image for our printer. |
| [beraT-T notes](https://github.com/beraT-T/niimbot-b1-unlock-notes) | B1 patch validation used original paper with the RFID removed; purchased third-party paper was not validated. Calibration can advance multiple labels. | Avoid treating chipless original stock as proof of our roll compatibility. Do not use calibration in the bounded one-label tests. |
| [vkolarik B1](https://github.com/vkolarik/niimbot-b1), [analysis](https://github.com/vkolarik/niimbot-b1/blob/main/docs/firmware-analysis.md) | Combined client/firmware work addresses RFID and alignment on B1 HW6.01/FW6.19. | Supports analysing feed/alignment as well as permission to print; a simple skipped branch may not suffice. Different MCU/image layout. |
| [niimprint issue 34](https://github.com/AndBondStyle/niimprint/issues/34) | Read discussion including comments obtained through the GitHub API. Reports B21_C2B firmware flashing support, but public stock images are explicitly not patched. Later comments direct patch seekers to NiimBlue Discord. | Flasher compatibility does not establish jailbreak compatibility or recoverability. No exact 40.36 patch found in inspected comments. |
| [NIIMBLUE FAQ](https://github.com/MultiMote/niimblue/wiki/Frequently-asked-questions) | Alternative client does not itself remove firmware paper restrictions. | Changing app/library alone may leave the same hardware error. |
| [Tested models](https://github.com/MultiMote/niimbluelib/issues/1) | Model 775 C2B is listed with B1 print task; model 771 has a different task. | Keep exact model identity; do not assume all B21 names mean the same protocol. |
| [B21 C2B recovery](https://printers.niim.blue/hardware/NIIMBOT-B21_C2B/niimbot-b21-c2b-unbrick/) | Invasive recovery includes loss of factory data when protection is removed. | Incompatible with the owner's no-erasing constraint. A downloaded stock image is not a full device backup. |
| [Serial commands](https://printers.niim.blue/interfacing/serial-commands/) | Debug command names include RFID/unlock-related operations. | Names do not establish safe semantics. Do not execute unknown unlock/flash commands; inspect handlers offline first. |
| [Custom firmware directory](https://fw.niim.blue/custom/) | Public fetch returned HTTP 401. | Contents unverified; do not describe it as empty or claim an exact patch exists there. |

## Wider search coverage and limitations

Searches included exact model/version terms, B21 C2B jailbreak, RFID bypass, third-party labels, and English/Chinese/Russian variants. Platforms included GitHub, Reddit, Stack Overflow and Substack. Search indexing and publicly accessible pages are not exhaustive; private Discord content was not inspected and no community messages were sent.

- Reddit discussions about [alternative clients](https://www.reddit.com/r/selfhosted/comments/1wbnfaj/print_to_a_niimbot_label_printer_without_their/) and [label restrictions](https://www.reddit.com/r/niimbot/comments/1hh13lp/any_thermal_printers_like_these_that_let_you_use/) supplied leads, not verified model-775 instructions. Technical conclusions above use linked project sources.
- [Stack Overflow Xamarin printing question](https://stackoverflow.com/questions/72738475/niimbot-printer-not-printing-xamarin-forms) concerns client/protocol problems, not a demonstrated firmware RFID bypass. Searches also surfaced Android connection questions; no applicable 40.36 jailbreak was located.
- Substack searches for NIIMBOT/jailbreak/third-party paper did not locate a relevant technical bypass. Unrelated search matches are not evidence of support.
- Exact-version searches such as `"B21" "40.36" jailbreak` and `"B21_C2B" patched firmware` did not establish a ready-made, validated patch for this unit.

## Next tests, in order

1. Capture one ordinary USB gap-label job, with timestamps and every response, to locate the exact rejection stage; retain the existing successful original-roll result as the positive control.
2. If justified by that trace, test one supported alternate paper mode separately, documenting feed/alignment and restoring the original setting. Continuous mode is value 3, not 2; value 2 is black-mark stock. An alternate mode is an experiment, not an assumed RFID bypass.
3. Analyse the unchanged, hash-verified stock 40.36 image offline: locate command dispatch, error 0x14 production, RFID state consumers, and print/feed paths. Compare methodology with Pro/B1 sources, not their patch offsets.
4. Prepare a candidate only after identifying exact instructions and consequences. Review input hash, byte diff, checksum format and recovery limits before any firmware write. No firmware-write step is implied by this search record.
5. After a justified change, test one sparse label before any photo, then alignment and photobooth output. Count every job against the owner's 10-label allowance.

Each test record must include: hypothesis; source/version; settings before/after; request and response bytes; decoded error; failing stage; physical output confirmed by owner; labels consumed; whether the failure explanation is proven or inferred; next evidence needed; restoration result. A timeout is recorded as a timeout, never relabelled as an RFID failure without a matching packet.
