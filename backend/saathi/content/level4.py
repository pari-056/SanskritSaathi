from ..lessonbase import Lesson

LESSONS = [
Lesson(
 "4.1", 4, "Advanced grammar", "Compounds (समासः)", "समासः", 25,
 "Recognise and analyse the six main kinds of Sanskrit compound.",
 """A **samāsa** fuses two or more words into one, dropping the case endings of all but the last. Long compounds are normal in classical prose and poetry, so analysing them is a core skill.

| Type | Idea | Example | Resolution |
|---|---|---|---|
| **तत्पुरुषः** (determinative) | first member relates to the second by a case; *second member is the head* | राजपुरुषः | राज्ञः पुरुषः (the king's man) |
| **कर्मधारयः** (descriptive) | adjective/noun + noun in apposition | नीलोत्पलम् | नीलम् उत्पलम् (a blue lotus) |
| **द्विगुः** (numeral) | numeral first, a collective sense | त्रिलोकी | त्रयाणां लोकानां समाहारः (the three worlds) |
| **द्वन्द्वः** (copulative) | "A and B", all members equal | रामलक्ष्मणौ | रामः च लक्ष्मणः च |
| **बहुव्रीहिः** (possessive) | the compound describes something *outside* it | पीताम्बरः | पीतम् अम्बरं यस्य सः (he whose garment is yellow, i.e. Vishnu) |
| **अव्ययीभावः** (adverbial) | first member indeclinable; whole is an adverb | प्रतिदिनम् | दिनं दिनं प्रति (every day) |

### How to analyse a compound
1. Split it into members (sandhi may hide the boundary).
2. Ask whether it is a **list** (द्वन्द्व), starts with an **indeclinable** (अव्ययीभाव), or starts with a **number** (द्विगु).
3. Otherwise ask: does the whole **describe someone/something else** ("he who has …")? → बहुव्रीहि.
4. If not, choose कर्मधारय (the members are the same thing) or तत्पुरुष (a case relation).

Gender and number come from the *last* member (except in द्वन्द्व and बहुव्रीहि, which follow what they describe).""",
 vocab=[("राजपुरुषः", "king's man"), ("नीलोत्पलम्", "blue lotus"), ("रामलक्ष्मणौ", "Rama and Lakshmana"), ("पीताम्बरः", "one in yellow garments"), ("प्रतिदिनम्", "every day"), ("त्रिलोकी", "the three worlds")],
 examples=[("राजपुरुषः गृहं गच्छति।", "The king's man goes home.")],
 questions=[
  ("रामलक्ष्मणौ is a…", "द्वन्द्व (copulative)", ["तत्पुरुष", "बहुव्रीहि", "अव्ययीभाव"], "It means 'Rama and Lakshmana'; the dual shows two equal members."),
  ("पीताम्बरः (one whose garment is yellow) is a…", "बहुव्रीहि", ["कर्मधारय", "द्विगु", "द्वन्द्व"], "It describes a person outside the compound."),
  ("राजपुरुषः = राज्ञः पुरुषः is a…", "तत्पुरुष (genitive)", ["द्वन्द्व", "बहुव्रीहि", "अव्ययीभाव"], "First member is in a case relation (genitive) to the second."),
  ("प्रतिदिनम् ('every day') is an…", "अव्ययीभाव", ["तत्पुरुष", "द्विगु", "बहुव्रीहि"], "It begins with an indeclinable and the whole is an adverb."),
  ("नीलोत्पलम् = नीलम् उत्पलम् is a…", "कर्मधारय", ["द्वन्द्व", "अव्ययीभाव", "बहुव्रीहि"], "Adjective + noun referring to the same thing."),
  ("A compound starting with a number, meaning a group, is…", "द्विगु", ["द्वन्द्व", "कर्मधारय", "तत्पुरुष"], "द्विगु = numeral compound."),
 ],
),
Lesson(
 "4.2", 4, "Advanced grammar", "Middle voice and the passive", "आत्मनेपदं कर्मणि प्रयोगश्च", 22,
 "Recognise ātmanepada verbs and form the passive.",
 """### Parasmaipada vs ātmanepada
Verbs have two sets of endings. **Parasmaipada** ("word for another") is what you know. **Ātmanepada** ("word for oneself") often marks that the action returns to the agent, though many roots simply take it.

Present of √लभ् (to obtain):
| | Sg. | Du. | Pl. |
|---|---|---|---|
| 3rd | लभते | लभेते | लभन्ते |
| 2nd | लभसे | लभेथे | लभध्वे |
| 1st | लभे | लभावहे | लभामहे |

Common ātmanepada roots: √लभ् (get), √सेव् (serve), √वृत् (be, exist: वर्तते), √मुद् (rejoice: मोदते).

### Passive (कर्मणि प्रयोगः)
Form: **root + -य- + ātmanepada endings**.
| Active | Passive |
|---|---|
| पठति (reads) | पठ्यते (is read) |
| खादति (eats) | खाद्यते (is eaten) |
| गच्छति (goes) | गम्यते (is gone, one goes) |
| पश्यति (sees) | दृश्यते (is seen) |
| करोति (does) | क्रियते (is done) |
| नयति (leads) | नीयते (is led) |

In a passive sentence:
- the **agent** is *instrumental*, the **object** is *nominative*, and the **verb agrees with the object**.
- रामः फलं खादति → **रामेण फलं खाद्यते।** (The fruit is eaten by Rama.)
- रामेण फलानि खाद्यन्ते। (plural object → plural verb)

Intransitive roots form an **impersonal passive** (भावे): रामेण गम्यते। "It is gone by Rama", i.e. Rama goes.""",
 vocab=[("लभते", "obtains"), ("वर्तते", "exists, is"), ("पठ्यते", "is read"), ("खाद्यते", "is eaten"), ("दृश्यते", "is seen"), ("क्रियते", "is done")],
 examples=[("रामेण फलं खाद्यते।", "The fruit is eaten by Rama."), ("बालकेन पुस्तकं पठ्यते।", "The book is read by the boy.")],
 questions=[
  ("'He obtains' (ātmanepada) =", "लभते", ["लभति", "लभ्यते", "अलभत्"], "लभ्-ते is the ātmanepada 3rd sg."),
  ("'It is read' =", "पठ्यते", ["पठति", "पठेत्", "पठितम्"], "root + य + ते."),
  ("In **रामेण फलं खाद्यते**, फलम् is the…", "nominative object", ["agent", "instrument", "genitive"], "In the passive the object becomes nominative."),
  ("The passive of करोति is", "क्रियते", ["कृयते", "करते", "कुरुते"], "√कृ → क्रियते."),
  ("'The fruits are eaten by Rama.'", "रामेण फलानि खाद्यन्ते।", ["रामेण फलानि खाद्यते।", "रामः फलानि खाद्यन्ते।", "रामेण फलं खाद्यन्ते।"], "The verb agrees with the plural object."),
 ],
),
Lesson(
 "4.3", 4, "Advanced grammar", "Word formation: kṛt and taddhita", "कृत्तद्धिताः", 20,
 "See how suffixes build new words from roots (kṛt) and from nouns (taddhita).",
 """Sanskrit builds vocabulary systematically. Knowing the suffixes lets you read unfamiliar words.

### Kṛt suffixes (added to *roots*)
| Suffix | Meaning | Examples |
|---|---|---|
| -तृ | agent, doer | कर्तृ → **कर्ता** (doer), दातृ → दाता (giver) |
| -अक | agent | पाठकः (reader), गायकः (singer), नायकः (leader) |
| -अन | action / instrument | पठनम् (reading), गमनम् (going), भोजनम् (eating, meal) |
| -ति | action, result | मतिः (thought), गतिः (movement), स्थितिः (state) |
| -त / -वत् | past participles | गतः, गतवान् |

### Taddhita suffixes (added to *nouns*)
| Suffix | Meaning | Examples |
|---|---|---|
| -त्व / -ता | abstract quality | गुरुत्वम् (heaviness), सुन्दरता (beauty) |
| -ईय | belonging to | भारतीय (Indian) |
| -इक | relating to | धार्मिक (relating to dharma) |
| -वत् / -मत् | possessing | बलवान् (strong), धनवान् (rich), श्रीमान् (prosperous) |
| -तर / -तम | more / most | सुन्दरतर (more beautiful), सुन्दरतम (most beautiful) |
| (vṛddhi) | descendant | राघवः (descendant of Raghu), पाण्डवः (son of Pāṇḍu) |

**Vṛddhi** (strengthening the first vowel: अ → आ, उ → औ, इ → ऐ) is the typical marker of many taddhitas: रघु → राघव, धर्म → धार्मिक.""",
 vocab=[("पाठकः", "reader"), ("गमनम्", "going"), ("गतिः", "movement"), ("बलवान्", "strong"), ("राघवः", "descendant of Raghu"), ("धार्मिक", "relating to dharma")],
 examples=[("पाठकः पुस्तकं पठति।", "The reader reads a book.")],
 questions=[
  ("**पाठकः** means", "reader", ["reading", "readable", "was read"], "-अक makes an agent noun: one who reads."),
  ("**पठनम्** is an…", "action noun (reading)", ["agent noun", "past participle", "gerund"], "-अन builds action nouns."),
  ("The suffix -ता / -त्व forms…", "abstract nouns", ["agents", "past participles", "adverbs"], "सुन्दर + ता = beauty."),
  ("**बलवान्** means", "having strength", ["strengthening", "weak", "the strong ones"], "-वत् means 'possessing'."),
  ("**राघवः** is…", "a descendant of Raghu", ["Raghu himself", "a place", "a verb form"], "Vṛddhi + -अ marks a patronymic."),
 ],
),
Lesson(
 "4.4", 4, "Pāṇini", "Pāṇini, the Māheśvara sūtras and pratyāhāras", "पाणिनीयव्याकरणम्", 25,
 "Meet the grammar that describes Sanskrit: the Aṣṭādhyāyī and its compression tricks.",
 """**Pāṇini** (around the 4th–5th century BCE) wrote the **अष्टाध्यायी** ("eight chapters"): about 4,000 terse rules (sūtras) that generate Sanskrit words and sentences. It is among the earliest formal grammars, and its rule-based, **generative** design is why it is studied in computational linguistics today.

### The sound inventory: 14 Māheśvara sūtras
अइउण् । ऋऌक् । एओङ् । ऐऔच् । हयवरट् । लण् । ञमङणनम् । झभञ् । घढधष् । जबगडदश् । खफछठथचटतव् । कपय् । शषसर् । हल् ।

The last letter of each (ण्, क्, ङ्, च् …) is a **marker** (इत्) and is not a sound.

### Pratyāhāras (abbreviations)
A pratyāhāra = a letter + a later marker: it stands for everything in between.
| Pratyāhāra | Covers |
|---|---|
| **अच्** | all vowels |
| **हल्** | all consonants |
| **इक्** | इ उ ऋ ऌ |
| **यण्** | य व र ल |
| **अक्** | अ इ उ ऋ ऌ |
| **जश्** | ज ब ग ड द (voiced unaspirated stops) |

### Sample sūtras
| Sūtra | Reading | Effect |
|---|---|---|
| अकः सवर्णे दीर्घः (6.1.101) | an अक् vowel + a similar vowel → long | न + अस्ति = नास्ति |
| आद्गुणः (6.1.87) | अ/आ + इक् vowel → guṇa | महा + ऋषिः = महर्षिः |
| वृद्धिरेचि (6.1.88) | अ/आ + एच् → vṛddhi | सदा + एव = सदैव |
| **इको यणचि** (6.1.77) | इक् → यण् before a vowel | इति + अपि = इत्यपि |
| एचोऽयवायावः (6.1.78) | ए ओ ऐ औ → अय् अव् आय् आव् before a vowel | ने + अनम् = नयनम् |

So **sandhi is rule application**: each junction is decided by the first rule that matches.""",
 vocab=[("सूत्रम्", "aphorism, rule"), ("अष्टाध्यायी", "Pāṇini's grammar"), ("प्रत्याहारः", "abbreviation"), ("इत्", "marker letter"), ("अच्", "vowels"), ("हल्", "consonants")],
 questions=[
  ("The pratyāhāra **अच्** stands for…", "all vowels", ["all consonants", "semivowels", "nasals"], "अच् runs from अ to the marker च् in ऐऔच्."),
  ("**यण्** =", "य व र ल", ["अ इ उ ऋ", "क ख ग घ", "श ष स ह"], "यण् covers the semivowels."),
  ("**इको यणचि** explains…", "इति + अपि = इत्यपि", ["न + अस्ति = नास्ति", "महा + ऋषिः = महर्षिः", "सदा + एव = सदैव"], "इक् vowels become यण् before a vowel."),
  ("**अकः सवर्णे दीर्घः** explains…", "न + अस्ति = नास्ति", ["इति + अपि = इत्यपि", "ने + अनम् = नयनम्", "तत् + च = तच्च"], "Similar vowels merge into a long vowel."),
  ("How many Māheśvara sūtras are there?", "14", ["8", "24", "108"], "There are fourteen."),
  ("**अष्टाध्यायी** means…", "eight chapters", ["eight cases", "eight roots", "eight sounds"], "अष्ट = eight; अध्याय = chapter."),
 ],
),
Lesson(
 "4.5", 4, "Reading", "Meter and reading a subhāṣita", "छन्दः सुभाषितं च", 25,
 "Count syllables, recognise the anuṣṭubh meter and read a classic verse.",
 """### Syllable weight
- **लघु** (laghu, light): a *short* vowel not followed by a conjunct.
- **गुरु** (guru, heavy): a *long* vowel, or a short vowel followed by a **conjunct, anusvāra or visarga**.

Example: धर्म is *dhar-ma*, two syllables. The first (**ध**) is **guru** because the conjunct र्म follows; the second (**म**) is laghu.

### Anuṣṭubh (श्लोकः)
The most common epic and classical meter: **4 pādas × 8 syllables = 32**. Each half-verse has 16 syllables.

> धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
> *dharma-kṣe-tre ku-ru-kṣe-tre / sa-ma-ve-tā yu-yu-tsa-vaḥ*, 8 + 8 syllables.
(Bhagavad Gītā 1.1, first half.)

### A subhāṣita ("well-said")
> विद्या ददाति विनयं विनयाद् याति पात्रताम्।
> पात्रत्वात् धनमाप्नोति धनात् धर्मं ततः सुखम्॥

*vidyā dadāti vinayaṃ vinayād yāti pātratām / pātratvāt dhanam āpnoti dhanād dharmaṃ tataḥ sukham*

**Meaning:** Knowledge gives humility; from humility comes worthiness; from worthiness one gains wealth; from wealth, dharma; and from that, happiness.

| Word | Meaning |
|---|---|
| विद्या | knowledge |
| ददाति | gives |
| विनयम् | humility, discipline |
| विनयात् | from humility |
| याति | reaches (√या) |
| पात्रताम् | worthiness |
| आप्नोति | obtains |
| धनात् | from wealth |
| ततः | from that |
| सुखम् | happiness |

Notice the **ablative chain**: विनयात् → पात्रत्वात् → धनात्, each step "from" the previous. Use the Grammar Lab to analyse the words the app knows.

### Another short maxim
**सत्यं वद। धर्मं चर।** *Speak the truth. Follow dharma.* (Taittirīya Upaniṣad)""",
 vocab=[("छन्दः", "meter"), ("श्लोकः", "verse"), ("सुभाषितम्", "well-said maxim"), ("विनयः", "humility"), ("पात्रता", "worthiness"), ("सुखम्", "happiness")],
 examples=[("विद्या ददाति विनयं विनयाद् याति पात्रताम्।", "Knowledge gives humility; from humility comes worthiness."), ("सत्यं वद।", "Speak the truth.")],
 questions=[
  ("An anuṣṭubh pāda has how many syllables?", "8", ["6", "11", "12"], "4 pādas × 8 = 32 syllables per verse."),
  ("A syllable with a short vowel followed by a conjunct is…", "guru (heavy)", ["laghu (light)", "silent", "neither"], "Position makes it heavy."),
  ("In **धर्म**, the first syllable ध is…", "guru, because र्म follows", ["laghu", "long by nature", "silent"], "Short vowel before a conjunct → guru."),
  ("**विनयात्** is in which case?", "ablative", ["genitive", "locative", "dative"], "-आत् is ablative: 'from humility'."),
  ("The verse 'विद्या ददाति …' teaches that…", "knowledge leads, step by step, to happiness", ["wealth is useless", "humility is weakness", "dharma comes first"], "The chain runs: knowledge → humility → worthiness → wealth → dharma → happiness."),
 ],
),
Lesson(
 "4.6", 4, "Computational Sanskrit", "Sanskrit and computational linguistics", "संगणकीयसंस्कृतम्", 25,
 "How machines analyse Sanskrit: tokenisation, sandhi splitting, morphology and parsing.",
 """Sanskrit is a rich testing ground for NLP because of **sandhi**, free word order, heavy inflection and long compounds.

### A typical pipeline
1. **Transliteration & encoding:** normalise Devanagari / IAST / HK into one scheme such as **SLP1** (one ASCII letter per sound; this app uses it internally).
2. **Segmentation (sandhi splitting):** find word boundaries. Hard because sandhi is *many-to-one*: different underlying pairs can produce the same surface string.
3. **Morphological analysis:** lemma + case/number/gender or tense/person/number for each word. Most forms are **ambiguous** (राम**म्** is accusative; फलम् is nominative *or* accusative).
4. **Compound analysis:** split and classify samāsa.
5. **Dependency parsing / kāraka labelling:** assign each word its role to the verb.
6. **Downstream tasks:** translation, search, tutoring.

### Rule-based vs neural
- **Rule-based** (paradigms, sandhi rules): precise and explainable, but limited by lexicon coverage.
- **Neural / LLM:** broad coverage and fluent, but can *hallucinate* forms and parses.
- **Hybrid** (this app): the LLM proposes, the rule engine verifies. Disagreements are flagged for the learner.

### Evaluation
Segmentation exact-match and F1, lemma accuracy, morphological feature F1, dependency UAS/LAS. Public resources include the **Sanskrit Heritage Platform** (Gérard Huet), the **Digital Corpus of Sanskrit** (Oliver Hellwig) and Universal Dependencies treebanks.

### Try it
In the **Lab**, join and split sandhi, inspect paradigms and run the self-check to see how a rule engine is evaluated against gold examples.""",
 vocab=[("संगणकः", "computer"), ("पदच्छेदः", "word division"), ("सन्धिविच्छेदः", "sandhi splitting"), ("शब्दरूपम्", "inflected form"), ("धातुः", "verbal root")],
 questions=[
  ("Why is sandhi splitting ambiguous?", "Different underlying pairs can give the same surface string", ["Sanskrit has no spaces in writing", "Sandhi is optional", "There are too few words"], "Sandhi is many-to-one, so splitting is one-to-many."),
  ("SLP1 is…", "an ASCII encoding with one letter per sound", ["a parsing algorithm", "a neural model", "a corpus"], "It makes rule-writing easy."),
  ("Which task assigns lemma + case + number to a word?", "morphological analysis", ["segmentation", "translation", "scansion"], "That is morphological analysis."),
  ("Why verify an LLM's grammar with a rule engine?", "LLMs can hallucinate plausible but wrong forms", ["LLMs cannot read Devanagari", "Rule engines are always complete", "It makes the app slower"], "Hybrid systems combine coverage and reliability."),
  ("Which metric measures dependency parsing?", "UAS / LAS", ["BLEU only", "Word error rate", "Perplexity"], "Unlabelled / labelled attachment score."),
 ],
),
]
