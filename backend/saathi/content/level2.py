from ..lessonbase import Lesson

LESSONS = [
Lesson(
 "2.1", 2, "Cases", "Instrumental and dative", "तृतीया-चतुर्थी", 15,
 "Say 'by/with' and 'to/for' with the instrumental and dative cases.",
 """### तृतीया (instrumental): by, with, by means of
| | Masculine / neuter -अ |
|---|---|
| Singular | रामेण, फलेन |
| Plural | रामैः, फलैः |

Uses:
- **means or tool:** सः पुस्तकेन पठति। (he studies with a book)
- **accompaniment**, with **सह** (with): रामः मित्रेण सह गच्छति। (Rama goes with a friend)
- **the agent** in passive-type sentences: रामेण फलं खादितम्। (the fruit was eaten by Rama)

### चतुर्थी (dative): to, for
| | Masculine / neuter -अ |
|---|---|
| Singular | रामाय, फलाय |
| Plural | रामेभ्यः, फलेभ्यः |

Uses: the **recipient** or **purpose**: फलं बालकाय अस्ति। (the fruit is for the boy) · सः पठनाय विद्यालयं गच्छति। (he goes to school for studying)

**Retroflex shift:** the ending -एन turns into -एण after र, ष, ऋ: रामेण, not *रामेन*.""",
 vocab=[("सह", "with"), ("मित्रम्", "friend"), ("गृहम्", "house"), ("नगरम्", "city"), ("वनम्", "forest"), ("जलम्", "water")],
 examples=[("रामः मित्रेण सह गच्छति।", "Rama goes with a friend."), ("रामेण फलं खादितम्।", "The fruit was eaten by Rama.")],
 questions=[
  ("**रामेण** means", "by/with Rama", ["to Rama", "of Rama", "from Rama"], "-एन/-एण is the instrumental singular."),
  ("'For the boy' =", "बालकाय", ["बालकेन", "बालकस्य", "बालकात्"], "-आय is the dative singular."),
  ("'With a friend' =", "मित्रेण सह", ["मित्राय सह", "मित्रस्य सह", "मित्रम् सह"], "सह takes the instrumental."),
  ("Why is it रामेण and not रामेन?", "र causes the retroflex ण", ["Sanskrit has no न", "It is dative", "It is a plural"], "न becomes ण after र, ष, ऋ."),
  ("The dative plural of राम is", "रामेभ्यः", ["रामैः", "रामाणाम्", "रामेषु"], "-एभ्यः is dative/ablative plural."),
 ],
 drills=[("decl", {"cases": [3, 4]}), ("identify", {"cases": [3, 4]})],
),
Lesson(
 "2.2", 2, "Cases", "Ablative, genitive, locative, vocative", "पञ्चमी-षष्ठी-सप्तमी-सम्बोधनम्", 15,
 "Complete the case system with 'from', 'of', 'in/on' and direct address.",
 """### पञ्चमी (ablative): from
रामात् (from Rama), गृहात् (from the house). Plural: रामेभ्यः.
सः गृहात् वनं गच्छति। He goes from the house to the forest.

### षष्ठी (genitive): of
रामस्य (of Rama). Plural: रामाणाम्.
रामस्य पुस्तकम् अस्ति। Rama has a book (lit. "of Rama a book is").

### सप्तमी (locative): in, on, at
रामे, गृहे (in the house), वने (in the forest). Plural: रामेषु.
वने मृगः अस्ति। There is a deer in the forest.

### सम्बोधनम् (vocative): addressing someone
Put **हे** before the vocative: हे राम! (O Rama). For -अ nouns the vocative singular is the bare stem: राम, बालक.

### The whole singular, for राम
| Case | Form |
|---|---|
| 1 प्रथमा | रामः |
| 2 द्वितीया | रामम् |
| 3 तृतीया | रामेण |
| 4 चतुर्थी | रामाय |
| 5 पञ्चमी | रामात् |
| 6 षष्ठी | रामस्य |
| 7 सप्तमी | रामे |
| 8 सम्बोधनम् | हे राम |""",
 vocab=[("मृगः", "deer, animal"), ("वनम्", "forest"), ("नगरम्", "city"), ("ग्रामः", "village"), ("वृक्षः", "tree"), ("पुत्रः", "son")],
 examples=[("सः गृहात् वनं गच्छति।", "He goes from the house to the forest."), ("वने मृगः अस्ति।", "There is a deer in the forest.")],
 questions=[
  ("'From the house' =", "गृहात्", ["गृहे", "गृहस्य", "गृहाय"], "-आत् is ablative."),
  ("'Of Rama' =", "रामस्य", ["रामात्", "रामे", "रामाय"], "-स्य is genitive."),
  ("'In the forest' =", "वने", ["वनात्", "वनस्य", "वनम्"], "-ए is locative singular."),
  ("The vocative of राम is", "हे राम", ["हे रामः", "हे रामम्", "हे रामेण"], "The vocative singular of -अ nouns drops the ending."),
  ("Which case answers 'whose?'", "genitive (षष्ठी)", ["dative (चतुर्थी)", "locative (सप्तमी)", "ablative (पञ्चमी)"], "Genitive shows possession/relation."),
 ],
 drills=[("decl", {"cases": [5, 6, 7]}), ("identify", {"cases": [5, 6, 7]})],
),
Lesson(
 "2.3", 2, "Cases", "Feminine nouns and adjective agreement", "स्त्रीलिङ्गम्", 18,
 "Decline feminine -आ nouns and make adjectives agree in gender, number and case.",
 """### Feminine -आ stems: लता (creeper)
| Case | Singular | Dual | Plural |
|---|---|---|---|
| 1 | लता | लते | लताः |
| 2 | लताम् | लते | लताः |
| 3 | लतया | लताभ्याम् | लताभिः |
| 4 | लतायै | लताभ्याम् | लताभ्यः |
| 5 | लतायाः | लताभ्याम् | लताभ्यः |
| 6 | लतायाः | लतयोः | लतानाम् |
| 7 | लतायाम् | लतयोः | लतासु |
| 8 | लते | लते | लताः |

### Agreement
An adjective copies the **gender, number and case** of the noun it describes:
- सुन्दरः बालकः (m.) · सुन्दरी बालिका (f.) · सुन्दरं फलम् (n.)
- सुन्दराः बालकाः (m. pl.) · सुन्दर्यः बालिकाः (f. pl.)
- सुन्दरं बालकं पश्यति। He sees the beautiful boy. (acc. m.)

Most adjectives in -अ take the feminine in -आ (प्रिया) or -ई (सुन्दरी).""",
 vocab=[("बालिका", "girl"), ("लता", "creeper"), ("कन्या", "girl, daughter"), ("विद्या", "knowledge"), ("सुन्दर", "beautiful"), ("प्रिय", "dear")],
 examples=[("सुन्दरी बालिका गच्छति।", "The beautiful girl goes."), ("सा विद्यां पठति।", "She studies knowledge/learning.")],
 questions=[
  ("The accusative singular of लता is", "लताम्", ["लता", "लतया", "लतायाः"], "Feminine -आ takes -ाम् in the accusative."),
  ("'Beautiful girl' (nominative)", "सुन्दरी बालिका", ["सुन्दरः बालिका", "सुन्दरं बालिका", "सुन्दराः बालिका"], "The adjective is feminine to match बालिका."),
  ("The genitive singular of लता is", "लतायाः", ["लतायाम्", "लतया", "लतानाम्"], "Genitive/ablative singular: -ायाः."),
  ("'Beautiful fruit' =", "सुन्दरं फलम्", ["सुन्दरः फलम्", "सुन्दरी फलम्", "सुन्दरा फलम्"], "फलम् is neuter, so the adjective is neuter."),
  ("The locative singular of कन्या is", "कन्यायाम्", ["कन्यायाः", "कन्यया", "कन्यायै"], "Locative -ायाम्."),
 ],
 drills=[("decl", {"cases": [1, 2, 3, 6, 7], "classes": ["A"]})],
),
Lesson(
 "2.4", 2, "Verbs", "Past, future and imperative", "लङ्-लृट्-लोट्", 18,
 "Form the imperfect (past), future and imperative of regular verbs.",
 """For **√गम्** (stem गच्छ-):

| | Present | **Imperfect** (past) | **Future** | **Imperative** |
|---|---|---|---|---|
| 3rd sg. | गच्छति | **अ**गच्छत् | गमिष्यति | गच्छतु |
| 2nd sg. | गच्छसि | अगच्छः | गमिष्यसि | गच्छ |
| 1st sg. | गच्छामि | अगच्छम् | गमिष्यामि | गच्छानि |
| 3rd pl. | गच्छन्ति | अगच्छन् | गमिष्यन्ति | गच्छन्तु |

- **Imperfect (लङ्):** add the prefix **अ-** to the stem and use "past" endings: -त्, -ताम्, -न्. It tells a past event: रामः अगच्छत्। Rama went.
- **Future (लृट्):** stem + **इष्य**: पठिष्यति (will read), but each root has its own future stem (गमिष्यति, द्रक्ष्यति for √दृश्).
- **Imperative (लोट्):** commands and wishes. गच्छ! (go!), गच्छतु (let him go), पठतु (may he read).

In classical literature the past is often told with participles (see lesson 3.4).""",
 vocab=[("अगच्छत्", "went"), ("गमिष्यति", "will go"), ("पठिष्यति", "will read"), ("पठतु", "let him read"), ("अवदत्", "said")],
 examples=[("रामः अगच्छत्।", "Rama went."), ("सः पठिष्यति।", "He will read.")],
 questions=[
  ("'He went' (imperfect) =", "अगच्छत्", ["गच्छति", "गमिष्यति", "गच्छतु"], "Imperfect adds अ- and -त्."),
  ("'He will go' =", "गमिष्यति", ["अगच्छत्", "गच्छति", "गच्छेत्"], "Future uses -इष्य."),
  ("'Go!' (to one person) =", "गच्छ", ["गच्छति", "अगच्छत्", "गमिष्यसि"], "The 2nd sg. imperative of thematic verbs is the bare stem."),
  ("'I will read' =", "पठिष्यामि", ["पठामि", "अपठम्", "पठानि"], "Future 1st sg.: पठिष्यामि."),
  ("The prefix अ- in अगच्छत् marks…", "past (imperfect)", ["future", "command", "question"], "अ- is the augment of the imperfect."),
 ],
 drills=[("conj", {"tenses": ["lan", "lrt", "lot"]})],
),
Lesson(
 "2.5", 2, "Verbs", "Dual, plural and verb agreement", "द्विवचनं बहुवचनं च", 15,
 "Use all three numbers and make the verb agree.",
 """### Three numbers
| | Singular | Dual | Plural |
|---|---|---|---|
| Noun (राम) | रामः | रामौ | रामाः |
| Noun (फल) | फलम् | फले | फलानि |
| Verb (पठ्) | पठति | पठतः | पठन्ति |

Use the **dual** for exactly two: रामलक्ष्मणौ गच्छतः। (Rama and Lakshmana go.)

### Agreement
The verb copies the subject's **person and number**:
- बालकः गच्छति · बालकौ गच्छतः · बालकाः गच्छन्ति
- When the subject is "I" or "you" the verb is 1st or 2nd person: अहं पठामि, त्वं पठसि, वयं पठामः.

### Other plural forms of राम
Accusative plural रामान्, instrumental रामैः, dative/ablative रामेभ्यः, genitive रामाणाम्, locative रामेषु.

Neuter plural nominative/accusative ends in **-आनि**: फलानि, पुस्तकानि.""",
 vocab=[("बालकौ", "two boys"), ("बालकाः", "boys"), ("फलानि", "fruits"), ("छात्राः", "students"), ("पुस्तकानि", "books")],
 examples=[("बालकाः विद्यालयं गच्छन्ति।", "The boys go to school."), ("छात्रौ पठतः।", "The two students read.")],
 questions=[
  ("'Two boys' (nominative) =", "बालकौ", ["बालकाः", "बालकः", "बालकान्"], "-औ is the dual."),
  ("'The boys go' =", "बालकाः गच्छन्ति।", ["बालकाः गच्छति।", "बालकौ गच्छन्ति।", "बालकः गच्छन्ति।"], "Plural subject, plural verb."),
  ("'We two read' =", "आवां पठावः।", ["वयं पठावः।", "आवां पठामः।", "अहं पठावः।"], "आवाम् (we two) takes the dual -आवः."),
  ("The neuter plural of फलम् is", "फलानि", ["फलाः", "फलौ", "फले"], "Neuter plural: -आनि."),
  ("Accusative plural of राम:", "रामान्", ["रामाः", "रामम्", "रामैः"], "-आन् is masculine accusative plural."),
 ],
 drills=[("decl", {"cases": [1, 2, 3], "numbers": ["du", "pl"]}), ("conj", {"tenses": ["lat"]})],
),
Lesson(
 "2.6", 2, "Joining ideas", "Particles, conjunctions and adverbs", "अव्ययानि", 12,
 "Use the small words that never change: and, or, also, not, here, there, if…then.",
 """**अव्ययानि** ("indeclinables") never change form.

| Word | Meaning | Example |
|---|---|---|
| च | and (placed *after*) | रामः लक्ष्मणः च। |
| वा | or | फलं वा जलं वा? |
| अपि | also, even | सः अपि गच्छति। |
| एव | only, indeed | रामः एव गच्छति। |
| न | not | सः न गच्छति। |
| तु / किन्तु | but | अहं पठामि, सः तु लिखति। |
| हि | for, indeed | |
| यदि … तर्हि | if … then | यदि सः गच्छति तर्हि अहं गच्छामि। |
| अत्र / तत्र / कुत्र | here / there / where | |
| अद्य / श्वः / ह्यः | today / tomorrow / yesterday | |
| सदा | always | |
| इति | "…", thus (closes a quotation) | |

**च** comes after the word it joins (X Y च) and may appear after both: रामः च लक्ष्मणः च.
**इति** marks speech or thought: सः "गच्छामि" इति वदति। He says "I am going."

The word order is flexible but the verb stays near the end.""",
 vocab=[("च", "and"), ("वा", "or"), ("अपि", "also"), ("एव", "only, indeed"), ("न", "not"), ("यदि", "if"), ("अत्र", "here"), ("तत्र", "there"), ("अद्य", "today"), ("सदा", "always")],
 examples=[("रामः लक्ष्मणः च गच्छतः।", "Rama and Lakshmana go."), ("अद्य सः गृहे न अस्ति।", "Today he is not at home.")],
 questions=[
  ("**अपि** means", "also, even", ["not", "or", "here"], "अपि = also."),
  ("'If … then' =", "यदि … तर्हि", ["च … वा", "अत्र … तत्र", "न … एव"], "यदि = if; तर्हि = then."),
  ("'Here' =", "अत्र", ["तत्र", "कुत्र", "अद्य"], "अत्र = here; तत्र = there."),
  ("Where is **च** placed?", "after the word it joins", ["before the word", "at the start of the sentence", "it can't be placed"], "च follows the word."),
  ("**इति** is used…", "to close a quotation", ["to mean 'and'", "to mean 'not'", "only with numbers"], "इति ends a quote: 'X' इति वदति."),
 ],
),
]
