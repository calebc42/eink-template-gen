---
name: '📄 New Device Request'
about: 'Add a new e-ink device to the supported list.'
title: 'Add support for [DEVICE NAME]'
labels: 'enhancement, new device'
---

### 1. Device Name

What is the common name of the device? (e.g., "reMarkable 2", "Boox Note Air 3 C")

### 2. Device ID (Key)

What should the short, unique ID for this device? This is used in the CLI (e.g., `manta`, `a5x`, `nomad`). It must be lowercase, with no spaces, and enclosed in quotes.

### 3. Screen Specifications

Please provide the exact screen specifications. This information is critical for pixel-perfect generation.

-   **Screen Width (pixels):**
-   **Screen Height (pixels):**
-   **Screen DPI (Dots Per Inch):**

### 4. Device Details (Optional but helpful)

-   **Screen Diagonal (inches):** (e.g., 10.3)
-   **Default Margin (mm):** (What seems like a comfortable default writing margin? e.g., 8.5)
-   **Toolbar Width (pixels):** (If the device has a persistent side toolbar, what is its width?)
-   **Source URL:** (Link to a product page or spec sheet confirming these values)

### 5. Confirmation

-   [ ] I have double-checked the `width`, `height`, and `dpi` values from a reliable source.

---

### For Contributors (Optional)

If you are willing to submit a Pull Request, the process is now much simpler:

1.  Open the `src/eink_template_gen/devices.json` file.
2.  Add a new JSON object to the list with the information from above.
3.  Ensure your new entry has a trailing comma `,` if it's not the last one in the list.