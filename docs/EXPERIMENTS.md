# Experiment log

All dates below are 2026-10-26 unless stated. One job-start diagnostic has been sent; no image rows or firmware writes. Physical labels consumed: 0 of 10, confirmed by owner.

| ID | Action | Result | Conclusion / next step |
|---|---|---|---|
| H01 | Earlier NIIMBLUE B1 task on original 40 x 30 mm roll | Owner physically confirmed correct print | Historical positive control; not rerun here |
| H02 | Earlier normal task on third-party 50 x 80 mm roll | WriteRfidFail (20); paper/lid detected, RFID false | Printer-side rejection; not proof that every possible task mode fails |
| D01 | First USB read-only probe | Port locked by NIIMBOT app | No packets sent; owner closed/disconnected app |
| D02 | USB probe after port release | Model 775; first decoder incorrectly reported versions as 102.76/102.50 and waited for wrong heartbeat ID | Preserve raw evidence; correct decoder, no printer change |
| D03 | Corrected USB probe, 10:39 UTC / 18:39 Singapore | Info and heartbeat agree: FW 40.36, HW 40.10, 384 dots. Battery 100%, lid closed, paper present, RFID unrecognised | Identity confirmed; no print commands or firmware writes |
| R01 | Official API query using model and firmware version only | Query from 40.33 returns stock 40.36 download; query at 40.36 gives no newer update | Obtain exact stock image; restoration remains unverified |

Probe tests: four passing tests cover packet framing, fragmented/corrupt packet parsing, rejection of printing/writing/identifying requests, and version decoding. These do not prove firmware recovery or print success.

For each subsequent experiment record timestamp, hypothesis, source commit, input/output hashes, settings, command trace, response, physical outcome, label count, conclusion and restoration status. Distinguish offline analysis from actual device writes.

R02: Downloaded stock 40.36 (113,680 bytes). Full-file CRC32 55760c0d matches the API field named md5 (which is only eight hex digits). SHA-256 is in the manifest. The image begins with a vector table, not the Pro firmware header. Directly running the Pro patcher on this file would be inappropriate. No image was sent to the printer.

R03: Expanded public-source search across GitHub, Reddit, Stack Overflow, Substack and multilingual queries. Found analogous B1 fatal 0x14 RFID rejection and model-specific B1/Pro patches, but no verified model-775/HW40.10/FW40.36 jailbreak in the sources inspected. Retrieved the niimprint issue 34 comments through the GitHub API to inspect comments hidden in the rendered page. Public custom-firmware directory returned 401; private Discord contents remain uninspected. See RESEARCH.md for source matrix, exact failure interpretation and next-test sequence. No printer commands or label consumption in this research step.

T01 (10:55 UTC): `tools/b21_start_test.py` used the NIIMBLUE 0.47.1 B1 opening sequence over USB. Unchanged density 3 and gap-label type 1 were acknowledged with 01. PrintStart command `555501070001000000000007aaaa` received response command 0x02 payload 00. Script stopped before PageStart or image rows; it did not capture an error 0xDB/0x14 in this attempt. PrintEnd cleanup received 0xF4 payload 01. Before/after identity, density and label type agree; paper present, lid closed, RFID unrecognised. Owner confirmed no movement or error light. Conclusion: this ordinary gap-label job is refused at job start; exact firmware reason remains inferred, not proven by response 00 alone. Evidence: `evidence/2026-10-26-usb-start-test.json`. No retry occurred. Zero labels consumed.

A01: Offline hash-verified stock analysis located the debug `test rfidMode` handler and a RAM byte it selects, plus separate RFID read diagnostic paths. No command was executed and no firmware was altered. See OFFLINE-40.36.md for addresses, evidence and unresolved effects. This is a candidate for further analysis, not an established bypass.

A02: Followed the mode byte to its direct reader: it schedules periodic state-bit changes rather than obviously bypassing RFID validity. Withheld that debug command because its benefit and full effects are unproven. Located the stock error decoder mapping internal bit 0x80000 to 0x14, plus multiple candidate setters including retry/counter checks. Added a hash-locked offline inspection tool and disassembly evidence. No device commands or labels used. Next: correlate the normal PrintStart rejection with these state paths, without masking unrelated errors or thermal protections.
