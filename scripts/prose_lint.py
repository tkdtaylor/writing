#!/usr/bin/env python3
"""prose_lint.py - Stylometric and mechanical prose diagnostics CLI.

Uses only the Python 3.10+ standard library. Computes cadence, lexical
diversity, substance/posture ratios, and line-numbered mechanical and lexical
tells matching docs/spec/data-model.md. Never emits a composite AI score.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

try:
    from scripts import strip_markdown as _strip_md
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    import strip_markdown as _strip_md  # type: ignore[no-redef]

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['\u2019-][A-Za-z0-9]+)*")
_ALPHA_RE = re.compile(r"[A-Za-z]+")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")

# Placeholder tokens used during sentence segmentation.
_DOT_PLACEHOLDER = "\x00"
_ABBREV_RE = re.compile(
    r"\b(?:e\.g|i\.e|etc|vs|mr|mrs|ms|dr|prof|jr|sr|inc|ltd|co|fig|no|st|v)\.",
    re.IGNORECASE,
)
_DECIMAL_OR_VER_RE = re.compile(r"\b(?:v?\d+(?:\.\d+)+)")
_FILENAME_EXT_RE = re.compile(
    r"\b([A-Za-z0-9_-]+)\.(md|py|sh|json|ya?ml|txt|toml|js|ts|tsx|jsx|rs|go|html|css|sql)\b",
    re.IGNORECASE,
)
_INITIALS_RE = re.compile(r"\b(?:[A-Z]\.){2,}")
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'\(\[`])")

# Minimal closed-class function words for 3-gram content filtering.
_PURE_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "by",
        "with",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "it",
        "its",
        "that",
        "this",
        "from",
    }
)

# Concrete anchor patterns
_NUMERIC_ANCHOR_RE = re.compile(
    r"\b(?:v\d+(?:\.\d+)*|\d+(?:\.\d+)*(?:%|ms|s|sec|min|hr|h|kb|mb|gb|tb|pb|rps|qps|x|k|m|b)?|p\d{2}|Q[1-4])\b"
)
_QUOTED_PHRASE_RE = re.compile(r"\"[^\"\n]{2,80}\"|\u201c[^\u201d\n]{2,80}\u201d")
_ACRONYM_RE = re.compile(r"^[A-Z]{2,}[0-9]*$")
_PROPER_NOUN_RE = re.compile(r"^[A-Z][a-z]{2,}$")

# Hedges and boosters
_HEDGE_PATTERNS = [
    r"in some cases",
    r"to some extent",
    r"it is possible",
    r"appears? to",
    r"seems? to",
    r"tends? to",
    r"might",
    r"could",
    r"may",
    r"perhaps",
    r"possibly",
    r"arguably",
    r"somewhat",
    r"roughly",
    r"approximately",
    r"apparently",
    r"seemingly",
    r"presumably",
    r"generally",
    r"typically",
    r"usually",
    r"sometimes",
    r"probably",
    r"suggests?",
]
_HEDGE_RE = re.compile(r"\b(?:" + "|".join(_HEDGE_PATTERNS) + r")\b", re.IGNORECASE)

_BOOSTER_PATTERNS = [
    r"clearly",
    r"obviously",
    r"undoubtedly",
    r"certainly",
    r"definitely",
    r"absolutely",
    r"undeniably",
    r"unquestionably",
    r"always",
    r"never",
    r"crucial",
    r"vital",
    r"essential",
    r"critical",
    r"pivotal",
    r"paramount",
    r"transformative",
    r"revolutionary",
    r"groundbreaking",
    r"indispensable",
    r"unprecedented",
    r"fundamentally",
    r"dramatically",
    r"significantly",
    r"extremely",
    r"profoundly",
    r"testaments?",
    r"underscores?",
    r"proves?",
]
_BOOSTER_RE = re.compile(
    r"\b(?:" + "|".join(_BOOSTER_PATTERNS) + r")\b", re.IGNORECASE
)

_IMPORTANCE_TRIGGER_RE = re.compile(
    r"\b(pivotal|transformative|crucial|vital|paramount|underscores?|testaments?|"
    r"indispensable|cornerstone|game-changing|revolutionary|"
    r"without\s+sacrificing|without\s+compromising|distinction\s+matters)\b",
    re.IGNORECASE,
)
_MECHANISM_MARKER_RE = re.compile(
    r"(?:\d|%|"
    r"\b(?:because|by|through|via|when|if|since|unless|until|so that|"
    r"reduces?|reduced|reducing|increases?|increased|increasing|"
    r"cuts?|lowers?|prevents?|blocks?|bounds?|caps?|eliminates?|saves?|"
    r"drops?|raises?|limits?|verifies|validates|encrypts|hashes|caches|retries|"
    r"ms|sec|seconds|minutes|hours|kb|mb|gb|tb|rps|qps)\b)",
    re.IGNORECASE,
)

# Mechanical & lexical tell patterns (using \u2014 escape, never literal em dash)
_EM_DASH_CHAR = "\u2014"

_AI_TELL_WORDS_RE = re.compile(
    r"\b("
    r"delves?|delved|delving|"
    r"tapestr(?:y|ies)|"
    r"realms?|"
    r"testaments?|"
    r"meticulous(?:ly)?|"
    r"nestled|nestles?|"
    r"multifaceted|"
    r"commendabl(?:e|y)|"
    r"utiliz(?:e|es|ed|ing|ation)|"
    r"seamless(?:ly)?|"
    r"robust(?:ly|ness)?|"
    r"pivotal|"
    r"comprehensiv(?:e|ely)|"
    r"holistic(?:ally)?"
    r")\b",
    re.IGNORECASE,
)

_INFLATED_VERBS_RE = re.compile(
    r"(?<!-)\b("
    r"bolsters?|bolstered|bolstering|"
    r"catalyz(?:e|es|ed|ing)|"
    r"grappl(?:e|es|ed|ing)|"
    r"spearheads?|spearheaded|spearheading|"
    r"amplif(?:y|ies|ied|ying)|"
    r"exemplif(?:y|ies|ied|ying)|"
    r"underscor(?:e|es|ed|ing)|"
    r"fosters?|fostered|fostering|"
    r"elevat(?:e|es|ed|ing)|"
    r"streamlin(?:e|es|ed|ing)|"
    r"supercharg(?:e|es|ed|ing)|"
    r"unleash(?:es|ed|ing)?|"
    r"harness(?:es|ed|ing)?|"
    r"reimagin(?:e|es|ed|ing)|"
    r"ignit(?:e|es|ed|ing)|"
    r"illuminat(?:e|es|ed|ing)"
    r")\b(?!-)",
    re.IGNORECASE,
)
_HARNESS_NOUN_PREFIX_RE = re.compile(
    r"\b(?:"
    r"a|an|the|any|each|every|some|no|this|these|those|"
    r"my|our|your|its|their|other|many|several|multiple|different|various|supported|"
    r"local|custom|host|target|single|same|"
    r"across|in|into|within|between|among|for|from|with|without|of|on|at|by|"
    r"agent|test|testing|eval|evaluation|benchmark|safety|wiring|cli|runtime|skill|party"
    r")\s+$",
    re.IGNORECASE,
)

_TECH_BUZZ_NOUNS_RE = re.compile(
    r"\b("
    r"substrates?|"
    r"wedges?|"
    r"nexus|"
    r"primitives?|"
    r"scaffolding|"
    r"paradigms?|"
    r"flywheels?|"
    r"north[- ]stars?"
    r")\b",
    re.IGNORECASE,
)

_LEADING_BLOCK_MARKER_RE = re.compile(r"^\s*(?:>\s*)*(?:[-*+]|\d+[.)])?\s*")
_FRAMING_THEATER_RE = re.compile(
    r"(?:"
    r"\b(?:"
    r"it(?:'s| is) worth noting|"
    r"it(?:'s| is) important to note|"
    r"in today's\b|"
    r"let(?:'s| us) (?:dive in|break (?:this|it) down|unpack(?:\s+(?:this|that|it))?)\b|"
    r"here(?:'s| is) the (?:twist|kicker|catch|thing)\b|"
    r"let that sink in|"
    r"read that again|"
    r"the key insight|"
    r"at its core|"
    r"here(?:'s| is) where it gets interesting|"
    r"in conclusion|"
    r"despite these challenges|"
    r"at the end of the day|"
    r"so,\s+to answer your question"
    r")|"
    r"(?:^|(?<=[.!?])\s+)together,\s+these\b"
    r")",
    re.IGNORECASE,
)

_CONTRASTIVE_PIVOT_RE = re.compile(
    r"("
    r"\b(?:isn't|is not|aren't|are not|wasn't|was not|not)\s+"
    r"(?:just|merely|simply)\s+[^.!?;:\n]{1,80}?,\s*"
    r"(?:it's|it is|they're|they are|that's|that is|we're|we are|but(?:\s+rather)?)\b|"
    r"\bnot\s+only\b[^.!?;:\n]{1,90}?\bbut\s+also\b|"
    r"\bless\s+(?:like|about)\s+[^.!?;:\n]{1,80}?(?:,\s*(?:and\s+)?|\s+and\s+)more\s+(?:like|about)\b|"
    r"\brather\s+than\s+(?:merely|simply)\b"
    r")",
    re.IGNORECASE,
)
_STACCATO_NOT_SENT_RE = re.compile(r"^Not\b(?!\s+only\b).*[.]$")
_SPLIT_PIVOT_NEG_MOD_RE = re.compile(r"\bnot\s+(?:just|merely|simply)\b", re.IGNORECASE)
_SPLIT_PIVOT_COPULA_NEG_RE = re.compile(
    r"\b(?:isn't|is\s+not|aren't|are\s+not|wasn't|was\s+not|weren't|were\s+not|"
    r"it's\s+not|that's\s+not|they're\s+not|not\s+(?:just|merely|simply))\b",
    re.IGNORECASE,
)
_SPLIT_PIVOT_S1_DEM_NEG_RE = re.compile(
    r"^(?:(?:This|That|It)\s+(?:isn't|is\s+not|wasn't|was\s+not)|It's\s+not|That's\s+not)\b",
    re.IGNORECASE,
)
_SPLIT_PIVOT_S2_INSTEAD_RE = re.compile(
    r"^(?:Instead|Rather),\s+(?:it(?:'s|\s+is|\s+was)|they(?:'re|\s+are|\s+were)|"
    r"that(?:'s|\s+is|\s+was)|this\s+(?:is|was))\b",
    re.IGNORECASE,
)
_SPLIT_PIVOT_S2_REFRAME_RE = re.compile(
    r"^(?:(?:Instead|Rather),\s+)?(?:it(?:'s|\s+is|\s+was)|they(?:'re|\s+are|\s+were)|"
    r"that(?:'s|\s+is|\s+was)|this\s+(?:is|was)|we(?:'re|\s+are|\s+were))\b",
    re.IGNORECASE,
)
_SPLIT_PIVOT_S2_PASSIVE_RE = re.compile(
    r"^(?:It(?:'s|\s+is|\s+was)|That(?:'s|\s+is|\s+was)|This\s+(?:is|was))\s+"
    r"(?!used\b|enabled\b|disabled\b|rejected\b|accepted\b|required\b|supported\b|"
    r"ignored\b|configured\b|set\b|stored\b|sent\b|handled\b|processed\b|"
    r"validated\b|verified\b|blocked\b|allowed\b|called\b|invoked\b|deprecated\b|"
    r"logged\b|retried\b|cached\b|dropped\b)",
    re.IGNORECASE,
)

_PARTICIPIAL_TAIL_RE = re.compile(
    r",\s+(?:thereby\s+|thus\s+|ultimately\s+)?"
    r"(?:highlighting|underscoring|emphasizing|ensuring|fostering|cultivating|"
    r"showcasing|reflecting|symbolizing|exemplifying|paving\s+the\s+way\s+for|"
    r"contributing\s+to)\b[^.!?]*[.!?'\")\]]*$",
    re.IGNORECASE,
)
_COPULA_AVOIDANCE_RE = re.compile(
    r"\b(?:"
    r"(?:serves?|served|stands?|stood|functions?|acts?|operates?)\s+as\s+a(?:n)?\s+"
    r"(?:(?:key|core|vital|crucial|critical|powerful|stark|clear|true|central|essential|"
    r"foundational|fundamental|prime)\s+)?"
    r"(?:testament|reminder|cornerstone|catalyst|beacon|pillar|symbol|foundation|model|"
    r"benchmark|backbone|bridge|window|gateway|hub)\b|"
    r"boasts?\s+(?:a\b|an\b|over\b|more\s+than\b|nearly\b|\d)"
    r")",
    re.IGNORECASE,
)
_RHETORICAL_QA_HOOK_RE = re.compile(
    r"^(?:(?:And|So|But)\s+)?"
    r"(?:"
    r"The\s+(?:result|catch|kicker|twist|upside|downside|payoff|problem|secret|truth|"
    r"bottom\s+line|best\s+part|worst\s+part|fix|answer|takeaway)|"
    r"Sound\s+familiar|"
    r"Why\s+does\s+(?:this|that|it)\s+matter|"
    r"What(?:'s|\s+is)\s+the\s+(?:catch|result|fix|point|kicker|twist|upside|downside|"
    r"payoff|bottom\s+line|takeaway)|"
    r"Here(?:'s|\s+is)\s+the\s+question"
    r")\?$",
    re.IGNORECASE,
)
_PERFORMATIVE_FRAGMENT_RE = re.compile(
    r"^(?:"
    r"Full\s+stop|"
    r"Period|"
    r"Simple\s+as\s+that|"
    r"Nothing\s+more,\s+nothing\s+less|"
    r"That\s+changes\s+everything|"
    r"And\s+maybe\s+that(?:'s|\s+is)\s+the\s+point|"
    r"Read\s+that\s+again|"
    r"Let\s+that\s+sink\s+in"
    r")[.!]$",
    re.IGNORECASE,
)
_NOMINALIZATION_CHAIN_RE = re.compile(
    r"\b(?:the|a|an)\s+[a-z]{4,}(?:tion|ment|ance|ence|ization)\s+of\b",
    re.IGNORECASE,
)

_BOLD_BULLET_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+\*\*([^*]+?)\*\*\s*(?::|-|\u2013|\u2014)?\s+(.+)$"
)
_BOLD_COLON_INSIDE_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+\*\*([^*]+?):\*\*\s+(.+)$"
)
_BOLD_COLON_OUTSIDE_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+\*\*([^*]+?)\*\*\s*:\s+(.+)$"
)

_EMOJI_CHAR_CLASS = (
    r"[\U0001F300-\U0001FAFF"
    r"\u2600-\u26FF"
    r"\u2700-\u27BF"
    r"\u2B50\u2B55]"
)
_EMOJI_BULLET_RE = re.compile(
    rf"^\s*(?:(?:[-*+]|\d+[.)])\s*{_EMOJI_CHAR_CLASS}|{_EMOJI_CHAR_CLASS}\ufe0f?\s+\S)"
)

# Connector colon helpers
_LEADING_LABEL_PREFIX_RE = re.compile(
    r"^(?:\s*(?:[-*+]|\d+[.)])\s+)?(?:"
    r"(?:\*\*[^*]+\*\*|`[^`]+`)(?:\s*\([^)]*\))?\s*:\s*|"
    r"(?:note|warning|caution|tip|important|example|summary|result|context|"
    r"problem|decision|status|action|ask|impact|risk|evidence|step\s+\d+)\s*:\s*"
    r")",
    re.IGNORECASE,
)
_CLAUSE_AUX_OR_PRONOUN_RE = re.compile(
    r"\b(?:"
    r"is|are|was|were|am|be|been|being|"
    r"has|have|had|do|does|did|"
    r"can|could|will|would|shall|should|may|might|must|"
    r"it|they|we|you|he|she|i|nobody|everyone|somebody|nothing|everything|"
    r"there\s+(?:is|are|was|were)"
    r")\b",
    re.IGNORECASE,
)
_FINITE_VERB_HINT_RE = re.compile(
    r"\b[a-z]{3,}(?:ed|es|s)\b",
    re.IGNORECASE,
)

# False scale (`from X to Y`) helpers
_FROM_TO_RE = re.compile(
    r"\bfrom\s+([A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*)?)\s+"
    r"to\s+([A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*)?)"
    r"(?=$|[\s,.;:!?)\]])",
    re.IGNORECASE,
)
_LITERAL_ENDPOINTS = frozenset(
    {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
        "jan",
        "feb",
        "mar",
        "apr",
        "jun",
        "jul",
        "aug",
        "sep",
        "sept",
        "oct",
        "nov",
        "dec",
        "morning",
        "noon",
        "afternoon",
        "evening",
        "night",
        "midnight",
        "dawn",
        "dusk",
        "start",
        "end",
        "beginning",
        "finish",
        "top",
        "bottom",
        "left",
        "right",
        "north",
        "south",
        "east",
        "west",
        "up",
        "down",
        "inside",
        "outside",
        "front",
        "back",
        "head",
        "tail",
        "first",
        "last",
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "ten",
        "hundred",
        "stdin",
        "stdout",
        "stderr",
        "input",
        "output",
        "source",
        "target",
        "destination",
        "client",
        "server",
        "host",
        "container",
        "backlog",
        "active",
        "completed",
        "dev",
        "staging",
        "prod",
        "production",
        "local",
        "remote",
        "disk",
        "memory",
        "http",
        "https",
        "json",
        "yaml",
        "markdown",
        "html",
        "time",
        "day",
        "week",
        "month",
        "year",
        "end-to-end",
        "a",
        "z",
    }
)
_COMMON_INFINITIVE_VERBS = frozenset(
    {
        "be",
        "have",
        "do",
        "make",
        "get",
        "use",
        "build",
        "create",
        "run",
        "check",
        "verify",
        "compute",
        "ensure",
        "avoid",
        "prevent",
        "reduce",
        "increase",
        "keep",
        "help",
        "produce",
        "generate",
        "load",
        "read",
        "write",
        "parse",
        "render",
        "send",
        "receive",
        "update",
        "validate",
        "enforce",
        "allow",
        "enable",
        "support",
        "provide",
        "deliver",
        "yield",
        "pass",
        "return",
        "extract",
        "strip",
        "detect",
        "flag",
        "find",
        "show",
        "turn",
        "move",
        "see",
        "know",
        "learn",
        "test",
        "fix",
        "edit",
        "draft",
        "review",
        "lint",
        "route",
        "install",
        "deploy",
        "configure",
        "measure",
        "evaluate",
        "compare",
        "analyze",
        "summarize",
        "inspect",
        "open",
        "close",
        "add",
        "remove",
        "delete",
        "copy",
        "fetch",
        "pull",
        "push",
        "merge",
        "split",
        "join",
        "format",
        "print",
        "emit",
        "report",
        "handle",
        "process",
        "solve",
        "answer",
        "explain",
        "describe",
        "define",
        "set",
        "reset",
        "call",
        "invoke",
        "trigger",
        "launch",
        "stop",
        "start",
    }
)
_DETERMINER_AFTER_TO_RE = re.compile(
    r"^\s+(?:the|a|an|this|that|these|those|our|your|their|its|my|his|her|each|every|all|any|some)\b",
    re.IGNORECASE,
)
_STOP_WORDS_IN_SCALE = frozenset(
    {
        "the",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        "it",
        "them",
        "us",
        "you",
        "me",
        "him",
        "her",
        "one",
        "another",
        "each",
        "other",
        "which",
        "what",
        "where",
        "when",
        "who",
        "whom",
        "here",
        "there",
    }
)

# Passive voice helpers
_PASSIVE_AUX_RE = re.compile(
    r"\b(?:am|is|are|was|were|be|been|being|get|gets|got|gotten)\s+"
    r"(?:[a-z]+ly\s+)?([a-z]{3,})\b",
    re.IGNORECASE,
)
_IRREGULAR_PARTICIPLES = frozenset(
    {
        "built",
        "bought",
        "brought",
        "broken",
        "caught",
        "chosen",
        "done",
        "drawn",
        "driven",
        "eaten",
        "fallen",
        "fed",
        "felt",
        "found",
        "forgotten",
        "forgiven",
        "frozen",
        "given",
        "gone",
        "grown",
        "heard",
        "held",
        "hidden",
        "kept",
        "known",
        "laid",
        "led",
        "left",
        "lost",
        "made",
        "meant",
        "met",
        "paid",
        "put",
        "read",
        "run",
        "said",
        "seen",
        "sent",
        "set",
        "shown",
        "shut",
        "sold",
        "spent",
        "spoken",
        "spread",
        "stood",
        "struck",
        "taken",
        "taught",
        "thought",
        "thrown",
        "told",
        "understood",
        "won",
        "worn",
        "written",
    }
)
_NON_PARTICIPLE_ED_EN = frozenset(
    {
        "red",
        "bed",
        "sled",
        "shed",
        "wed",
        "open",
        "even",
        "often",
        "sudden",
        "golden",
        "wooden",
        "linen",
        "chicken",
        "kitchen",
        "garden",
        "citizen",
        "dozen",
        "seven",
        "ten",
        "men",
        "women",
        "children",
        "token",
        "green",
        "screen",
        "queen",
        "between",
        "keen",
        "naked",
        "wicked",
        "sacred",
        "tired",
        "excited",
        "interested",
        "concerned",
        "pleased",
        "supposed",
        "used",
        "based",
    }
)

# Adverb (-ly) stoplist per Task 004
_NON_ADVERB_LY = frozenset(
    {
        "only",
        "early",
        "family",
        "likely",
        "unlikely",
        "supply",
        "apply",
        "reply",
        "daily",
        "weekly",
        "monthly",
        "yearly",
        "hourly",
        "quarterly",
        "friendly",
        "lovely",
        "lonely",
        "timely",
        "costly",
        "deadly",
        "ugly",
        "holy",
        "silly",
        "belly",
        "jelly",
        "rally",
        "tally",
        "ally",
        "bully",
        "folly",
        "jolly",
        "hilly",
        "chilly",
        "lily",
        "italy",
        "july",
        "fly",
        "ply",
        "sly",
        "rely",
        "imply",
        "comply",
        "multiply",
        "assembly",
        "anomaly",
        "monopoly",
        "melancholy",
        "homily",
        "bodily",
        "orderly",
        "elderly",
        "scholarly",
        "neighborly",
        "cowardly",
        "brotherly",
        "sisterly",
        "fatherly",
        "motherly",
        "poly",
    }
)

# Shorthand ambiguities, exclamation marks, and false agency patterns
_SHORTHAND_AMBIGUITY_RE = re.compile(
    r"(?:\band/or\b|\b[A-Za-z]{2,}\(s\)(?![A-Za-z0-9_]))",
    re.IGNORECASE,
)
_HTML_COMMENT_FRAG_RE = re.compile(r"<!--.*?-->|<!--")
_MD_IMAGE_ALT_RE = re.compile(r"!\[[^\]]*\]")
_GITHUB_ALERT_RE = re.compile(
    r"\[\!(?:NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]",
    re.IGNORECASE,
)
_NOT_EQUAL_RE = re.compile(r"!={1,2}")
_DOUBLE_QUOTED_LITERAL_RE = re.compile(
    r'"(?:\\.|[^"\\\n])*"|\u201c[^\u201d\n]*\u201d'
)
_FALSE_AGENCY_RE = re.compile(
    r"\b(?:the\s+|these\s+|our\s+|raw\s+)?"
    r"(?:metrics?|data|numbers?|telemetry|benchmarks?|architecture|design|schema|"
    r"codebase|history|market|landscape|reality)\s+"
    r"(?:speaks?\b|tells?\s+(?:us|a\s+story)\b|demands?\b|wants?\b|insists?\b|"
    r"dictates?\b|drives?\s+alignment\b|forces?\s+us\b|refuses?\s+to\b|knows?\b)",
    re.IGNORECASE,
)

# Genre profile validation constants and patterns
VALID_PROFILES = (
    "default",
    "technical",
    "memo",
    "one-pager",
    "six-pager",
    "narrative",
)
_NUMBERED_STEP_RE = re.compile(r"^\s*\d+\.\s+")
_LIST_ITEM_PREFIX_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_APPENDIX_HEADING_RE = re.compile(
    r"^\s{0,3}#{1,3}\s+Appendi(?:x|ces)\b",
    re.IGNORECASE,
)
_SLASH_DATE_RE = re.compile(r"(?<!/)\b\d{1,2}/\d{1,2}/(?:\d{2}|\d{4})\b(?!/)")
_TWELVE_HOUR_TIME_RE = re.compile(
    r"(?<![\d.])\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_BARE_URL_RE = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class SentenceSpan:
    line: int
    text: str
    words: list[str]


def _make_excerpt(text: str, limit: int = 120) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _protect_dots(text: str) -> str:
    s = text.replace("...", _DOT_PLACEHOLDER * 3)
    s = _ABBREV_RE.sub(lambda m: m.group(0).replace(".", _DOT_PLACEHOLDER), s)
    s = _DECIMAL_OR_VER_RE.sub(
        lambda m: m.group(0).replace(".", _DOT_PLACEHOLDER), s
    )
    s = _FILENAME_EXT_RE.sub(
        lambda m: f"{m.group(1)}{_DOT_PLACEHOLDER}{m.group(2)}", s
    )
    s = _INITIALS_RE.sub(lambda m: m.group(0).replace(".", _DOT_PLACEHOLDER), s)
    return s


def split_sentences(paragraphs_with_lines: list[tuple[int, str]]) -> list[SentenceSpan]:
    """Split line-tagged paragraphs into SentenceSpan entries."""
    sentences: list[SentenceSpan] = []
    for para_line, para_text in paragraphs_with_lines:
        protected = _protect_dots(para_text)
        parts = _SENT_SPLIT_RE.split(protected)
        for part in parts:
            restored = part.replace(_DOT_PLACEHOLDER, ".").strip()
            if not restored:
                continue
            words = _WORD_RE.findall(restored)
            if words:
                sentences.append(SentenceSpan(line=para_line, text=restored, words=words))
    return sentences


def _coeff_of_variation(lengths: list[int]) -> float:
    if len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    if mean <= 0.0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    return math.sqrt(variance) / mean


def _count_syllables(word: str) -> int:
    letters = "".join(_ALPHA_RE.findall(word)).lower()
    if not letters:
        return 1
    if len(letters) <= 3:
        return 1
    if letters.endswith("e") and not (
        letters.endswith("le") and len(letters) > 2 and letters[-3] not in "aeiouy"
    ):
        letters = letters[:-1]
    elif letters.endswith("ed") and len(letters) > 4 and letters[-3] not in "td":
        letters = letters[:-2]
    elif (
        letters.endswith("es")
        and len(letters) > 4
        and not letters.endswith(("ses", "zes", "xes", "ches", "shes"))
    ):
        letters = letters[:-2]
    groups = _VOWEL_GROUP_RE.findall(letters)
    return max(1, len(groups))


def _compute_mattr_50(tokens: list[str]) -> float:
    n = len(tokens)
    if n == 0:
        return 0.0
    window = 50
    if n < window:
        return len(set(tokens)) / n
    counts: Counter[str] = Counter(tokens[:window])
    total_ttr = len(counts) / window
    num_windows = n - window + 1
    for i in range(window, n):
        outgoing = tokens[i - window]
        incoming = tokens[i]
        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]
        counts[incoming] += 1
        total_ttr += len(counts) / window
    return total_ttr / num_windows


def _compute_repeated_trigrams(tokens: list[str]) -> tuple[float, list[dict[str, Any]]]:
    n = len(tokens)
    if n < 3:
        return 0.0, []
    total_trigrams = n - 2
    min_count = 2 if n < 400 else 3

    trigram_counts: Counter[tuple[str, str, str]] = Counter()
    for idx in range(total_trigrams):
        tri = (tokens[idx], tokens[idx + 1], tokens[idx + 2])
        if all(w in _PURE_STOPWORDS for w in tri):
            continue
        trigram_counts[tri] += 1

    repeated_items = [
        (tri, cnt) for tri, cnt in trigram_counts.items() if cnt >= min_count
    ]
    repeated_items.sort(key=lambda item: (-item[1], " ".join(item[0])))

    excess_repeats = sum(cnt - 1 for _, cnt in repeated_items)
    rate = excess_repeats / total_trigrams if total_trigrams > 0 else 0.0
    formatted = [
        {"trigram": " ".join(tri), "count": cnt} for tri, cnt in repeated_items
    ]
    return round(rate, 4), formatted


def _count_anchors(sentences: list[SentenceSpan]) -> int:
    anchors = 0
    for sent in sentences:
        anchors += len(_QUOTED_PHRASE_RE.findall(sent.text))
        unquoted = _QUOTED_PHRASE_RE.sub(" ", sent.text)
        anchors += len(_NUMERIC_ANCHOR_RE.findall(unquoted))
        words = _WORD_RE.findall(unquoted)
        for idx, tok in enumerate(words):
            if _NUMERIC_ANCHOR_RE.fullmatch(tok):
                continue
            if idx == 0:
                if _ACRONYM_RE.fullmatch(tok):
                    anchors += 1
                continue
            if _ACRONYM_RE.fullmatch(tok):
                anchors += 1
            elif _PROPER_NOUN_RE.fullmatch(tok):
                anchors += 1
    return anchors


def _detect_connector_colons(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    n = len(masked_lines)
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        stripped = mline.strip()
        # Skip ATX headings, Setext underlines, blockquotes, or lines ending with ':'.
        if (
            stripped.startswith("#")
            or stripped.endswith(":")
            or re.match(r"^(?:={2,}|-{2,})$", stripped)
        ):
            continue
        # Strip leading label prefixes (e.g. `- **Term**:` or `- `mode=x` (...):`) before masking inline code.
        without_label = _LEADING_LABEL_PREFIX_RE.sub("", mline)
        cleaned = _strip_md.mask_inline_syntax_for_tells(without_label).strip()
        if ": " not in cleaned:
            continue

        # Inspect each sentence on this line so `A. B: C.` checks `B: C.` cleanly.
        protected = _protect_dots(cleaned)
        for sent_part in _SENT_SPLIT_RE.split(protected):
            sent = sent_part.replace(_DOT_PLACEHOLDER, ".").strip()
            if ": " not in sent or sent.endswith(":"):
                continue
            left, right = sent.split(": ", 1)
            left_clean = _strip_md.clean_inline_markdown(left)
            right_clean = _strip_md.clean_inline_markdown(right)
            if not left_clean or not right_clean:
                continue
            # Ignore quotes introduced by a colon (`He wrote: "..."`).
            if right.lstrip().startswith(('"', "'", "\u201c", "\u2018")):
                continue
            left_words = _WORD_RE.findall(left_clean)
            right_words = _WORD_RE.findall(right_clean)
            if len(left_words) < 3 or len(right_words) < 4:
                continue
            # Distinguish an independent clause from a noun-list enumeration (`a, b, and c`).
            has_clause_signal = bool(_CLAUSE_AUX_OR_PRONOUN_RE.search(right_clean))
            is_comma_list = (
                "," in right_clean
                and bool(re.search(r",\s*(?:and|or)\b", right_clean, re.IGNORECASE))
                and not has_clause_signal
            )
            if is_comma_list:
                continue
            if has_clause_signal or _FINITE_VERB_HINT_RE.search(right_clean):
                hits.append(
                    {
                        "line": idx + 1,
                        "excerpt": _make_excerpt(raw_lines[idx]),
                    }
                )
                break
    return hits


def _detect_bold_restatement_bullets(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    articles = {"the", "a", "an", "this", "that", "our", "your"}
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        m = (
            _BOLD_COLON_INSIDE_RE.match(mline)
            or _BOLD_COLON_OUTSIDE_RE.match(mline)
            or _BOLD_BULLET_RE.match(mline)
        )
        if not m:
            continue
        # Require an explicit separator (colon inside/outside bold or dash) so `- **Codex** auto-loads` is untouched.
        raw_segment = mline
        if not re.match(
            r"^\s*(?:[-*+]|\d+[.)])\s+(?:\*\*[^*]+:\*\*|\*\*[^*]+\*\*\s*(?::|-|\u2013|\u2014))",
            raw_segment,
        ):
            continue
        term_raw = _strip_md.clean_inline_markdown(m.group(1).rstrip(":"))
        rest_raw = _strip_md.clean_inline_markdown(m.group(2))
        term_words = [
            w.lower() for w in _ALPHA_RE.findall(term_raw) if w.lower() not in articles
        ]
        rest_words = [w.lower() for w in _ALPHA_RE.findall(rest_raw)]
        if not term_words or not rest_words:
            continue
        lead_term = term_words[0]
        lead_rest = rest_words[0]
        if lead_rest in articles and len(rest_words) >= 2:
            lead_rest = rest_words[1]

        same_word = lead_term == lead_rest
        shared_stem = (
            len(lead_term) >= 5
            and len(lead_rest) >= 5
            and (lead_term[:5] == lead_rest[:5])
        )
        if same_word or shared_stem:
            hits.append(
                {
                    "line": idx + 1,
                    "term": term_raw,
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _detect_false_scales(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        cleaned = _strip_md.mask_inline_syntax_for_tells(mline)
        cleaned = _strip_md.clean_inline_markdown(cleaned, keep_code_text=False)
        for m in _FROM_TO_RE.finditer(cleaned):
            x_phrase = m.group(1).strip()
            y_phrase = m.group(2).strip()
            combined = f"{x_phrase} {y_phrase}"
            if re.search(r"\d", combined):
                continue
            x_words = [w.lower() for w in _WORD_RE.findall(x_phrase)]
            y_words = [w.lower() for w in _WORD_RE.findall(y_phrase)]
            if not x_words or not y_words:
                continue
            if any(w in _STOP_WORDS_IN_SCALE for w in (x_words[0], y_words[0])):
                continue
            if x_words[-1] in _LITERAL_ENDPOINTS or y_words[-1] in _LITERAL_ENDPOINTS:
                continue
            if x_words[0] in _LITERAL_ENDPOINTS or y_words[0] in _LITERAL_ENDPOINTS:
                continue
            # Exclude `from <noun> to <infinitive verb> [determiner/object]`.
            trailing = cleaned[m.end() :]
            if y_words[0] in _COMMON_INFINITIVE_VERBS and (
                len(y_words) > 1 or _DETERMINER_AFTER_TO_RE.match(trailing)
            ):
                continue
            if _DETERMINER_AFTER_TO_RE.match(trailing):
                continue
            if x_words == y_words:
                continue
            hits.append(
                {
                    "line": idx + 1,
                    "match": f"from {x_phrase} to {y_phrase}",
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _scan_line_regex(
    pattern: re.Pattern[str],
    masked_lines: list[str],
    raw_lines: list[str],
    normalize_quotes: bool = False,
    strip_leading_marker: bool = False,
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        cleaned = _strip_md.mask_inline_syntax_for_tells(mline)
        if normalize_quotes:
            cleaned = cleaned.replace("\u2019", "'").replace("\u2018", "'")
        if strip_leading_marker:
            cleaned = _LEADING_BLOCK_MARKER_RE.sub("", cleaned)
        for m in pattern.finditer(cleaned):
            hits.append(
                {
                    "line": idx + 1,
                    "match": re.sub(r"\s+", " ", m.group(0)).strip().lower(),
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _scan_inflated_verbs(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        cleaned = _strip_md.mask_inline_syntax_for_tells(mline)
        for m in _INFLATED_VERBS_RE.finditer(cleaned):
            matched_lower = m.group(0).strip().lower()
            if matched_lower in {"harness", "harnesses"}:
                prefix = cleaned[: m.start()]
                if _HARNESS_NOUN_PREFIX_RE.search(prefix):
                    continue
                if matched_lower == "harnesses" and not prefix.strip():
                    continue
            hits.append(
                {
                    "line": idx + 1,
                    "match": re.sub(r"\s+", " ", matched_lower),
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _detect_participial_tail_puffery(
    posture_sentences: list[SentenceSpan],
    full_sentences: list[SentenceSpan],
    raw_lines: list[str],
) -> list[dict[str, Any]]:
    full_by_line: dict[int, list[SentenceSpan]] = {}
    for fs in full_sentences:
        full_by_line.setdefault(fs.line, []).append(fs)

    hits: list[dict[str, Any]] = []
    for sent in posture_sentences:
        sent_norm = sent.text.replace("\u2019", "'").replace("\u2018", "'").strip()
        m = _PARTICIPIAL_TAIL_RE.search(sent_norm)
        if not m:
            continue
        tail = m.group(0)
        if _MECHANISM_MARKER_RE.search(tail):
            continue
        # If inline code inside this sentence's trailing clause supplied a concrete
        # mechanism (e.g., `, ensuring \`SHA-256\` digests match`), exempt it.
        line_full_sents = full_by_line.get(sent.line, [])
        if line_full_sents:
            has_unanchored_full = False
            saw_tail_in_full = False
            for fs in line_full_sents:
                fs_norm = fs.text.replace("\u2019", "'").replace("\u2018", "'").strip()
                fm = _PARTICIPIAL_TAIL_RE.search(fs_norm)
                if fm:
                    saw_tail_in_full = True
                    if not _MECHANISM_MARKER_RE.search(fm.group(0)):
                        has_unanchored_full = True
            if saw_tail_in_full and not has_unanchored_full:
                continue
        excerpt_src = (
            raw_lines[sent.line - 1]
            if 1 <= sent.line <= len(raw_lines) and raw_lines[sent.line - 1].strip()
            else sent.text
        )
        hits.append(
            {
                "line": sent.line,
                "match": re.sub(r"\s+", " ", tail).strip().lower(),
                "excerpt": _make_excerpt(excerpt_src),
            }
        )
    return hits


def _detect_rhetorical_qa_pivots(
    posture_sentences: list[SentenceSpan],
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for idx in range(len(posture_sentences) - 1):
        cur = posture_sentences[idx]
        nxt = posture_sentences[idx + 1]
        if len(cur.words) > 8:
            continue
        cur_norm = cur.text.replace("\u2019", "'").replace("\u2018", "'").strip()
        nxt_norm = nxt.text.strip()
        if not cur_norm.endswith("?") or nxt_norm.endswith("?") or not nxt.words:
            continue
        if _RHETORICAL_QA_HOOK_RE.match(cur_norm):
            hits.append(
                {
                    "line": cur.line,
                    "match": re.sub(r"\s+", " ", cur_norm).lower(),
                    "excerpt": _make_excerpt(f"{cur.text} {nxt.text}"),
                }
            )
    return hits


def _detect_performative_fragments(
    posture_sentences: list[SentenceSpan], raw_lines: list[str]
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for sent in posture_sentences:
        sent_norm = sent.text.replace("\u2019", "'").replace("\u2018", "'").strip()
        if _PERFORMATIVE_FRAGMENT_RE.match(sent_norm):
            excerpt_src = (
                raw_lines[sent.line - 1]
                if 1 <= sent.line <= len(raw_lines) and raw_lines[sent.line - 1].strip()
                else sent.text
            )
            hits.append(
                {
                    "line": sent.line,
                    "match": re.sub(r"\s+", " ", sent_norm).lower(),
                    "excerpt": _make_excerpt(excerpt_src),
                }
            )
    return hits


def _detect_split_contrastive_pivots(
    posture_sentences: list[SentenceSpan],
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    n = len(posture_sentences)
    idx = 0
    while idx < n - 1:
        cur = posture_sentences[idx]
        nxt = posture_sentences[idx + 1]
        cur_norm = cur.text.replace("\u2019", "'").replace("\u2018", "'").strip()
        nxt_norm = nxt.text.replace("\u2019", "'").replace("\u2018", "'").strip()

        # Staccato negation runs (`Not X. Not Y. [Z.]`)
        if (
            len(cur.words) <= 10
            and len(nxt.words) <= 10
            and _STACCATO_NOT_SENT_RE.match(cur_norm)
            and _STACCATO_NOT_SENT_RE.match(nxt_norm)
        ):
            run = [cur, nxt]
            j = idx + 2
            while j < n:
                cand = posture_sentences[j]
                cand_norm = (
                    cand.text.replace("\u2019", "'").replace("\u2018", "'").strip()
                )
                if len(cand.words) <= 10 and _STACCATO_NOT_SENT_RE.match(cand_norm):
                    run.append(cand)
                    j += 1
                else:
                    break
            joined_norm = " ".join(
                s.text.replace("\u2019", "'").replace("\u2018", "'").strip()
                for s in run
            )
            joined_raw = " ".join(s.text for s in run)
            hits.append(
                {
                    "line": cur.line,
                    "match": re.sub(r"\s+", " ", joined_norm).strip().lower(),
                    "excerpt": _make_excerpt(joined_raw),
                }
            )
            idx = j
            continue

        # Two-sentence negative parallelisms (`This isn't a X. It's a Y.` / `not simply X. Instead, it is Y.`)
        if cur_norm.endswith(".") and not nxt_norm.endswith("?"):
            is_mod_reframe = bool(
                _SPLIT_PIVOT_NEG_MOD_RE.search(cur_norm)
                and _SPLIT_PIVOT_S2_REFRAME_RE.match(nxt_norm)
            )
            is_instead_copula = bool(
                _SPLIT_PIVOT_COPULA_NEG_RE.search(cur_norm)
                and _SPLIT_PIVOT_S2_INSTEAD_RE.match(nxt_norm)
            )
            is_dem_mirror = bool(
                len(cur.words) <= 14
                and _SPLIT_PIVOT_S1_DEM_NEG_RE.match(cur_norm)
                and _SPLIT_PIVOT_S2_PASSIVE_RE.match(nxt_norm)
            )
            if is_mod_reframe or is_instead_copula or is_dem_mirror:
                pair_norm = f"{cur_norm} {nxt_norm}"
                pair_raw = f"{cur.text} {nxt.text}"
                hits.append(
                    {
                        "line": cur.line,
                        "match": re.sub(r"\s+", " ", pair_norm).strip().lower(),
                        "excerpt": _make_excerpt(pair_raw),
                    }
                )
                idx += 2
                continue

        idx += 1
    return hits


def _detect_stacked_questions(sentences: list[SentenceSpan]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    run: list[SentenceSpan] = []

    def flush_run() -> None:
        if len(run) >= 3:
            hits.append(
                {
                    "line": run[0].line,
                    "count": len(run),
                    "excerpt": _make_excerpt(" ".join(s.text for s in run[:3])),
                }
            )

    for sent in sentences:
        if sent.text.rstrip().endswith("?"):
            run.append(sent)
        else:
            flush_run()
            run = []
    flush_run()
    return hits


def _count_passive_voice(sentences: list[SentenceSpan]) -> int:
    count = 0
    for sent in sentences:
        for m in _PASSIVE_AUX_RE.finditer(sent.text):
            part = m.group(1).lower()
            if part in _NON_PARTICIPLE_ED_EN:
                continue
            if part in _IRREGULAR_PARTICIPLES or (
                len(part) >= 4 and (part.endswith("ed") or part.endswith("en"))
            ):
                count += 1
    return count


def _count_adverbs(tokens: list[str]) -> int:
    count = 0
    for tok in tokens:
        clean = "".join(_ALPHA_RE.findall(tok)).lower()
        if len(clean) >= 4 and clean.endswith("ly") and clean not in _NON_ADVERB_LY:
            count += 1
    return count


def _extract_raw_paragraphs(text: str) -> list[tuple[int, str]]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    paragraphs: list[tuple[int, str]] = []
    buf: list[str] = []
    start_line = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if buf:
                paragraphs.append((start_line, " ".join(buf)))
                buf = []
            continue
        if not buf:
            start_line = idx + 1
        buf.append(stripped)
    if buf:
        paragraphs.append((start_line, " ".join(buf)))
    return paragraphs


def _detect_exclamation_marks(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    """Detect prose exclamation marks outside code, quotes, images, alerts, and !=."""
    hits: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        cleaned = _strip_md.mask_inline_syntax_for_tells(mline)
        cleaned = _HTML_COMMENT_FRAG_RE.sub(" ", cleaned)
        cleaned = _MD_IMAGE_ALT_RE.sub(" ", cleaned)
        cleaned = _GITHUB_ALERT_RE.sub(" ", cleaned)
        cleaned = _NOT_EQUAL_RE.sub(" ", cleaned)
        cleaned = _DOUBLE_QUOTED_LITERAL_RE.sub(" ", cleaned)
        excl_count = cleaned.count("!")
        if excl_count > 0:
            hits.append(
                {
                    "line": idx + 1,
                    "count": excl_count,
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _detect_false_agency(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    """Detect inanimate metrics, data, or architecture performing human rhetorical acts."""
    hits: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        cleaned = _strip_md.mask_inline_syntax_for_tells(mline)
        cleaned = _strip_md.clean_inline_markdown(cleaned, keep_code_text=False)
        for m in _FALSE_AGENCY_RE.finditer(cleaned):
            hits.append(
                {
                    "line": idx + 1,
                    "match": re.sub(r"\s+", " ", m.group(0)).strip().lower(),
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _split_pre_appendix(text: str) -> tuple[str, bool]:
    """Split text before the first non-fenced Appendix heading (h1-h3)."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    fm_end = _strip_md._find_frontmatter_end(lines)
    fence_char = ""
    fence_len = 0
    for idx, line in enumerate(lines):
        if idx <= fm_end:
            continue
        if not fence_char:
            m_fence = _strip_md._FENCE_OPEN_RE.match(line)
            if m_fence:
                marker, rest = m_fence.group(1), m_fence.group(2)
                if not (marker[0] == "`" and "`" in rest):
                    fence_char = marker[0]
                    fence_len = len(marker)
                    continue
            if _APPENDIX_HEADING_RE.match(line):
                return "\n".join(lines[:idx]), True
        else:
            close_re = re.compile(
                rf"^(?:\s*>)*\s*{re.escape(fence_char)}{{{fence_len},}}\s*$"
            )
            if close_re.match(line):
                fence_char = ""
                fence_len = 0
    return text, False


def _compute_body_density(
    paragraphs_with_lines: list[tuple[int, str]],
    masked_lines: list[str],
    raw_lines: list[str],
) -> tuple[int, float]:
    """Compute (total_body_words, prose_paragraph_share) separating paragraphs vs lists."""
    paragraph_words = 0
    list_words = 0
    for line_no, para_text in paragraphs_with_lines:
        wc = len(_WORD_RE.findall(para_text))
        if wc == 0:
            continue
        line_idx = line_no - 1
        check_line = ""
        if 0 <= line_idx < len(masked_lines) and masked_lines[line_idx].strip():
            check_line = masked_lines[line_idx]
        elif 0 <= line_idx < len(raw_lines):
            check_line = raw_lines[line_idx]
        if _LIST_ITEM_PREFIX_RE.match(check_line):
            list_words += wc
        else:
            paragraph_words += wc
    total_words = paragraph_words + list_words
    if total_words == 0:
        return 0, 1.0
    return total_words, round(paragraph_words / total_words, 3)


def _detect_overlong_steps(
    paragraphs_with_lines: list[tuple[int, str]],
    masked_lines: list[str],
    raw_lines: list[str],
) -> list[dict[str, Any]]:
    """Flag numbered procedural steps exceeding the 20-word STE ceiling."""
    hits: list[dict[str, Any]] = []
    for line_no, para_text in paragraphs_with_lines:
        line_idx = line_no - 1
        check_line = ""
        if 0 <= line_idx < len(masked_lines) and masked_lines[line_idx].strip():
            check_line = masked_lines[line_idx]
        elif 0 <= line_idx < len(raw_lines):
            check_line = raw_lines[line_idx]
        if not _NUMBERED_STEP_RE.match(check_line):
            continue
        wc = len(_WORD_RE.findall(para_text))
        if wc > 20:
            excerpt_src = (
                raw_lines[line_idx]
                if 0 <= line_idx < len(raw_lines) and raw_lines[line_idx].strip()
                else para_text
            )
            hits.append(
                {
                    "line": line_no,
                    "words": wc,
                    "excerpt": _make_excerpt(excerpt_src),
                }
            )
    return hits


def _detect_date_time_issues(
    masked_lines: list[str], raw_lines: list[str]
) -> list[dict[str, Any]]:
    """Flag ambiguous slash dates and 12-hour AM/PM clock times outside code/quotes."""
    hits: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        cleaned = _strip_md.mask_inline_syntax_for_tells(mline)
        cleaned = _BARE_URL_RE.sub(" ", cleaned)
        cleaned = _DOUBLE_QUOTED_LITERAL_RE.sub(" ", cleaned)
        line_matches: list[tuple[int, str, str]] = []
        for m in _SLASH_DATE_RE.finditer(cleaned):
            line_matches.append(
                (m.start(), m.group(0), "Use ISO 8601 date format (YYYY-MM-DD)")
            )
        for m in _TWELVE_HOUR_TIME_RE.finditer(cleaned):
            line_matches.append(
                (m.start(), m.group(0), "Use 24-hour UTC time format (HH:MM UTC)")
            )
        line_matches.sort(key=lambda item: item[0])
        for _, match_str, rec in line_matches:
            hits.append(
                {
                    "line": idx + 1,
                    "match": match_str,
                    "recommendation": rec,
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
    return hits


def _evaluate_profile_checks(
    profile: str | None,
    text: str,
    raw: bool,
    paragraphs_with_lines: list[tuple[int, str]],
    masked_lines: list[str],
    raw_lines: list[str],
    body_sent_lengths: list[int],
    body_sent_cv: float,
) -> dict[str, Any] | None:
    """Evaluate genre-specific profile checks when a non-default profile is active."""
    requested = (profile or "default").strip()
    if requested not in VALID_PROFILES:
        raise ValueError(
            f"Unsupported profile {profile!r}; expected one of {', '.join(VALID_PROFILES)}"
        )
    if requested == "default":
        return None

    if requested == "technical":
        overlong_steps = _detect_overlong_steps(
            paragraphs_with_lines, masked_lines, raw_lines
        )
        date_time_issues = _detect_date_time_issues(masked_lines, raw_lines)
        return {
            "profile": "technical",
            "requested_profile": requested,
            "passed": len(overlong_steps) == 0 and len(date_time_issues) == 0,
            "overlong_steps": overlong_steps,
            "date_time_issues": date_time_issues,
        }

    if requested in {"memo", "one-pager", "six-pager"}:
        body_source, has_appendix = _split_pre_appendix(text)
        if has_appendix:
            if raw:
                body_paras = _extract_raw_paragraphs(body_source)
                body_raw = (
                    body_source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
                )
                body_masked = list(body_raw)
            else:
                body_struct = _strip_md.extract_markdown_structure(body_source)
                body_paras = body_struct.paragraphs_with_lines
                body_raw = body_struct.raw_lines
                body_masked = body_struct.masked_lines
        else:
            body_paras = paragraphs_with_lines
            body_masked = masked_lines
            body_raw = raw_lines

        body_word_count, prose_share = _compute_body_density(
            body_paras, body_masked, body_raw
        )
        date_time_issues = _detect_date_time_issues(body_masked, body_raw)

        resolved = requested
        if requested == "memo":
            resolved = "one-pager" if body_word_count <= 750 else "six-pager"

        min_prose_share = 0.80
        prose_density_ok = prose_share >= min_prose_share

        if resolved == "one-pager":
            word_budget_range = [350, 550]
            word_budget_ok = 350 <= body_word_count <= 550
            return {
                "profile": resolved,
                "requested_profile": requested,
                "passed": (
                    word_budget_ok
                    and prose_density_ok
                    and len(date_time_issues) == 0
                ),
                "body_word_count": body_word_count,
                "appendix_stripped": has_appendix,
                "word_budget_range": word_budget_range,
                "word_budget_ok": word_budget_ok,
                "prose_paragraph_share": prose_share,
                "min_prose_share": min_prose_share,
                "prose_density_ok": prose_density_ok,
                "date_time_issues": date_time_issues,
            }

        word_budget_max = 2500
        word_budget_ok = body_word_count <= word_budget_max
        return {
            "profile": resolved,
            "requested_profile": requested,
            "passed": (
                word_budget_ok
                and prose_density_ok
                and len(date_time_issues) == 0
            ),
            "body_word_count": body_word_count,
            "appendix_stripped": has_appendix,
            "word_budget_max": word_budget_max,
            "word_budget_ok": word_budget_ok,
            "prose_paragraph_share": prose_share,
            "min_prose_share": min_prose_share,
            "prose_density_ok": prose_density_ok,
            "date_time_issues": date_time_issues,
        }

    # Narrative profile
    _, prose_share = _compute_body_density(
        paragraphs_with_lines, masked_lines, raw_lines
    )
    min_prose_share = 0.85
    prose_density_ok = prose_share >= min_prose_share
    rounded_cv = round(body_sent_cv, 3)
    min_cv = 0.30
    cadence_ok = True if len(body_sent_lengths) < 6 else rounded_cv >= min_cv
    return {
        "profile": "narrative",
        "requested_profile": requested,
        "passed": prose_density_ok and cadence_ok,
        "prose_paragraph_share": prose_share,
        "min_prose_share": min_prose_share,
        "prose_density_ok": prose_density_ok,
        "body_sentence_count": len(body_sent_lengths),
        "body_sentence_cv": rounded_cv,
        "min_body_sentence_cv": min_cv,
        "cadence_ok": cadence_ok,
    }


def analyze_text(
    text: str,
    source: str = "<stdin>",
    raw: bool = False,
    profile: str | None = None,
) -> dict[str, Any]:
    """Compute stylometric and mechanical prose diagnostics matching data-model.md."""
    md_struct = _strip_md.extract_markdown_structure(text)
    if raw:
        paragraphs_with_lines = _extract_raw_paragraphs(text)
        posture_paragraphs = paragraphs_with_lines
        raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        masked_lines = list(raw_lines)
    else:
        paragraphs_with_lines = md_struct.paragraphs_with_lines
        posture_paragraphs = md_struct.prose_without_code_with_lines
        raw_lines = md_struct.raw_lines
        masked_lines = md_struct.masked_lines

    sentences = split_sentences(paragraphs_with_lines)
    posture_sentences = (
        sentences if raw else split_sentences(posture_paragraphs)
    )
    all_words: list[str] = []
    for sent in sentences:
        all_words.extend(sent.words)
    lower_tokens = [w.lower() for w in all_words]

    word_count = len(all_words)
    sentence_count = len(sentences)
    paragraph_word_counts = [
        len(_WORD_RE.findall(p)) for _, p in paragraphs_with_lines if _WORD_RE.search(p)
    ]
    paragraph_count = len(paragraph_word_counts)

    # Cadence metrics
    all_sent_lengths = [len(s.words) for s in sentences]
    body_sent_lengths = [ln for ln in all_sent_lengths if ln >= 8]
    mean_sentence_words = (
        round(word_count / sentence_count, 2) if sentence_count > 0 else 0.0
    )
    all_sent_cv = _coeff_of_variation(all_sent_lengths)
    body_sent_cv = _coeff_of_variation(body_sent_lengths)
    para_cv = _coeff_of_variation(paragraph_word_counts)

    cadence_masking = bool(
        len(body_sent_lengths) >= 2
        and len(all_sent_lengths) > len(body_sent_lengths)
        and (all_sent_cv - body_sent_cv) >= 0.15
        and body_sent_cv < 0.35
    )

    overloaded_sentences = [
        {
            "line": s.line,
            "words": len(s.words),
            "excerpt": _make_excerpt(s.text),
        }
        for s in sentences
        if len(s.words) > 35
    ]

    if word_count > 0 and sentence_count > 0:
        char_count = sum(sum(1 for ch in w if ch.isalnum()) for w in all_words)
        syllable_count = sum(_count_syllables(w) for w in all_words)
        ari_raw = (
            4.71 * (char_count / word_count)
            + 0.5 * (word_count / sentence_count)
            - 21.43
        )
        fk_raw = (
            0.39 * (word_count / sentence_count)
            + 11.8 * (syllable_count / word_count)
            - 15.59
        )
        ari_grade = round(max(0.0, ari_raw), 2)
        fk_grade = round(max(0.0, fk_raw), 2)
    else:
        ari_grade = 0.0
        fk_grade = 0.0

    # Lexical diversity metrics
    mattr_50 = round(_compute_mattr_50(lower_tokens), 3)
    repeated_trigram_rate, repeated_trigrams = _compute_repeated_trigrams(lower_tokens)

    # Substance and posture metrics
    norm_text_for_rates = "\n".join(
        s.text for s in posture_sentences
    ).replace("\u2019", "'")
    anchor_count = _count_anchors(sentences)
    hedge_count = len(_HEDGE_RE.findall(norm_text_for_rates))
    booster_count = len(_BOOSTER_RE.findall(norm_text_for_rates))
    nominalization_count = len(_NOMINALIZATION_CHAIN_RE.findall(norm_text_for_rates))

    def per_100w(cnt: int) -> float:
        return round(cnt * 100.0 / word_count, 2) if word_count > 0 else 0.0

    importance_without_mechanism: list[dict[str, Any]] = []
    hedge_booster_collisions: list[dict[str, Any]] = []
    for sent in posture_sentences:
        sent_norm = sent.text.replace("\u2019", "'")
        imp_match = _IMPORTANCE_TRIGGER_RE.search(sent_norm)
        if imp_match and not _MECHANISM_MARKER_RE.search(sent_norm):
            importance_without_mechanism.append(
                {
                    "line": sent.line,
                    "trigger": re.sub(r"\s+", " ", imp_match.group(0)).strip().lower(),
                    "excerpt": _make_excerpt(sent.text),
                }
            )
        h_match = _HEDGE_RE.search(sent_norm)
        b_match = _BOOSTER_RE.search(sent_norm)
        if h_match and b_match:
            hedge_booster_collisions.append(
                {
                    "line": sent.line,
                    "hedge": h_match.group(0).lower(),
                    "booster": b_match.group(0).lower(),
                    "excerpt": _make_excerpt(sent.text),
                }
            )

    # Mechanics and tells on masked raw lines
    em_dashes: list[dict[str, Any]] = []
    emoji_bullets: list[dict[str, Any]] = []
    for idx, mline in enumerate(masked_lines):
        if not mline.strip():
            continue
        no_code = _strip_md.mask_inline_syntax_for_tells(mline)
        em_cnt = no_code.count(_EM_DASH_CHAR)
        if em_cnt > 0:
            em_dashes.append(
                {
                    "line": idx + 1,
                    "count": em_cnt,
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )
        if _EMOJI_BULLET_RE.match(no_code):
            emoji_bullets.append(
                {
                    "line": idx + 1,
                    "excerpt": _make_excerpt(raw_lines[idx]),
                }
            )

    connector_colons = _detect_connector_colons(masked_lines, raw_lines)
    bold_restatement_bullets = _detect_bold_restatement_bullets(masked_lines, raw_lines)
    false_scales = _detect_false_scales(masked_lines, raw_lines)
    ai_tell_words = _scan_line_regex(_AI_TELL_WORDS_RE, masked_lines, raw_lines)
    inflated_style_verbs = _scan_inflated_verbs(masked_lines, raw_lines)
    tech_buzz_nouns = _scan_line_regex(_TECH_BUZZ_NOUNS_RE, masked_lines, raw_lines)
    framing_theater = _scan_line_regex(
        _FRAMING_THEATER_RE,
        masked_lines,
        raw_lines,
        normalize_quotes=True,
        strip_leading_marker=True,
    )
    contrastive_pivots = _scan_line_regex(
        _CONTRASTIVE_PIVOT_RE, masked_lines, raw_lines, normalize_quotes=True
    )
    contrastive_pivots.extend(_detect_split_contrastive_pivots(posture_sentences))
    contrastive_pivots.sort(key=lambda item: int(item["line"]))

    participial_tail_puffery = _detect_participial_tail_puffery(
        posture_sentences, sentences, raw_lines
    )
    copula_avoidance = _scan_line_regex(
        _COPULA_AVOIDANCE_RE, masked_lines, raw_lines, normalize_quotes=True
    )
    rhetorical_qa_pivots = _detect_rhetorical_qa_pivots(posture_sentences)
    performative_fragments = _detect_performative_fragments(
        posture_sentences, raw_lines
    )
    stacked_questions = _detect_stacked_questions(sentences)
    shorthand_ambiguities = _scan_line_regex(
        _SHORTHAND_AMBIGUITY_RE, masked_lines, raw_lines
    )
    exclamation_marks = _detect_exclamation_marks(masked_lines, raw_lines)
    false_agency = _detect_false_agency(masked_lines, raw_lines)
    passive_count = _count_passive_voice(sentences)
    adverb_count = _count_adverbs(all_words)

    profile_checks = _evaluate_profile_checks(
        profile=profile,
        text=text,
        raw=raw,
        paragraphs_with_lines=paragraphs_with_lines,
        masked_lines=masked_lines,
        raw_lines=raw_lines,
        body_sent_lengths=body_sent_lengths,
        body_sent_cv=body_sent_cv,
    )

    report: dict[str, Any] = {
        "source": source,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "cadence": {
            "mean_sentence_words": mean_sentence_words,
            "body_sentence_cv": round(body_sent_cv, 3),
            "paragraph_word_cv": round(para_cv, 3),
            "cadence_masking": cadence_masking,
            "overloaded_sentences": overloaded_sentences,
            "ari_grade": ari_grade,
            "flesch_kincaid_grade": fk_grade,
        },
        "lexical_diversity": {
            "mattr_50": mattr_50,
            "repeated_trigram_rate": repeated_trigram_rate,
            "repeated_trigrams": repeated_trigrams,
        },
        "substance_and_posture": {
            "anchors_per_100w": per_100w(anchor_count),
            "hedges_per_100w": per_100w(hedge_count),
            "boosters_per_100w": per_100w(booster_count),
            "importance_without_mechanism": importance_without_mechanism,
            "hedge_booster_collisions": hedge_booster_collisions,
        },
        "mechanics_and_tells": {
            "em_dashes": em_dashes,
            "connector_colons": connector_colons,
            "bold_restatement_bullets": bold_restatement_bullets,
            "emoji_bullets": emoji_bullets,
            "hard_wrapped_lines": md_struct.hard_wrapped_lines,
            "false_scales": false_scales,
            "ai_tell_words": ai_tell_words,
            "inflated_style_verbs": inflated_style_verbs,
            "tech_buzz_nouns": tech_buzz_nouns,
            "framing_theater": framing_theater,
            "contrastive_pivots": contrastive_pivots,
            "participial_tail_puffery": participial_tail_puffery,
            "copula_avoidance": copula_avoidance,
            "rhetorical_qa_pivots": rhetorical_qa_pivots,
            "performative_fragments": performative_fragments,
            "stacked_questions": stacked_questions,
            "shorthand_ambiguities": shorthand_ambiguities,
            "exclamation_marks": exclamation_marks,
            "false_agency": false_agency,
            "passive_voice_per_100w": per_100w(passive_count),
            "adverbs_per_100w": per_100w(adverb_count),
            "nominalizations_per_100w": per_100w(nominalization_count),
        },
    }
    if profile_checks is not None:
        report["profile_checks"] = profile_checks
    return report


def format_human_report(report: dict[str, Any]) -> str:
    """Format a compact, actionable human-readable diagnostic report."""
    cad = report["cadence"]
    lex = report["lexical_diversity"]
    sub = report["substance_and_posture"]
    mech = report["mechanics_and_tells"]

    lines = [
        f"Prose Lint: {report['source']}",
        (
            f"  Counts: {report['word_count']} words, "
            f"{report['sentence_count']} sentences, "
            f"{report['paragraph_count']} paragraphs"
        ),
        (
            f"  Cadence: mean={cad['mean_sentence_words']}w, "
            f"body_cv={cad['body_sentence_cv']}, "
            f"para_cv={cad['paragraph_word_cv']}, "
            f"masking={cad['cadence_masking']}, "
            f"ARI={cad['ari_grade']}, FK={cad['flesch_kincaid_grade']}"
        ),
        (
            f"  Lexical: MATTR-50={lex['mattr_50']}, "
            f"repeated_3gram_rate={lex['repeated_trigram_rate']} "
            f"({len(lex['repeated_trigrams'])} repeated)"
        ),
        (
            f"  Substance: anchors={sub['anchors_per_100w']}/100w, "
            f"hedges={sub['hedges_per_100w']}/100w, "
            f"boosters={sub['boosters_per_100w']}/100w, "
            f"passive={mech['passive_voice_per_100w']}/100w, "
            f"adverbs={mech['adverbs_per_100w']}/100w, "
            f"nominalizations={mech['nominalizations_per_100w']}/100w"
        ),
    ]

    findings: list[str] = []
    profile_checks = report.get("profile_checks")
    if isinstance(profile_checks, dict):
        prof = profile_checks["profile"]
        req = profile_checks.get("requested_profile")
        prof_label = f"{req} -> {prof}" if req and req != prof else prof
        status = "PASS" if profile_checks["passed"] else "REVIEW"
        if prof == "technical":
            lines.append(
                f"  Profile ({prof_label}): {status} "
                f"(overlong_steps={len(profile_checks['overlong_steps'])}, "
                f"date_time_issues={len(profile_checks['date_time_issues'])})"
            )
            for item in profile_checks["overlong_steps"][:5]:
                findings.append(
                    f"  - L{item['line']} [overlong_step] ({item['words']}w > 20w): {item['excerpt']}"
                )
        elif prof in {"one-pager", "six-pager"}:
            budget_desc = (
                "350..550"
                if prof == "one-pager"
                else f"<={profile_checks['word_budget_max']}"
            )
            lines.append(
                f"  Profile ({prof_label}): {status} "
                f"(body_words={profile_checks['body_word_count']}/{budget_desc}, "
                f"prose_share={profile_checks['prose_paragraph_share']:.1%}, "
                f"date_time_issues={len(profile_checks['date_time_issues'])})"
            )
            if not profile_checks["word_budget_ok"]:
                target_desc = (
                    "target 350..550w"
                    if prof == "one-pager"
                    else f"ceiling {profile_checks['word_budget_max']}w"
                )
                findings.append(
                    f"  - [word_budget]: pre-Appendix body is {profile_checks['body_word_count']}w ({target_desc})"
                )
            if not profile_checks["prose_density_ok"]:
                findings.append(
                    f"  - [prose_density]: prose_paragraph_share={profile_checks['prose_paragraph_share']:.1%} "
                    f"(< {profile_checks['min_prose_share']:.0%} minimum)"
                )
        elif prof == "narrative":
            lines.append(
                f"  Profile ({prof_label}): {status} "
                f"(prose_share={profile_checks['prose_paragraph_share']:.1%}, "
                f"body_cv={profile_checks['body_sentence_cv']})"
            )
            if not profile_checks["prose_density_ok"]:
                findings.append(
                    f"  - [prose_density]: prose_paragraph_share={profile_checks['prose_paragraph_share']:.1%} "
                    f"(< {profile_checks['min_prose_share']:.0%} minimum)"
                )
            if not profile_checks["cadence_ok"]:
                findings.append(
                    f"  - [narrative_cadence]: body_sentence_cv={profile_checks['body_sentence_cv']} "
                    f"(< 0.30 across {profile_checks['body_sentence_count']} body sentences)"
                )

        for item in profile_checks.get("date_time_issues", [])[:5]:
            findings.append(
                f"  - L{item['line']} [date_time_issue] ({item['match']}): {item['excerpt']}"
            )

    for item in cad["overloaded_sentences"][:5]:
        findings.append(
            f"  - L{item['line']} [overloaded_sentence] ({item['words']}w): {item['excerpt']}"
        )
    if lex["repeated_trigrams"]:
        top_tri = ", ".join(
            f"\"{t['trigram']}\" ({t['count']}x)" for t in lex["repeated_trigrams"][:5]
        )
        findings.append(f"  - [repeated_trigrams]: {top_tri}")
    for item in sub["importance_without_mechanism"][:5]:
        findings.append(
            f"  - L{item['line']} [importance_without_mechanism] ({item['trigger']}): {item['excerpt']}"
        )
    for item in sub["hedge_booster_collisions"][:5]:
        findings.append(
            f"  - L{item['line']} [hedge_booster_collision] ({item['hedge']} + {item['booster']}): {item['excerpt']}"
        )
    if mech["hard_wrapped_lines"]:
        line_str = ", ".join(str(n) for n in mech["hard_wrapped_lines"][:10])
        findings.append(f"  - [hard_wrapped_lines]: lines {line_str}")

    labeled_categories = [
        ("em_dashes", "em_dash"),
        ("connector_colons", "connector_colon"),
        ("bold_restatement_bullets", "bold_restatement"),
        ("emoji_bullets", "emoji_bullet"),
        ("false_scales", "false_scale"),
        ("ai_tell_words", "ai_tell_word"),
        ("inflated_style_verbs", "inflated_verb"),
        ("tech_buzz_nouns", "tech_buzz_noun"),
        ("framing_theater", "framing_theater"),
        ("contrastive_pivots", "contrastive_pivot"),
        ("participial_tail_puffery", "participial_tail_puffery"),
        ("copula_avoidance", "copula_avoidance"),
        ("rhetorical_qa_pivots", "rhetorical_qa_pivot"),
        ("performative_fragments", "performative_fragment"),
        ("stacked_questions", "stacked_questions"),
        ("shorthand_ambiguities", "shorthand_ambiguity"),
        ("exclamation_marks", "exclamation_mark"),
        ("false_agency", "false_agency"),
    ]
    for key, label in labeled_categories:
        for item in mech[key][:5]:
            detail = item.get("match") or item.get("term") or ""
            suffix = f" ({detail})" if detail else ""
            findings.append(f"  - L{item['line']} [{label}]{suffix}: {item['excerpt']}")

    if findings:
        lines.append("  Findings:")
        lines.extend(findings)
    else:
        lines.append("  Findings: none")

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prose_lint.py",
        description=(
            "Run stylometric and mechanical prose diagnostics without a composite AI score."
        ),
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Input file path(s), or '-' / omitted to read from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit JSON report (single object for one input, list for multiple).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Analyze raw text without stripping Markdown syntax first.",
    )
    parser.add_argument(
        "--profile",
        "--mode",
        dest="profile",
        choices=list(VALID_PROFILES),
        default="default",
        help=(
            "Optional genre validation profile (default, technical, memo, "
            "one-pager, six-pager, narrative)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    active_profile: str | None = None if args.profile == "default" else args.profile

    targets = args.files if args.files else ["-"]
    stdin_cache: str | None = None
    reports: list[dict[str, Any]] = []

    for target in targets:
        if target == "-":
            if stdin_cache is None:
                stdin_cache = sys.stdin.read()
            reports.append(
                analyze_text(
                    stdin_cache,
                    source="<stdin>",
                    raw=args.raw,
                    profile=active_profile,
                )
            )
        else:
            path = Path(target)
            try:
                if not path.is_file():
                    print(f"error: file not found: {target}", file=sys.stderr)
                    return 2
                content = path.read_text(encoding="utf-8")
            except OSError as exc:
                print(f"error: cannot read {target}: {exc}", file=sys.stderr)
                return 2
            reports.append(
                analyze_text(
                    content,
                    source=target,
                    raw=args.raw,
                    profile=active_profile,
                )
            )

    if args.as_json:
        payload: Any = reports[0] if len(reports) == 1 else reports
        print(json.dumps(payload, indent=2))
    else:
        print("\n\n".join(format_human_report(r) for r in reports))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

