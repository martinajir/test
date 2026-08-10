// app.js
// Wires up the story generator UI: clicking "More words" appends a new
// randomly-chosen fragment to the story. "Start new story" resets everything
// with a fresh opener.

(function () {
  const storyEl = document.getElementById('story');
  const wordCountEl = document.getElementById('wordCount');
  const moreBtn = document.getElementById('moreBtn');
  const restartBtn = document.getElementById('restartBtn');

  let usedFragments = [];
  let storyText = '';

  function randomFrom(list, exclude) {
    const pool = exclude
      ? list.filter((item) => !exclude.includes(item))
      : list;
    const source = pool.length > 0 ? pool : list;
    return source[Math.floor(Math.random() * source.length)];
  }

  function countWords(text) {
    const trimmed = text.trim();
    return trimmed.length === 0 ? 0 : trimmed.split(/\s+/).length;
  }

  function updateView() {
    storyEl.textContent = storyText;
    wordCountEl.textContent = `${countWords(storyText)} words`;
  }

  function startNewStory() {
    usedFragments = [];
    const opener = randomFrom(STORY_OPENERS);
    const firstFragment = randomFrom(STORY_FRAGMENTS);
    usedFragments.push(firstFragment);
    storyText = `${opener} ${firstFragment}`;
    moreBtn.disabled = false;
    moreBtn.textContent = 'More words ✨';
    updateView();
  }

  function addMoreWords() {
    // Once most fragments have been used, wrap up the story with a closer.
    if (usedFragments.length >= STORY_FRAGMENTS.length) {
      const closer = randomFrom(STORY_CLOSERS);
      storyText += ` ${closer}`;
      moreBtn.disabled = true;
      moreBtn.textContent = 'The end';
      updateView();
      return;
    }

    const nextFragment = randomFrom(STORY_FRAGMENTS, usedFragments);
    usedFragments.push(nextFragment);
    storyText += ` ${nextFragment}`;
    updateView();
  }

  moreBtn.addEventListener('click', addMoreWords);
  restartBtn.addEventListener('click', startNewStory);

  // Kick things off with an initial story on page load.
  startNewStory();
})();
