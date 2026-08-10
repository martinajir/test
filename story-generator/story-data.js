// story-data.js
// A bank of story fragments used to build a randomly generated, ever-growing story.
// Each click on "More words" appends another randomly chosen fragment.

const STORY_OPENERS = [
  "Once upon a time, in a village hidden behind a curtain of fog,",
  "The old lighthouse keeper had not seen another soul in years, until one stormy night,",
  "Deep within the clockwork city, where gears turned instead of hearts,",
  "On the day the stars fell silent, a young cartographer named Mira",
  "Long before the maps were drawn, when dragons still argued over borders,",
];

const STORY_FRAGMENTS = [
  "a strange light flickered at the edge of the forest, pulling curious eyes toward the tree line.",
  "an old book began to whisper secrets that hadn't been spoken aloud in a hundred years.",
  "a traveler arrived with a satchel full of maps that led to places no longer on any chart.",
  "the wind carried the smell of rain and something faintly metallic, like a warning.",
  "a cat with mismatched eyes padded silently across the rooftops, watching everything.",
  "the townsfolk gathered, unsure whether to celebrate or flee.",
  "somewhere below the cobblestones, a hidden door creaked open for the first time in decades.",
  "a letter arrived, sealed in wax the color of dried blood, addressed to no one in particular.",
  "the river changed course overnight, revealing the ruins of a city no one remembered building.",
  "a single candle refused to go out, no matter how hard the wind tried.",
  "footsteps echoed from a hallway that, by all accounts, shouldn't have existed.",
  "the stars rearranged themselves into a pattern that matched an ancient prophecy.",
  "a merchant offered a trade that seemed too generous to be entirely honest.",
  "somewhere in the distance, a bell rang thirteen times.",
  "the shadows in the room began to move independently of the light.",
  "a small child pointed at the sky and said, quite calmly, that it was about to change.",
  "the ink on the map shifted, redrawing itself as if alive.",
  "an owl landed on the windowsill holding something that glimmered like starlight.",
  "the ground trembled once, gently, like a giant turning over in its sleep.",
  "a melody drifted from an instrument no one could see.",
];

const STORY_CLOSERS = [
  "And so, the story continues, waiting for someone brave enough to turn the page.",
  "No one knew yet how it would end, but everyone agreed it had only just begun.",
  "Whatever happened next would be told for generations to come.",
  "For now, the tale rests here, though it is far from finished.",
];
