# Sanskrit Saathi evaluation report

Engine lexicon: **3,813** indexed forms · **169** stems/roots

## sa_ufal-ud-test.conllu
230 sentences · 1434 evaluated tokens (skipped: {'skipped_compound_member': 214, 'skipped_punct': 195}) · sha256[:16] `8e956d19e67e96d8`

### Morphological analysis

* Coverage (token has ≥1 analysis): **38.9%**
* Lemma recall: **33.7%** · full recall (lemma + features): **33.1%**
* Correct reading present among the analyses of covered tokens: **85.0%**
* Mean analyses per covered token (ambiguity): 1.42

| Type | Tokens | Coverage | Lemma recall | Full recall |
|---|---|---|---|---|
| adjective | 159 | 31.4% | 30.2% | 30.2% |
| gerund | 35 | 17.1% | 17.1% | 17.1% |
| indeclinable | 278 | 71.6% | 68.3% | 68.3% |
| infinitive | 5 | 40.0% | 40.0% | 40.0% |
| noun | 509 | 15.7% | 14.0% | 13.0% |
| participle | 101 | 17.8% | 7.9% | 7.9% |
| pronoun | 170 | 85.3% | 61.2% | 58.8% |
| verb-finite | 177 | 32.8% | 30.5% | 30.5% |

Most frequent uncovered lemmas (best candidates to add next):

ब्रू (verb-finite, 14), नामन् (noun, 12), राजन् (noun, 12), यथा (indeclinable, 11), वच् (verb-finite, 11), अह् (verb-finite, 11), इदम् (adjective, 9), वरम् (indeclinable, 8), श्रु (verb-finite, 7), भवत् (pronoun, 7), इदम् (pronoun, 7), तथा (indeclinable, 7), ब्राह्मण (noun, 6), चिद् (indeclinable, 6), उपाय (noun, 5), गम् (verb-finite, 5), दमनक (noun, 5), भद्र (noun, 5), कृ (verb-finite, 4), भू (verb-finite, 4), महत् (adjective, 4), युज् (participle, 4), ज्ञा (verb-finite, 4), चिद् (adjective, 4), मध्य (noun, 4)

### Sandhi / segmentation

* Multiword tokens: 259
* **Sandhi rule recall** (rules rebuild the gold surface from gold parts): **91.9%**
* Splitter coverage: 7.0% · exact match: **5.0%**

Junctions where the rules disagree with the corpus: अ|म् ×2, त्|ज् ×1, आ|ए ×1, ं|ष् ×1, अ|ज् ×1, इ|अ ×1, म्|आ ×1, अ|प् ×1, र्|ए ×1, म्|भ् ×1, ह्|अ ×1, ः|उ ×1
