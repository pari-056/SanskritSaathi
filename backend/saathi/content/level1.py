from ..lessonbase import Lesson

LESSONS = [
Lesson(
 "1.1", 1, "Script & sound", "Vowels and vowel signs", "स्वराः", 12,
 "Read and write the Sanskrit vowels, their signs, and the two special marks.",
 """Sanskrit is written in **Devanagari**. Each symbol stands for one sound, so once you know the letters you can read any word.

### Vowels (स्वराः)
| Short | Long |
|---|---|
| अ *a* | आ *ā* |
| इ *i* | ई *ī* |
| उ *u* | ऊ *ū* |
| ऋ *ṛ* | ॠ *ṝ* |
| ऌ *ḷ* | |

**Diphthongs** (always long): ए *e*, ऐ *ai*, ओ *o*, औ *au*.

A long vowel lasts about twice as long as a short one. The difference changes meaning, so keep it clear.

### Vowel signs (मात्राः)
After a consonant a vowel is written as a sign: क + ा = **का**, क + ि = **कि**, क + ी = **की**, क + ु = **कु**, क + ू = **कू**, क + ृ = **कृ**, क + े = **के**, क + ै = **कै**, क + ो = **को**, क + ौ = **कौ**.
The vowel **अ** has no sign: every bare consonant already carries it (क = *ka*).

### Two special marks
- **अनुस्वारः** ं (*ṃ*): a nasal sound, as in संस्कृतम्.
- **विसर्गः** ः (*ḥ*): a light breathy echo of the vowel, as in रामः (*rāmaḥ*).""",
 vocab=[("कमलम्", "lotus"), ("जलम्", "water"), ("फलम्", "fruit"), ("गृहम्", "house"), ("नदी", "river"), ("पुस्तकम्", "book")],
 examples=[("रामः", "Rama"), ("नदी", "river")],
 questions=[
  ("Which letter is the **long** vowel ī?", "ई", ["इ", "ऊ", "ए"], "ई is long ī; इ is short i."),
  ("What is the IAST transliteration of ऐ?", "ai", ["a", "au", "e"], "ऐ = ai, a diphthong."),
  ("Which is a **short** vowel?", "उ", ["ऊ", "ए", "ऐ"], "उ is short u. ए, ऐ are always long and ऊ is long ū."),
  ("क + ू = ?", "कू", ["कि", "कु", "के"], "The sign ू makes the long ū: कू (kū)."),
  ("The mark ः is called…", "visarga", ["anusvāra", "virāma", "avagraha"], "ः is visarga (ḥ). The nasal dot ं is anusvāra."),
 ],
 drills=[("script_vowel", {}), ("script_matra", {})],
),
Lesson(
 "1.2", 1, "Script & sound", "Consonants and the varga chart", "व्यञ्जनानि", 15,
 "Learn the consonant chart: five classes by place of articulation, plus semivowels and sibilants.",
 """Consonants (**व्यञ्जनानि**) are arranged by where in the mouth they are made. The first 25 form five **vargas** (classes); each row runs unvoiced → aspirated → voiced → voiced aspirated → nasal.

| Class (वर्गः) | | | | | |
|---|---|---|---|---|---|
| Guttural (कण्ठ्य) | क *ka* | ख *kha* | ग *ga* | घ *gha* | ङ *ṅa* |
| Palatal (तालव्य) | च *ca* | छ *cha* | ज *ja* | झ *jha* | ञ *ña* |
| Retroflex (मूर्धन्य) | ट *ṭa* | ठ *ṭha* | ड *ḍa* | ढ *ḍha* | ण *ṇa* |
| Dental (दन्त्य) | त *ta* | थ *tha* | द *da* | ध *dha* | न *na* |
| Labial (ओष्ठ्य) | प *pa* | फ *pha* | ब *ba* | भ *bha* | म *ma* |

**Semivowels (अन्तःस्थाः):** य *ya*, र *ra*, ल *la*, व *va*
**Sibilants (ऊष्माणः):** श *śa*, ष *ṣa*, स *sa*; and **ह** *ha*

### Key ideas
- **Aspirated** means a puff of breath follows: ख *kha* is k + h said together (as in *bookhouse*), not like English *kh*.
- Every bare consonant carries an inherent **अ**. To remove it, add the **virāma** ्: क् = *k*.
- Retroflex (ट ठ ड ढ ण) are made with the tongue curled back; dental (त थ द ध न) with the tongue on the teeth.""",
 vocab=[("कथा", "story"), ("गजः", "elephant"), ("चन्द्रः", "moon"), ("दन्तः", "tooth"), ("पत्रम्", "leaf, letter"), ("मधु", "honey")],
 questions=[
  ("Which of these is a **dental** consonant?", "त", ["ट", "क", "प"], "त is dental ta. ट is retroflex."),
  ("Which letter is **aspirated**?", "ख", ["क", "ग", "ङ"], "ख = kha (क + breath). ग is voiced, ङ is nasal."),
  ("The mark ् (virāma) does what?", "Removes the inherent a", ["Adds a long ā", "Marks a nasal", "Marks a pause"], "क् = k, without the vowel."),
  ("What is the IAST of ष?", "ṣa", ["śa", "sa", "ha"], "ष = ṣa (retroflex sibilant); श = śa; स = sa."),
  ("Which row is the **labial** class?", "प फ ब भ म", ["क ख ग घ ङ", "त थ द ध न", "य र ल व"], "The labial class is प फ ब भ म."),
 ],
 drills=[("script_consonant", {}), ("script_matra", {})],
),
Lesson(
 "1.3", 1, "Script & sound", "Conjuncts, repha and reading words", "संयुक्ताक्षराणि", 15,
 "Read conjunct consonants and the special shapes of र, then read real words.",
 """When consonants meet with no vowel between them they are written as a **conjunct** (संयुक्ताक्षरम्). Usually the first letter loses its vertical bar and joins the second.

| Conjunct | Made of | Example |
|---|---|---|
| क्त | क् + त | उक्त *ukta* |
| त्य | त् + य | सत्य *satya* |
| स्त | स् + त | अस्ति *asti* |
| द्ध | द् + ध | बुद्धि *buddhi* |
| न्द | न् + द | सुन्दर *sundara* |

### Special conjuncts
- **क्ष** = क् + ष *kṣa* (क्षेत्रम् *kṣetram*)
- **ज्ञ** = ज् + ञ *jña* (ज्ञानम् *jñānam*)
- **त्र** = त् + र *tra* (मित्रम् *mitram*)
- **श्र** = श् + र *śra* (श्रीः *śrīḥ*)

### The letter र
- **Before** a consonant र is written as a hook **above**: र् + म = **र्म** (धर्मः *dharmaḥ*). This is the *repha*.
- **After** a consonant it is a small stroke **below**: क + र = **क्र**, प + र = **प्र** (प्रथमा *prathamā*).

### Reading practice
संस्कृतम् = *saṃskṛtam* · विद्या = *vidyā* · कृष्णः = *kṛṣṇaḥ* · अस्ति = *asti*.""",
 vocab=[("विद्या", "knowledge"), ("धर्मः", "duty, righteousness"), ("मित्रम्", "friend"), ("ज्ञानम्", "knowledge"), ("क्षेत्रम्", "field"), ("संस्कृतम्", "Sanskrit")],
 examples=[("अहं संस्कृतं पठामि।", "I study Sanskrit.")],
 questions=[
  ("क्ष is made of…", "क् + ष", ["क् + स", "ख् + ष", "क् + श"], "क्ष = k + ṣ."),
  ("Read: **संस्कृतम्**", "saṃskṛtam", ["sanskritam", "saṃskratam", "samskṛtām"], "सं-स्कृ-त-म्: saṃ-skṛ-ta-m."),
  ("How is **धर्म** (dharma) written, with repha?", "धर्म", ["धरम", "धम्र", "धर्मा"], "र् before म is written above: र्म."),
  ("Which conjunct is *jña*?", "ज्ञ", ["त्र", "श्र", "क्ष"], "ज्ञ = ज् + ञ."),
  ("Read: **बुद्धि**", "buddhi", ["budhi", "bhuddi", "buddī"], "द्ध = d + dh, so bud-dhi."),
 ],
 drills=[("script_conjunct", {})],
),
Lesson(
 "1.4", 1, "First sentences", "Greetings and introductions", "अभिवादनम्", 12,
 "Greet people, say your name, and ask theirs politely.",
 """### Everyday phrases
| Sanskrit | Meaning |
|---|---|
| नमस्ते | Greetings (to one person) |
| सुप्रभातम् | Good morning |
| स्वागतम् | Welcome |
| धन्यवादः | Thank you |
| कृपया | Please |
| पुनः मिलामः | See you again |

### Saying who you are
- **मम नाम ... अस्ति।** — My name is … (lit. "my name is …")
- **अहं ... अस्मि।** — I am …
- **भवतः नाम किम्?** — What is your name? (to a man)
- **भवत्याः नाम किम्?** — What is your name? (to a woman)
- **भवान् कथम् अस्ति?** / **भवती कथम् अस्ति?** — How are you? (to a man / woman)
- **अहं कुशलः / कुशला अस्मि।** — I am well (man / woman).

**भवान्** (m.) and **भवती** (f.) are the polite "you". They take a *third-person* verb: भवान् अस्ति.

Sanskrit often drops the verb "to be" in simple statements: **सः छात्रः।** = He is a student.""",
 vocab=[("नमस्ते", "greetings"), ("धन्यवादः", "thanks"), ("स्वागतम्", "welcome"), ("कृपया", "please"), ("नाम", "name"), ("भवान्", "you (polite, m.)"), ("भवती", "you (polite, f.)")],
 examples=[("मम नाम रामः अस्ति।", "My name is Rama."), ("अहं छात्रः अस्मि।", "I am a student.")],
 questions=[
  ("What does **धन्यवादः** mean?", "Thank you", ["Welcome", "Please", "Good morning"], "धन्यवादः = thanks."),
  ("Polite 'you' for a **woman**:", "भवती", ["भवान्", "त्वम्", "सः"], "भवती is feminine; भवान् is masculine."),
  ("A good reply to **भवतः नाम किम्?**", "मम नाम रामः अस्ति।", ["अहं गच्छति।", "सः पठति।", "धन्यवादः।"], "Answer a name question with मम नाम … अस्ति."),
  ("**सुप्रभातम्** means", "Good morning", ["Good night", "Goodbye", "Thank you"], "सु (good) + प्रभातम् (dawn)."),
  ("**अहं कुशला अस्मि** is said by", "a woman", ["a man", "a group", "a child only"], "कुशला is feminine."),
 ],
),
Lesson(
 "1.5", 1, "First sentences", "Pronouns and the verb 'to be'", "सर्वनामानि", 15,
 "Learn the personal pronouns and the present tense of √अस् (to be).",
 """### Pronouns (nominative)
| | Singular | Dual (two) | Plural |
|---|---|---|---|
| **I / we** (1st) | अहम् | आवाम् | वयम् |
| **you** (2nd) | त्वम् | युवाम् | यूयम् |
| **he** (3rd m.) | सः | तौ | ते |
| **she** (3rd f.) | सा | ते | ताः |
| **it** (3rd n.) | तत् | ते | तानि |

Sanskrit has **three numbers**: singular (एकवचनम्), **dual** (द्विवचनम्) for exactly two, and plural (बहुवचनम्) for three or more.

### √अस् "to be", present tense
| Person | Sing. | Dual | Plural |
|---|---|---|---|
| 3rd | अस्ति | स्तः | सन्ति |
| 2nd | असि | स्थः | स्थ |
| 1st | अस्मि | स्वः | स्मः |

**Persons:** the tradition calls the 3rd person **प्रथम** ("first"), 2nd **मध्यम** ("middle"), 1st **उत्तम** ("last"). Do not let the names confuse you: प्रथम = he/she/it.

Examples: अहं छात्रः अस्मि। · त्वं बालकः असि। · सा बालिका अस्ति। · ते छात्राः सन्ति।""",
 vocab=[("अहम्", "I"), ("त्वम्", "you"), ("सः", "he"), ("सा", "she"), ("तत्", "it, that"), ("वयम्", "we"), ("ते", "they (m.)")],
 examples=[("अहं छात्रः अस्मि।", "I am a student."), ("सा बालिका अस्ति।", "She is a girl."), ("ते छात्राः सन्ति।", "They are students.")],
 questions=[
  ("'I am' =", "अस्मि", ["असि", "अस्ति", "स्मः"], "अस्मि is 1st person singular."),
  ("'You (sg.) are' =", "असि", ["अस्मि", "अस्ति", "सन्ति"], "असि is 2nd person singular."),
  ("'They are' =", "सन्ति", ["अस्ति", "स्मः", "स्तः"], "सन्ति is 3rd person plural."),
  ("Which pronoun means 'she'?", "सा", ["सः", "तत्", "अहम्"], "सा is feminine."),
  ("**आवाम्** means", "we two", ["we (many)", "you two", "they"], "आवाम् is the 1st-person dual."),
 ],
 drills=[("conj", {"roots": ["as"], "tenses": ["lat"]})],
),
Lesson(
 "1.6", 1, "First sentences", "Present tense of regular verbs", "लट्लकारः", 18,
 "Conjugate regular first-class verbs in the present tense (लट्).",
 """Most everyday verbs use one pattern. Take the **present stem** and add endings. For **√पठ्** (to read), stem **पठ-**:

| Person | Singular | Dual | Plural |
|---|---|---|---|
| 3rd | पठति | पठतः | पठन्ति |
| 2nd | पठसि | पठथः | पठथ |
| 1st | पठामि | पठावः | पठामः |

In the 1st person the stem vowel lengthens: पठ → पठा-मि.

### Common verbs
| Root | Meaning | 3rd sg. |
|---|---|---|
| √पठ् | read | पठति |
| √गम् | go | **गच्छति** (stem गच्छ-) |
| √लिख् | write | लिखति |
| √खाद् | eat | खादति |
| √वद् | speak | वदति |
| √भू | be, become | **भवति** |
| √पा | drink | **पिबति** |
| √दृश् | see | **पश्यति** |
| √स्था | stand | **तिष्ठति** |

Some roots change their stem (गम् → गच्छ-) but the endings are the same.

The verb agrees with its subject in **person and number**: बालकः पठति, बालकौ पठतः, बालकाः पठन्ति.""",
 vocab=[("पठति", "reads"), ("गच्छति", "goes"), ("लिखति", "writes"), ("खादति", "eats"), ("वदति", "speaks"), ("भवति", "is, becomes"), ("पिबति", "drinks"), ("पश्यति", "sees")],
 examples=[("अहं पठामि।", "I read."), ("सः गच्छति।", "He goes."), ("ते खादन्ति।", "They eat.")],
 questions=[
  ("'I read' =", "पठामि", ["पठति", "पठसि", "पठन्ति"], "1st person singular: पठामि."),
  ("'They go' =", "गच्छन्ति", ["गच्छति", "गच्छतः", "गच्छसि"], "3rd person plural -न्ति."),
  ("'You (sg.) write' =", "लिखसि", ["लिखति", "लिखामि", "लिखथः"], "2nd person singular -सि."),
  ("'We two eat' =", "खादावः", ["खादामः", "खादतः", "खादथः"], "1st person dual -आवः."),
  ("The 3rd sg. present of √पा (drink) is", "पिबति", ["पाति", "पाबति", "पीति"], "√पा uses the stem पिब-."),
 ],
 drills=[("conj", {"tenses": ["lat"]})],
),
Lesson(
 "1.7", 1, "First sentences", "Nouns: subject and object", "प्रथमा-द्वितीया", 15,
 "Use the nominative for the subject and the accusative for the object, in simple sentences.",
 """Sanskrit nouns change their **endings** to show their job in the sentence, so word order is flexible. The verb usually comes last.

### Two cases
- **प्रथमा** (nominative): the subject → बालकः, फलम्
- **द्वितीया** (accusative): the object, or the goal of movement → बालकम्, फलम्

### Masculine and neuter nouns in -अ
| | Masculine (राम) | Neuter (फल) |
|---|---|---|
| Nominative sg. | रामः | फलम् |
| Accusative sg. | रामम् | फलम् |

Neuter nominative and accusative look the same. Context decides.

### Examples
- **रामः फलं खादति।** Rama eats a fruit.
- **बालकः पुस्तकं पठति।** The boy reads a book.
- **सः विद्यालयं गच्छति।** He goes to school. (the goal takes the accusative)

The final **म्** is often written as the dot **ं** before a consonant: फलं खादति.

The same meaning can be written फलं रामः खादति, but the *endings* still show who does what.""",
 vocab=[("बालकः", "boy"), ("पुस्तकम्", "book"), ("फलम्", "fruit"), ("विद्यालयः", "school"), ("गृहम्", "house"), ("वृक्षः", "tree"), ("छात्रः", "student")],
 examples=[("रामः फलं खादति।", "Rama eats a fruit."), ("बालकः पुस्तकं पठति।", "The boy reads a book."), ("सः विद्यालयं गच्छति।", "He goes to school.")],
 questions=[
  ("In **बालकः पुस्तकं पठति**, who is the subject?", "बालकः", ["पुस्तकम्", "पठति", "none"], "बालकः is nominative: the one who reads."),
  ("Fill in: रामः ___ खादति। (fruit, as object)", "फलम्", ["फलः", "फलाय", "फलेन"], "The object takes the accusative: फलम्."),
  ("'The boy goes to school.'", "बालकः विद्यालयं गच्छति।", ["बालकं विद्यालयः गच्छति।", "बालकः विद्यालयः गच्छति।", "विद्यालयं बालकं गच्छति।"], "Subject nominative, goal accusative, verb last."),
  ("The accusative singular of **राम** is", "रामम्", ["रामः", "रामेण", "रामाय"], "-म् marks the accusative singular."),
  ("Which two cases look identical for neuter nouns?", "nominative and accusative", ["dative and genitive", "instrumental and locative", "none"], "Neuter nom. = acc."),
 ],
 drills=[("decl", {"cases": [1, 2]}), ("identify", {"cases": [1, 2]})],
),
Lesson(
 "1.8", 1, "First sentences", "Asking questions and counting to ten", "प्रश्नाः सङ्ख्याश्च", 12,
 "Ask who, what, where, when, how; count from one to ten.",
 """### Question words
| Sanskrit | Meaning |
|---|---|
| कः / का / किम् | who (m.) / who (f.) / what |
| कुत्र | where? |
| कुतः | from where? |
| कदा | when? |
| कथम् | how? |
| किमर्थम् | why? |

Examples: **सः कः अस्ति?** Who is he? · **भवान् कुत्र गच्छति?** Where are you going? · **फलं कुत्र अस्ति?** Where is the fruit?

Add **किम्** at the start to turn a statement into a yes/no question: **किं भवान् पठति?**

### Numbers 1–10
| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| एक | द्वि | त्रि | चतुर् | पञ्च |
| 6 | 7 | 8 | 9 | 10 |
| षट् | सप्त | अष्ट | नव | दश |""",
 vocab=[("कुत्र", "where"), ("कदा", "when"), ("कथम्", "how"), ("किम्", "what"), ("कः", "who"), ("पञ्च", "five"), ("दश", "ten")],
 examples=[("भवान् कुत्र गच्छति?", "Where are you going?"), ("सः कः अस्ति?", "Who is he?")],
 questions=[
  ("**कुत्र** means", "where", ["when", "how", "who"], "कुत्र = where; कदा = when."),
  ("**पञ्च** is", "five", ["four", "six", "ten"], "पञ्च = 5."),
  ("**सप्त** is", "seven", ["six", "eight", "nine"], "सप्त = 7."),
  ("How do you ask 'What is your name?'", "भवतः नाम किम्?", ["भवतः नाम कुत्र?", "भवतः नाम कदा?", "भवान् कथम्?"], "किम् = what."),
  ("**नव** is", "nine", ["five", "ten", "two"], "नव = 9."),
 ],
),
]
