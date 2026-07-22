# Contributing to Open Survival Wiki

Thank you for contributing to the Open Survival Wiki. This document outlines content guidelines, review processes, and standards for submissions.

## Content Style Guide

### Voice and Tone

- **Active voice.** Write directly. "Apply pressure to the wound" not "Pressure should be applied to the wound."
- **Imperative mood for procedures.** "Cut the bandage to length" not "You should cut the bandage."
- **Present tense.** "Water boils at 100 °C" not "Water will boil."
- **Neutral, factual tone.** Avoid speculation or opinion. Cite practical experience or authoritative sources where possible.
- **No promotional language.** No brand endorsements or product placements.

### Units and Measurements

- **Metric units only.** Temperatures in °C, distances in metres/kilometres, volumes in litres, weights in grams/kilograms.
- Imperial equivalents in parentheses for reference: `Boil at 100 °C (212 °F)`.
- Time: 24-hour clock for precise times; duration in days/weeks/months.

### Formatting

- Use ATX headings (`##` for section, `###` for sub-section).
- Use numbered lists for sequential steps.
- Use bullet lists for options or materials.
- Use `code blocks` for commands, measurements, or chemical formulas.
- Use `{% warning() %}`, `{% info() %}`, `{% steps() %}`, `{% materials() %}` shortcodes appropriately.
- Keep paragraphs short (3–5 sentences max).
- One blank line between sections.

### Safety Disclaimers

**Required on the following content types:**
- **Weapons:** Include a safety box at the top: "Improper handling of weapons can cause death or serious injury. Verify local laws before constructing or carrying."
- **Medicine/herbal remedies:** Include a safety box: "This information is for educational purposes only. Misidentification or improper dosage can be fatal. Consult a qualified medical professional when possible."
- **Fire/high-heat:** Include a safety box: "Uncontrolled fire is a leading cause of death in survival situations. Maintain a firebreak site and never leave unattended."
- **Structural/engineering:** Include a note: "Load-bearing structures require proper engineering. This guide provides general principles only."

Use the `{% warning() %}` shortcode for all safety boxes.

### Geographic Focus

Priority regions for content and examples:
1. **Australia (AU)** — arid, tropical north, temperate south, coastal
2. **China (CN)** — diverse climates, high-density urban, remote rural
3. **Southeast Asia (SEA)** — tropical, monsoon, island nations

Secondary: North America, Europe, Africa.

When providing examples (e.g. edible plants, weather patterns), prioritise AU/CN/SEA. Global applicability is the goal; regional specificity is noted in brackets: `*Acacia aneura* (Mulga — arid AU)`.

## Image Guidelines

- **Format:** WebP preferred. PNG for screenshots/diagrams. No BMP or TIFF.
- **Max file size:** 500 KB per image.
- **Dimensions:** Max 1920px wide. Thumbnails should be ≤ 400px.
- **Alt text:** Required on every image. Describe what the image shows, not just "Image of a knife."
- **File naming:** `kebab-case-descriptive.webp`. No spaces.
- **Placement:** Place images in `static/images/<section>/`. Use the `{% image() %}` shortcode.
- **Diagrams:** SVG preferred for line drawings and diagrams.

## Content Structure Rules

- Each article is a Markdown file in the appropriate `content/` subdirectory.
- Every section directory must have an `_index.md` that describes the section.
- Front matter must include: `title`, `description`, `date`, `updated`, `tags`, `category`.
- Example front matter:
  ```toml
  +++
  title = "Finding Water in Arid Environments"
  description = "Techniques for locating water sources in dry climates"
  date = 2026-07-22
  updated = 2026-07-22
  tags = ["water", "arid", "survival"]
  category = "immediate"
  +++
  ```

## Review Process

1. **Draft:** Write your content in a branch.
2. **Self-review:** Check against style guide, add safety disclaimers where needed, verify all links work.
3. **Peer review:** At least one other contributor reviews for technical accuracy and style compliance.
4. **Technical review** (if applicable): Weapons, medicine, and structural content requires subject-matter expert review.
5. **Merge:** Once approved, squash-merge into main.

## Pull Request Guidelines

- One topic per PR. Keep PRs focused.
- PR title: `[Tier N] Brief description` (e.g. `[Tier 1] Water procurement in monsoon climates`).
- Include a summary of changes and any review notes.
- Reference related issues or articles.

## What Not to Contribute

- Do not submit content promoting specific brands or commercial products.
- Do not submit content advocating violence, discrimination, or illegal activity.
- Do not submit unverified "survival myths" or urban legends — cite sources.
- Do not submit AI-generated content without human verification and heavy editing.

## Code of Conduct

Be respectful. Survival knowledge saves lives; treat every contributor with dignity regardless of background, experience level, or skill set.

---

*Knowledge shared is survival multiplied.*
