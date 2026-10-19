"""Built-in lexicon (SLP1). Small but verified: every entry is declined/conjugated by rule.

Add entries here to grow coverage; the morphology engine generates all forms.
"""

# (stem, declension class, gender, gloss)
# classes: a (a-stem), A (ā-stem), i, I (ī-stem), u
NOUNS = [
    # a-stem masculine
    ("rAma", "a", "m", "Rama"), ("CAtra", "a", "m", "student"), ("bAlaka", "a", "m", "boy"),
    ("deva", "a", "m", "god"), ("puruza", "a", "m", "man"), ("vfkza", "a", "m", "tree"),
    ("grAma", "a", "m", "village"), ("nfpa", "a", "m", "king"), ("Darma", "a", "m", "duty, righteousness"),
    ("AcArya", "a", "m", "teacher"), ("gaja", "a", "m", "elephant"), ("aSva", "a", "m", "horse"),
    ("sUrya", "a", "m", "sun"), ("candra", "a", "m", "moon"), ("mfga", "a", "m", "deer, animal"),
    ("putra", "a", "m", "son"), ("Sabda", "a", "m", "word, sound"), ("arTa", "a", "m", "meaning, wealth"),
    ("loka", "a", "m", "world, people"), ("kAla", "a", "m", "time"), ("kfzRa", "a", "m", "Krishna; black"),
    ("DanyavAda", "a", "m", "thanks"), ("kAka", "a", "m", "crow"), ("gfDra", "a", "m", "vulture"),
    ("vAnara", "a", "m", "monkey"), ("lakzmaRa", "a", "m", "Lakshmana"),
    # a-stem neuter
    ("Pala", "a", "n", "fruit"), ("pustaka", "a", "n", "book"), ("vidyAlaya", "a", "n", "school"),
    ("mitra", "a", "n", "friend"), ("saMskfta", "a", "n", "Sanskrit"), ("gfha", "a", "n", "house"),
    ("jala", "a", "n", "water"), ("puzpa", "a", "n", "flower"), ("patra", "a", "n", "leaf, letter"),
    ("vana", "a", "n", "forest"), ("nagara", "a", "n", "city"), ("kArya", "a", "n", "work, task"),
    ("jYAna", "a", "n", "knowledge"), ("muKa", "a", "n", "face, mouth"), ("padma", "a", "n", "lotus"),
    ("Dana", "a", "n", "wealth"), ("kzetra", "a", "n", "field"), ("dugDa", "a", "n", "milk"),
    ("kAvya", "a", "n", "poem"), ("anna", "a", "n", "food"), ("Bojana", "a", "n", "meal"),
    ("vacana", "a", "n", "statement, word"), ("gIta", "a", "n", "song"), ("stotra", "a", "n", "hymn"),
    ("sUtra", "a", "n", "aphorism, thread"), ("ratna", "a", "n", "jewel"), ("svarRa", "a", "n", "gold"),
    ("suKa", "a", "n", "happiness"),
    # ā-stem feminine
    ("latA", "A", "f", "creeper"), ("bAlikA", "A", "f", "girl"), ("kanyA", "A", "f", "girl, daughter"),
    ("vidyA", "A", "f", "knowledge"), ("SAlA", "A", "f", "hall"), ("sevA", "A", "f", "service"),
    ("BAzA", "A", "f", "language"), ("kaTA", "A", "f", "story"), ("CAyA", "A", "f", "shadow"),
    ("mAlA", "A", "f", "garland"), ("senA", "A", "f", "army"), ("pUjA", "A", "f", "worship"),
    ("kriyA", "A", "f", "action"), ("pAWaSAlA", "A", "f", "school"), ("gaMgA", "A", "f", "the Ganga"),
    ("sItA", "A", "f", "Sita"), ("SikzA", "A", "f", "education, phonetics"), ("vIRA", "A", "f", "veena"),
    # i-stem masculine
    ("hari", "i", "m", "Hari, Vishnu"), ("kavi", "i", "m", "poet"), ("muni", "i", "m", "sage"),
    ("agni", "i", "m", "fire"), ("ravi", "i", "m", "sun"), ("kapi", "i", "m", "monkey"),
    ("pati", "i", "m", "lord, husband"), ("atiTi", "i", "m", "guest"),
    # i-stem feminine
    ("mati", "i", "f", "mind, thought"), ("rAtri", "i", "f", "night"), ("BUmi", "i", "f", "earth"),
    ("SAnti", "i", "f", "peace"), ("budDi", "i", "f", "intelligence"), ("dfzwi", "i", "f", "sight"),
    ("nIti", "i", "f", "policy, ethics"), ("Bakti", "i", "f", "devotion"),
    # ī-stem feminine
    ("nadI", "I", "f", "river"), ("devI", "I", "f", "goddess"), ("kumArI", "I", "f", "girl"),
    ("gOrI", "I", "f", "Gauri, Parvati"), ("nArI", "I", "f", "woman"), ("lakzmI", "I", "f", "Lakshmi"),
    # u-stem masculine
    ("guru", "u", "m", "teacher"), ("Sizu", "u", "m", "child"), ("sADu", "u", "m", "good person"),
    ("hetu", "u", "m", "reason"), ("vAyu", "u", "m", "wind"), ("BAnu", "u", "m", "sun"),
    ("Bikzu", "u", "m", "mendicant"), ("Satru", "u", "m", "enemy"), ("vizRu", "u", "m", "Vishnu"),
]

# a-stem adjectives (declined in all three genders): (stem, gloss, feminine stems)
ADJECTIVES = [
    ("sundara", "beautiful", ["sundarI", "sundarA"]), ("priya", "dear", ["priyA"]),
    ("uttama", "best, excellent", ["uttamA"]), ("SuBa", "auspicious", ["SuBA"]),
    ("dIrGa", "long", ["dIrGA"]), ("alpa", "small, little", ["alpA"]),
    ("navIna", "new", ["navInA"]), ("pUrRa", "full, complete", ["pUrRA"]),
    ("ramya", "pleasant", ["ramyA"]), ("maDura", "sweet", ["maDurA"]),
    ("vIra", "brave", ["vIrA"]), ("kuSala", "skilful", ["kuSalA"]),
    ("svacCa", "clean", ["svacCA"]), ("kzudra", "tiny, petty", ["kzudrA"]),
    ("sarala", "simple", ["saralA"]), ("kaWina", "hard, difficult", ["kaWinA"]),
    ("sulaBa", "easy to get", ["sulaBA"]), ("Sukla", "white", ["SuklA"]),
    ("nIla", "blue", ["nIlA"]), ("rakta", "red", ["raktA"]),
]

# Pronouns of the sarvanāman a-stem type: (stem, lemma, gloss, masc nom sg, fem nom sg, neut nom/acc sg)
PRONOUNS_A = [
    ("ta", "tad", "that; he/she/it", "saH", "sA", "tat"),
    ("eta", "etad", "this", "eSaH", "eSA", "etat"),
    ("ka", "kim", "who? what?", "kaH", "kA", "kim"),
    ("ya", "yad", "who, which (relative)", "yaH", "yA", "yat"),
    ("sarva", "sarva", "all, every", "sarvaH", "sarvA", "sarvam"),
    ("anya", "anya", "other", "anyaH", "anyA", "anyat"),
    ("eka", "eka", "one", "ekaH", "ekA", "ekam"),
]

# Verbs (parasmaipada). trans: transitive?  Past passive participle / gerund / infinitive listed.
# root, gloss, present stem, future stem, transitive, ppp, gerund, infinitive
VERBS = [
    ("gam", "go", "gacCa", "gamizya", False, "gata", "gatvA", "gantum"),
    ("paW", "read, recite", "paWa", "paWizya", True, "paWita", "paWitvA", "paWitum"),
    ("liK", "write", "liKa", "liKizya", True, "liKita", "liKitvA", "liKitum"),
    ("KAd", "eat", "KAda", "KAdizya", True, "KAdita", "KAditvA", "KAditum"),
    ("vad", "speak, say", "vada", "vadizya", True, "ukta", "uktvA", "vaditum"),
    ("BU", "be, become", "Bava", "Bavizya", False, "BUta", "BUtvA", "Bavitum"),
    ("pA", "drink", "piba", "pAsya", True, "pIta", "pItvA", "pAtum"),
    ("dfS", "see", "paSya", "drakzya", True, "dfzwa", "dfzwvA", "drazwum"),
    ("sTA", "stand", "tizWa", "sTAsya", False, "sTita", "sTitvA", "sTAtum"),
    ("pac", "cook", "paca", "pakzya", True, "pakva", "paktvA", "paktum"),
    ("nI", "lead, carry", "naya", "nezya", True, "nIta", "nItvA", "netum"),
    ("smf", "remember", "smara", "smarizya", True, "smfta", "smftvA", "smartum"),
    ("vas", "dwell, live", "vasa", "vatsya", False, "uzita", "uzitvA", "vastum"),
    ("has", "laugh", "hasa", "hasizya", False, "hasita", "hasitvA", "hasitum"),
    ("cal", "move, walk", "cala", "calizya", False, "calita", "calitvA", "calitum"),
    ("DAv", "run", "DAva", "DAvizya", False, "DAvita", "DAvitvA", "DAvitum"),
    ("praC", "ask", "pfcCa", "prakzya", True, "pfzwa", "pfzwvA", "prazwum"),
]
# Irregular roots with hand-written tables live in morph.py: "as" (to be) and "kf" (to do).
IRREGULAR_VERB_META = {
    "as": ("be, exist", False, None, None, None),
    "kf": ("do, make", True, "kfta", "kftvA", "kartum"),
}

# Indeclinables: (form, gloss)
INDECLINABLES = [
    ("ca", "and"), ("vA", "or"), ("api", "also, even"), ("eva", "only, indeed"),
    ("iti", "thus (quote marker)"), ("na", "not"), ("tu", "but"), ("hi", "for, indeed"),
    ("atra", "here"), ("tatra", "there"), ("kutra", "where?"), ("yatra", "where (relative)"),
    ("sarvatra", "everywhere"), ("iha", "here"), ("kaTam", "how?"), ("kadA", "when?"),
    ("yadA", "when (relative)"), ("tadA", "then"), ("adya", "today"), ("SvaH", "tomorrow"),
    ("hyaH", "yesterday"), ("aTa", "now, then"), ("punaH", "again"), ("saha", "with"),
    ("vinA", "without"), ("ataH", "therefore, hence"), ("kintu", "but, however"),
    ("yadi", "if"), ("tarhi", "then, in that case"), ("sadA", "always"), ("SIGram", "quickly"),
    ("namaH", "salutation, bow"), ("namaste", "greetings (namaḥ + te: 'salutation to you')"),
    ("svAgatam", "welcome"), ("kfpayA", "please (lit. 'through kindness')"),
    ("BoH", "hey! sir!"), ("aho", "oh! ah!"), ("kutaH", "from where?"), ("tataH", "then, thence"),
    ("evam", "thus, so"), ("aDunA", "now"), ("ekadA", "once, one day"), ("bAQam", "certainly, OK"),
    ("mA", "don't (prohibitive)"), ("kim", "what? (also a question marker)"),
    ("samyak", "properly"), ("bahu", "much, many"),
]
