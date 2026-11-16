# Builder input

Call `build_ieltsshokh_html` with `{"kind":"writing","data":{...}}` or `{"kind":"reading","data":{...}}`. Use plain English content. The only supported file path is the explicit cached original image field. Do not provide Python or executable HTML.

## Writing

- For a supplied Task 1 image set `data.tasks[0].source_image_path` to its exact original Telegram cache path. The tool embeds the original bytes and returns their SHA-256. Leave `chart_svg` absent. A source missing from the cache needs to be resent. For an explicitly new fictional chart, use `chart_svg` and set the tool-level `practice_visual` to true.

- `data.title`: test name, e.g. `Writing Mock 06`.
- `data.tasks`: exactly two task objects in order. Each has a verbatim `prompt` (separate paragraphs with line breaks), `model` (array of complete model paragraphs), `vocabulary` (array of [expression, explanation] pairs) and `toolkit` (array of [group title, array of [phrase, usage hint] pairs]). Optional `instruction` overrides the word-limit caption. Optional `chart_svg` takes a static SVG with a viewBox and plain shapes/text, without scripts, styles or links.
- Keep the task prompts grounded in the source. If Task 1 requires a visual and it is missing or illegible, ask for that visual. Write a full model report and essay with clear paragraphing, accurate data comparisons, and vocabulary used in context. No band claim about a learner's response.

## Reading

- `data.title`, `data.passages` (1–3), `data.questions` (object keyed by question number), optional `data.minutes`.
- Each passage has `num`, `title`, `caption`, `paragraphs` (plain strings) and `sections`. Mark exact evidence inside a paragraph as `{{1|the exact words}}`. Prefix paragraph labels with `A|`, subheadings with `##` or italics with `@@`. One question number can have several marked excerpts.
- Each section has `type`, `label`, `desc` and the following fields:
  - `tfng`, `ynng`: `qs` list of numbers.
  - `notes`: `text` with blanks like `[[2]]`, optional `title`.
  - `chip`: `qs`, `letters` (e.g. `["A","B","C"]`), optional `box` (plain list of headings).
  - `mc`: `qs` and `options` keyed by question number with [letter, label] pairs.
  - `multi`: starting question `q`, optional choice count `n` (default 2), `stem` and `options` (array of [letter, label] pairs).
- Each question has `prompt`, `answer`, `keyword` (wording from the question), `paraphrase` (exact passage phrase or an em dash when no equivalent exists), `evidence` (exact wording from a marker for that number) and `explanation`. `notes` answers can include an `accept` list of variants. For NOT GIVEN, mark the closest relevant lines and explain what the passage does not establish.
- Read and check all numbering, option sets, answers and source quotes before building. The builder checks shape and exact quote markers. Passing these checks does not establish IELTS accuracy by itself.
