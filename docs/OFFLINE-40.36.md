# Stock 40.36 offline observations

Input SHA-256: `25c9ba099339b482b6ba1b515fbf9bdfb32969abf38d6712be39c7c4b294d1a0`.
Image base: `0x08002000`. Capstone 5.0.7, ARM Thumb little-endian. These are static-analysis candidates, not a tested bypass. No binary bytes changed and no debug commands sent.

## Debug RFID mode candidate

- String `test rfidMode` at `0x08017d40`.
- Dispatcher uses ADR at `0x0801795c`, compares 13 bytes through `0x08002bc6`, then branches on the comparison result.
- Matching handler at `0x08017968` reads argument character at input offset 14. ASCII `1`, `2`, `3` select byte values 1, 2, 3; other values select 0. It writes `[r7 + 0x27]` then returns through `0x0801798c`.
- In this dispatcher r7 is loaded at `0x08017888` from literal `0x08017c7c`, whose value is `0x20000192`. Candidate mode byte is therefore `0x200001b9` (RAM). r8 is initialised to 1 at `0x080178ce`; r4 to 0 at `0x08017864`.
- This handler has no direct flash-write call. That does NOT prove that other code consuming the mode is harmless, temporary, or a paper-authentication bypass. Trace consumers and reset initialisation before execution.

## RFID read diagnostic candidate

- Dispatcher path `0x0801800a` calls `0x08015304`, `0x080154b0`, `0x08015750` then compares byte `[r4+9]` to 1.
- r4 comes from literal `0x0801824c`, value `0x20001eec`.
- Failure path references string at `0x08018250` (`label rfid read failed`); success path references `0x0801826c` (`label rfid read success`).
- This identifies a diagnostic state check, not yet the job-start rejection path. Do not patch it merely because it prints the relevant words.

Next: resolve mode-byte readers and their effects, and correlate job-start response 00 with the command dispatcher. Linear disassembly can misinterpret embedded data; confirm candidate functions and control flow before treating inferred semantics as established.
