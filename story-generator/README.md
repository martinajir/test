# Story Generator

A tiny, dependency-free web app that generates a short story and lets you
click a button to keep expanding it with more words.

## How it works

- `index.html` - page layout and styling for the story card, the story text
  area, and the two controls (`More words` and `Start new story`).
- `story-data.js` - a bank of story openers, mid-story fragments, and closing
  lines used to assemble the story.
- `app.js` - the logic that:
  - Picks a random opener + first fragment on load.
  - Appends a new, not-yet-used fragment each time you click **More words**.
  - Once all fragments have been used, appends a closing line and disables
    the button (the story is "The end").
  - Lets you click **Start new story** to reset with a fresh random opener.
  - Keeps a live word count under the story text.

## Running it

No build step or server required. Open `story-generator/index.html` directly
in a browser, or serve the folder with any static file server, e.g.:

```bash
cd story-generator
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.
