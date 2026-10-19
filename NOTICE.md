# Third-party material

* **vidyut / vidyut-prakriya** (MIT licence, https://github.com/ambuda-org/vidyut). A Pāṇinian derivation engine. It is used
  (1) offline by `backend/tools/build_verb_lexicon.py` to produce `backend/saathi/data/verbs.json` (principal parts and
  listed paradigms for 2,200+ Dhātupāṭha roots), and (2) as an independent oracle in the evaluation harness and tests.
  It is **not** a runtime dependency. `verbs.json` contains output derived from vidyut.
* **Dhātupāṭha data** distributed with vidyut (from ashtadhyayi.com), downloaded by the build tool; not bundled.
* **Universal Dependencies Sanskrit treebanks** (UD_Sanskrit-UFAL, UD_Sanskrit-Vedic; CC BY-SA 4.0). Downloaded on demand by
  `python -m saathi.evaluation fetch`; not bundled. If you redistribute the corpora or derivatives, keep the licence and attribution.
