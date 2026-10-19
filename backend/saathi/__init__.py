"""Sanskrit Saathi: a rule-based Sanskrit engine plus a Gemini-powered tutor.

The deterministic modules (translit, sandhi, morph, syntax) give *verifiable*
results for the forms they cover. The LLM layer (llm.py) handles open-ended
tutoring and is cross-checked against these modules.
"""
