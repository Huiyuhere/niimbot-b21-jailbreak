# Photo rendering, filters and DPI

## Hardware versus image processing

The tested B21 C2B uses a 203 DPI head and 384 printable dots across about 48 mm, on 50 mm-wide stock. At approximately 8 dots/mm, software cannot create smaller independent heat elements or upgrade this head to 300 DPI. Dense black dots can merge on thermal paper. More black coverage is not necessarily more recognizable detail.

The owner preferred a NIIMBOT-app result described as “150 DPI, density 3” on original paper. That is useful empirical feedback, not evidence the physical head changed resolution. Source image, rendering algorithm and paper differed from the early photobooth samples, so it was not a controlled DPI-only comparison.

## Current preferred style C

The production renderer uses the following order:

1. Fit each captured photo into its slot at output size, retaining aspect ratio and full framing.
2. Convert luminance using 0.299 R + 0.587 G + 0.114 B.
3. Apply local histogram contrast: up to 8 × 8 tiles, 256 bins, clip factor 1.5, redistributed excess and interpolated tile maps.
4. Lift photo midtones with `255 * (gray / 255)^0.50`; values below gamma 1 brighten midtones while retaining endpoints.
5. Sharpen using the four-neighbour mean: `clamp(pixel + 1.0 * (pixel - mean))` for C. Style B uses strength 0.6 with the same local contrast.
6. Use serpentine Atkinson diffusion at native output resolution, threshold 128. Distribute error/8 to six neighbours; 75% of quantization error is diffused. This gives a different tonal result from full-error Floyd–Steinberg.
7. Dither the logo separately from final text rendering. Message/date use the default font and are thresholded at 160 after drawing, preserving crisp strokes rather than photo dot texture.
8. Send the exact one-bit raster shown in preview with requested density 3.

Default `softPhoto` is false. An earlier optional 150/203 downsampling experiment is not the current default. The driver accepts density 2 or 3; the owner saw little visible difference between those settings on these trials. There was no confirmed device readback proving a heat change on unrecognized stock. No print-speed adjustment was transmitted; a UI/model `speed` field alone is not proof of a device command.

## Physical comparisons and limits

Early standard dithering produced faces the owner considered too dark. Atkinson made smiles more recognizable. The owner preferred B and C over baseline, then chose C for clearer features. These are subjective physical comparisons, not an objective resolution benchmark or a controlled paper comparison.

Threshold/stencil rendering was explored as a graphic alternative; it can remove subtle facial tones. Style C aims to retain facial structure with local contrast, lighter midtones and edge sharpening. It cannot recover detail absent from the source image. Preview shows transmitted dots, not thermal dot spreading, paper coating response or exact darkness.

For group photos, keep face size, focus, lighting and framing consistent during comparisons. Compare one rendering parameter at a time, using the same image, physical dimensions and roll. Test a new paper stock independently before copying density settings.

## Exact implementation

- [ThermalPrint renderer at 428bbf4](https://github.com/Huiyuhere/yourtypemixer/blob/428bbf4/photobooth/client/src/components/ThermalPrint.tsx)
- [Local contrast at 428bbf4](https://github.com/Huiyuhere/yourtypemixer/blob/428bbf4/photobooth/client/src/helpers/photoContrast.ts)
- [B21 transport/driver at 428bbf4](https://github.com/Huiyuhere/yourtypemixer/blob/428bbf4/photobooth/client/src/helpers/b21Driver.ts)
- [NIIMBLUE model table](https://printers.niim.blue/hardware/models/) — distinguish standard B21 from B21 Pro.
