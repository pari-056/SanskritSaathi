from ..lessonbase import Lesson

LESSONS = [
Lesson(
 "3.1", 3, "More forms", "Stems in -इ, -उ and -ई", "इकारान्त-उकारान्तशब्दाः", 20,
 "Decline nouns ending in -i, -u and -ī, which are very common.",
 """### Masculine -इ: हरि (Hari)
| Case | Sg. | Du. | Pl. |
|---|---|---|---|
| 1 | हरिः | हरी | हरयः |
| 2 | हरिम् | हरी | हरीन् |
| 3 | हरिणा | हरिभ्याम् | हरिभिः |
| 4 | हरये | हरिभ्याम् | हरिभ्यः |
| 5 | हरेः | हरिभ्याम् | हरिभ्यः |
| 6 | हरेः | हर्योः | हरीणाम् |
| 7 | हरौ | हर्योः | हरिषु |
| 8 | हरे | हरी | हरयः |

### Masculine -उ: गुरु (teacher)
Same pattern: गुरुः, गुरुम्, गुरुणा, गुरवे, गुरोः, गुरोः, गुरौ, **हे गुरो**. Plural: गुरवः, गुरून्, गुरुभिः, गुरुभ्यः, गुरूणाम्, गुरुषु.

### Feminine -इ: मति (mind) and -ई: नदी (river)
- मतिः, मतिम्, **मत्या**, मतये / मत्यै, मतेः / मत्याः, मतीनाम्, मतौ / मत्याम्
- नदी, नदीम्, **नद्या**, नद्यै, नद्याः, नद्याः, **नद्याम्**; plural नद्यः, नदीः, नदीभिः, नदीनाम्, नदीषु

**Sound changes to notice:** the plural locative -सु becomes -षु after इ/उ (हरिषु); न becomes ण after र (हरिणा, गुरूणाम्).""",
 vocab=[("हरिः", "Hari, Vishnu"), ("कविः", "poet"), ("मुनिः", "sage"), ("अग्निः", "fire"), ("गुरुः", "teacher"), ("शिशुः", "child"), ("मतिः", "mind"), ("नदी", "river"), ("देवी", "goddess")],
 examples=[("हरिः गृहं गच्छति।", "Hari goes home."), ("गुरुः शिशुं पश्यति।", "The teacher sees the child.")],
 questions=[
  ("The instrumental singular of हरि is", "हरिणा", ["हरिना", "हरिम्", "हरये"], "-इ stems: -ना → -णा after र."),
  ("The nominative plural of गुरु is", "गुरवः", ["गुरवे", "गुरून्", "गुरोः"], "-उ stem nom. pl.: -अवः."),
  ("The genitive singular of नदी is", "नद्याः", ["नद्याम्", "नदीः", "नदीनाम्"], "Feminine -ई: -याः."),
  ("The vocative of हरि is", "हे हरे", ["हे हरिः", "हे हरिम्", "हे हरिणा"], "The vocative of -इ stems ends in -ए."),
  ("The accusative plural of मति is", "मतीः", ["मतयः", "मतिम्", "मतिभिः"], "Feminine -इ accusative plural: -ईः."),
 ],
 drills=[("decl", {"classes": ["i", "I", "u"]})],
),
Lesson(
 "3.2", 3, "More forms", "Pronoun declension", "सर्वनामशब्दाः", 18,
 "Decline तद् (that), एतद् (this), किम् (what), यद् (which) and the personal pronouns.",
 """### तद् (he / that) — masculine
| Case | Sg. | Du. | Pl. |
|---|---|---|---|
| 1 | सः | तौ | ते |
| 2 | तम् | तौ | तान् |
| 3 | तेन | ताभ्याम् | तैः |
| 4 | तस्मै | ताभ्याम् | तेभ्यः |
| 5 | तस्मात् | ताभ्याम् | तेभ्यः |
| 6 | तस्य | तयोः | तेषाम् |
| 7 | तस्मिन् | तयोः | तेषु |

Pronouns have special endings: **-स्मै, -स्मात्, -स्मिन्, -एषाम्**. एतद् (एषः "this"), किम् (कः "who/what") and यद् (यः "who, which") follow it: एतस्मै, कस्मिन्, येषाम्.
Feminine **सा**: ताम्, तया, तस्यै, तस्याः, तस्याः, तस्याम्. Neuter nominative/accusative: **तत्**.

### Personal pronouns
| Case | I | you |
|---|---|---|
| 1 | अहम् | त्वम् |
| 2 | माम् / मा | त्वाम् / त्वा |
| 3 | मया | त्वया |
| 4 | मह्यम् / मे | तुभ्यम् / ते |
| 5 | मत् | त्वत् |
| 6 | मम / मे | तव / ते |
| 7 | मयि | त्वयि |

The short forms (मा, मे, त्वा, ते) are **enclitic**: they never start a sentence.
**मम** "my" and **तव** "your" are the genitives: मम नाम रामः अस्ति। तव गृहं कुत्र अस्ति?""",
 vocab=[("तद्", "that, he/she/it"), ("एतद्", "this"), ("किम्", "what"), ("यद्", "which"), ("मम", "my"), ("तव", "your"), ("मया", "by me"), ("त्वया", "by you")],
 examples=[("तस्य नाम किम्?", "What is his name?"), ("मम गृहे फलम् अस्ति।", "There is a fruit in my house.")],
 questions=[
  ("**तस्य** means", "of him / his", ["to him", "by him", "from him"], "तस्य is the genitive singular of तद्."),
  ("'To him' =", "तस्मै", ["तस्य", "तस्मात्", "तेन"], "-स्मै is the dative of pronouns."),
  ("**मया** means", "by me", ["to me", "of me", "in me"], "मया is the instrumental of अस्मद्."),
  ("'My' (genitive of 'I') =", "मम", ["मया", "माम्", "मयि"], "मम = my."),
  ("**त्वयि** means", "in you", ["by you", "of you", "from you"], "-यि is the locative."),
 ],
 drills=[("identify", {"cases": [3, 4, 5, 6, 7]})],
),
Lesson(
 "3.3", 3, "More forms", "Optative, and the verbs कृ and अस्", "विधिलिङ्", 18,
 "Express 'should', 'would' and 'may' with the optative, and learn two key irregular verbs.",
 """### The optative (विधिलिङ्)
Used for **advice, wishes, possibility**: "should", "may", "would".

| | Singular | Dual | Plural |
|---|---|---|---|
| 3rd | पठेत् | पठेताम् | पठेयुः |
| 2nd | पठेः | पठेतम् | पठेत |
| 1st | पठेयम् | पठेव | पठेम |

- सः गच्छेत्। He should go / may go.
- **सत्यं वदेत्।** One should speak the truth.
- यदि सः पठेत् तर्हि जानीयात्। If he studied, he would know.

### √कृ (to do, make) — present
| | Sg. | Du. | Pl. |
|---|---|---|---|
| 3rd | करोति | कुरुतः | कुर्वन्ति |
| 2nd | करोषि | कुरुथः | कुरुथ |
| 1st | करोमि | कुर्वः | कुर्मः |

### √अस् optative
स्यात् (it may be), स्याः, स्याम्, स्युः. "May it be so": **तथास्तु** (तथा + अस्तु, imperative of अस्).""",
 vocab=[("करोति", "does, makes"), ("कुर्वन्ति", "they do"), ("स्यात्", "may be"), ("सत्यम्", "truth"), ("वदेत्", "should speak"), ("गच्छेत्", "should go")],
 examples=[("सः सत्यं वदेत्।", "He should speak the truth."), ("अहं कार्यं करोमि।", "I do the work.")],
 questions=[
  ("'He should go' =", "गच्छेत्", ["गच्छति", "अगच्छत्", "गमिष्यति"], "Optative 3rd sg.: -एत्."),
  ("**करोति** means", "does, makes", ["goes", "speaks", "is"], "√कृ = do/make."),
  ("'They do' =", "कुर्वन्ति", ["करोति", "कुरुतः", "कुर्मः"], "3rd plural of √कृ."),
  ("The optative 3rd singular of √अस् is", "स्यात्", ["अस्ति", "आसीत्", "अस्तु"], "स्यात् = may be / would be."),
  ("'I would read' =", "पठेयम्", ["पठामि", "पठानि", "अपठम्"], "Optative 1st sg.: -एयम्."),
 ],
 drills=[("conj", {"tenses": ["vidhilin"]}), ("conj", {"roots": ["kf", "as"], "tenses": ["lat", "lan", "lot", "vidhilin"]})],
),
Lesson(
 "3.4", 3, "More forms", "Participles, gerunds and infinitives", "कृदन्तानि", 20,
 "Use -त (past participle), -त्वा (having done), and -तुम् (to do).",
 """### Past passive participle (क्त)
Adds **-त / -इत** to the root: गत (gone), पठित (read), लिखित (written), खादित (eaten), उक्त (said), दृष्ट (seen), कृत (done), पीत (drunk), स्थित (stood).
It is declined like a noun/adjective in all genders: गतः, गता, गतम्.

Two uses:
1. **Passive** (transitive roots): the agent is *instrumental*, the object *nominative* and the participle agrees with the object.
   रामेण फलं खादितम्। *The fruit was eaten by Rama.*
2. **Active-past** (verbs of motion, being): the subject is nominative. रामः गतः। *Rama has gone.*

### Gerund (क्त्वा) — "having done …, then …"
-त्वा (indeclinable): गत्वा, पठित्वा, खादित्वा, उक्त्वा, दृष्ट्वा, कृत्वा.
**सः गृहं गत्वा पुस्तकं पठति।** Having gone home, he reads a book.

### Infinitive (तुमुन्) — "to do"
-तुम्: गन्तुम्, पठितुम्, खादितुम्, वदितुम्, द्रष्टुम्, कर्तुम्.
**सः पठितुं विद्यालयं गच्छति।** He goes to school to read.

All three share the root, so learn them with the verb: √गम् → गतः · गत्वा · गन्तुम्.""",
 vocab=[("गतः", "gone"), ("गत्वा", "having gone"), ("गन्तुम्", "to go"), ("पठितम्", "read (n.)"), ("खादितम्", "eaten (n.)"), ("उक्तम्", "said (n.)"), ("दृष्ट्वा", "having seen"), ("कर्तुम्", "to do")],
 examples=[("रामेण फलं खादितम्।", "The fruit was eaten by Rama."), ("रामः गतः।", "Rama has gone."), ("सः गृहं गत्वा पठति।", "Having gone home, he reads.")],
 questions=[
  ("'To go' =", "गन्तुम्", ["गत्वा", "गतः", "गच्छति"], "-तुम् is the infinitive."),
  ("'Having gone' =", "गत्वा", ["गन्तुम्", "गतम्", "गच्छेत्"], "-त्वा is the gerund."),
  ("'Rama has gone.'", "रामः गतः।", ["रामेण गतः।", "रामः गतम्।", "रामं गतः।"], "Intransitive: nominative subject agrees with the participle."),
  ("In **रामेण फलं खादितम्** who is the agent?", "रामेण", ["फलम्", "खादितम्", "none"], "The agent of a passive participle is instrumental."),
  ("Why is it खादितम् (neuter)?", "It agrees with फलम्", ["It agrees with रामेण", "It is a plural", "Participles are always neuter"], "The participle agrees with the nominative object फलम्."),
 ],
 drills=[("decl", {"classes": ["a", "A"], "cases": [1, 2]})],
),
Lesson(
 "3.5", 3, "Sandhi", "Vowel sandhi", "अच्सन्धिः", 20,
 "Join vowels at word boundaries: the rules that make Sanskrit sound smooth.",
 """**Sandhi** ("joining") changes sounds where words or parts meet. Start with the vowels.

| Rule | Pattern | Example |
|---|---|---|
| **Same vowel → long** (सवर्णदीर्घः) | अ/आ + अ/आ → आ | न + अस्ति = **नास्ति** · विद्या + आलयः = **विद्यालयः** |
| | इ/ई + इ/ई → ई | कवि + इन्द्रः = कवीन्द्रः |
| | उ/ऊ + उ/ऊ → ऊ | गुरु + उपदेशः = गुरूपदेशः |
| **Guṇa** (गुणः) | अ/आ + इ/ई → ए | तत्र + इति = **तत्रेति** |
| | अ/आ + उ/ऊ → ओ | सूर्य + उदयः = सूर्योदयः |
| | अ/आ + ऋ → अर् | महा + ऋषिः = **महर्षिः** |
| **Vṛddhi** (वृद्धिः) | अ/आ + ए/ऐ → ऐ | सदा + एव = **सदैव** |
| | अ/आ + ओ/औ → औ | महा + औषधम् = महौषधम् |
| **Yaṇ** (यण्) | इ/ई + other vowel → य् | इति + अपि = **इत्यपि** |
| | उ/ऊ + other vowel → व् | सु + आगतम् = **स्वागतम्** |
| | ऋ + other vowel → र् | पितृ + आज्ञा = पित्राज्ञा |
| **Ayādi** (अयादि) | ए → अय्, ओ → अव् | ने + अनम् = नयनम् · पो + अनः = पवनः |
| **Pūrvarūpa** | ए/ओ + अ → ए/ओ + ऽ | ते + अपि = **तेऽपि** · सः + अहम् = सोऽहम् |

Look at the **last sound of word 1** and the **first sound of word 2**. Practise with the Sandhi lab: type रामः and अस्ति.""",
 vocab=[("नास्ति", "is not"), ("विद्यालयः", "school"), ("महर्षिः", "great sage"), ("सदैव", "always"), ("इत्यपि", "thus also"), ("स्वागतम्", "welcome")],
 examples=[("तत्र इति → तत्रेति", "there + thus"), ("सदा एव → सदैव", "always indeed")],
 questions=[
  ("न + अस्ति =", "नास्ति", ["नअस्ति", "नस्ति", "नैस्ति"], "अ + अ → आ."),
  ("इति + अपि =", "इत्यपि", ["इतिअपि", "इतेपि", "इतीपि"], "इ before a different vowel becomes य्."),
  ("महा + ऋषिः =", "महर्षिः", ["महाऋषिः", "महारिषिः", "महार्षिः"], "आ + ऋ → अर् (guṇa)."),
  ("सदा + एव =", "सदैव", ["सदेव", "सदाएव", "सदोव"], "आ + ए → ऐ (vṛddhi)."),
  ("सु + आगतम् =", "स्वागतम्", ["सुआगतम्", "सोआगतम्", "सूआगतम्"], "उ before another vowel → व्."),
 ],
 drills=[("sandhi", {"kinds": ["vowel"]})],
),
Lesson(
 "3.6", 3, "Sandhi", "Visarga sandhi", "विसर्गसन्धिः", 18,
 "The visarga changes depending on the sound that follows.",
 """Many words end in **ः** (visarga): रामः, देवाः, हरिः. What it becomes depends on what comes next.

| Word 1 ends | Next sound | Result | Example |
|---|---|---|---|
| **-अः** | अ | ओऽ | रामः + अस्ति = **रामोऽस्ति** |
| | other vowel | अ (hiatus) | रामः + इति = राम इति |
| | voiced consonant | ओ | रामः + गच्छति = **रामो गच्छति** |
| **-आः** | vowel / voiced | आ | देवाः + गच्छन्ति = **देवा गच्छन्ति** |
| **-इः, -उः** | vowel / voiced | इर्, उर् | हरिः + अस्ति = **हरिरस्ति** |
| any | च / छ | श् | रामः + च = **रामश्च** |
| any | ट / ठ | ष् | रामः + टीका = रामष्टीका |
| any | त / थ | स् | रामः + तत्र = **रामस्तत्र** |
| any | क ख प फ | ः stays | रामः + पठति = रामः पठति |

**Special:** सः and एषः drop their visarga before any sound except short अ: सः + गच्छति = **स गच्छति**, सः + एव = **स एव**, but सः + अस्ति = **सोऽस्ति**.
Before **र**, इः/उः lengthen: हरिः + रमते = हरी रमते.

A quick rule of thumb: *voiced next → the visarga turns into a vowel or र्; voiceless next → it stays or turns into a sibilant.*""",
 vocab=[("रामोऽस्ति", "Rama is"), ("रामश्च", "and Rama"), ("हरिरस्ति", "Hari is"), ("स एव", "he indeed"), ("सोऽहम्", "I am that")],
 examples=[("रामः + गच्छति → रामो गच्छति", "Rama goes"), ("सः + एव → स एव", "he indeed")],
 questions=[
  ("रामः + अस्ति =", "रामोऽस्ति", ["रामः अस्ति", "रामअस्ति", "रामरस्ति"], "अः + अ → ओऽ."),
  ("रामः + गच्छति =", "रामो गच्छति", ["रामः गच्छति", "रामा गच्छति", "रामर् गच्छति"], "अः before a voiced consonant → ओ."),
  ("हरिः + अस्ति =", "हरिरस्ति", ["हरोऽस्ति", "हरिअस्ति", "हरीस्ति"], "इः before a vowel → इर्."),
  ("रामः + च =", "रामश्च", ["रामसच", "रामो च", "रामः च्"], "ः + च → श्च."),
  ("सः + गच्छति =", "स गच्छति", ["सो गच्छति", "सः गच्छति", "सर् गच्छति"], "सः drops its visarga before consonants."),
 ],
 drills=[("sandhi", {"kinds": ["visarga"]})],
),
Lesson(
 "3.7", 3, "Sandhi", "Consonant sandhi", "हल्सन्धिः", 18,
 "Final consonants assimilate to the sound that follows.",
 """Consonants at the end of a word adapt to the next sound.

| Rule | Example |
|---|---|
| **Voicing:** a final क् ट् त् प् becomes voiced (ग् ड् द् ब्) before a vowel or voiced sound | तत् + गच्छति = **तद् गच्छति** · जगत् + ईशः = **जगदीशः** · वाक् + ईशः = वागीशः |
| **त् before च/छ → च्** | तत् + च = **तच्च** · शरत् + चन्द्रः = शरच्चन्द्रः |
| **त् before श → च्छ** | तत् + श्रुत्वा = तच्छ्रुत्वा |
| **त् before ह → द्ध** | तत् + हि = **तद्धि** |
| **म् → अनुस्वारः** before a consonant | तम् + गच्छति = **तं गच्छति** · फलम् + खादति = फलं खादति |
| **म् + vowel** joins | फलम् + अस्ति = फलमस्ति |
| **Doubling:** short vowel + final ङ्/न् + vowel doubles the nasal | तस्मिन् + एव = **तस्मिन्नेव** · गच्छन् + अत्र = गच्छन्नत्र |
| **न् + च** → ंश्च | तान् + च = तांश्च |

**Aim:** the sounds at the junction move to the *same place or voicing* as their neighbour, which is easier to say.""",
 vocab=[("तद्धि", "for that"), ("तच्च", "and that"), ("जगदीशः", "lord of the world"), ("वागीशः", "lord of speech"), ("तस्मिन्नेव", "in that very"), ("तं गच्छति", "goes to him")],
 examples=[("तत् + च → तच्च", "and that"), ("तम् + गच्छति → तं गच्छति", "goes to him")],
 questions=[
  ("तत् + च =", "तच्च", ["तत्च", "तद्च", "तथ्च"], "त् + च → च्च."),
  ("जगत् + ईशः =", "जगदीशः", ["जगतीशः", "जगत्ईशः", "जगथीशः"], "त् before a vowel → द्."),
  ("तम् + गच्छति =", "तं गच्छति", ["तम् गच्छति", "तन् गच्छति", "तग् गच्छति"], "Final म् → ं before a consonant."),
  ("तत् + हि =", "तद्धि", ["तत्हि", "तथ्हि", "तह्हि"], "त् + ह → द्ध."),
  ("तस्मिन् + एव =", "तस्मिन्नेव", ["तस्मिनेव", "तस्मिन् एव", "तस्मिणेव"], "A short vowel + final न् before a vowel doubles the न्."),
 ],
 drills=[("sandhi", {"kinds": ["consonant"]})],
),
Lesson(
 "3.8", 3, "Sentence structure", "Kāraka: who does what to whom", "कारकम्", 20,
 "Map each noun to its semantic role and see how case marks it.",
 """Pāṇini describes a sentence as a verb with **kārakas**, the participants in the action:

| Kāraka | Role | Typical case |
|---|---|---|
| **कर्ता** (kartā) | the agent, the doer | nominative (active) / instrumental (passive) |
| **कर्म** (karman) | the thing acted on, goal | accusative |
| **करणम्** (karaṇa) | the instrument or means | instrumental |
| **सम्प्रदानम्** (sampradāna) | the recipient | dative |
| **अपादानम्** (apādāna) | the source, separation | ablative |
| **अधिकरणम्** (adhikaraṇa) | the place or time | locative |

The **genitive** (षष्ठी) is *not* a kāraka. It expresses a relationship between nouns (सम्बन्धः).

### Example
रामः वने मित्रेण सह फलं खादति।
- रामः — kartā (nom.) · फलम् — karman (acc.) · वने — adhikaraṇa (loc.) · मित्रेण सह — companion (instr.)

### Agreement checks
1. The verb agrees with the **kartā** in person and number.
2. Adjectives agree with their noun in gender, number and case.
3. In **passive-participle** sentences the agent becomes instrumental and the object nominative.

Use the **Grammar Lab** to see these roles computed for your own sentences.""",
 vocab=[("कर्ता", "agent"), ("कर्म", "object"), ("करणम्", "instrument"), ("सम्प्रदानम्", "recipient"), ("अपादानम्", "source"), ("अधिकरणम्", "locus")],
 examples=[("रामः गृहात् वनं गच्छति।", "Rama goes from the house to the forest."), ("बालकः पुस्तकं पठति।", "The boy reads a book.")],
 questions=[
  ("Which kāraka is expressed by the ablative?", "apādāna (source)", ["karaṇa (instrument)", "adhikaraṇa (locus)", "sampradāna (recipient)"], "Ablative = separation/source."),
  ("The kartā of an active sentence is in the…", "nominative", ["accusative", "genitive", "locative"], "The agent is nominative in active sentences."),
  ("In **वने फलं खादति**, वने is the…", "adhikaraṇa", ["karman", "kartā", "karaṇa"], "Locative = place: adhikaraṇa."),
  ("Is the genitive a kāraka?", "No, it expresses a relation (sambandha)", ["Yes, it is the kartā", "Yes, it is the karaṇa", "Only in the plural"], "षष्ठी shows relation, not a role in the action."),
  ("The agent of a passive participle is…", "instrumental", ["accusative", "nominative", "dative"], "रामेण फलं खादितम्: agent रामेण."),
 ],
 drills=[("identify", {"cases": [2, 3, 4, 5, 7]})],
),
]
