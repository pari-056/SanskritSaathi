import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import QuizRunner from "../components/QuizRunner";
import { ErrorBox, Spinner, Tabs } from "../components/ui";

interface Letter { sanskrit: string; iast: string }
interface Chart {
  vowels: Letter[]; vargas: { name: string; letters: Letter[] }[]; marks: Letter[]; matras: Letter[]; words: Letter[];
}

function Grid({ items }: { items: Letter[] }) {
  return (
    <div className="glyph-grid">
      {items.map((x) => (
        <div key={x.sanskrit} className="glyph"><div className="glyph-dev dev" lang="sa">{x.sanskrit}</div><div className="muted small">{x.iast}</div></div>
      ))}
    </div>
  );
}

const KINDS = [["vowel", "Vowels"], ["consonant", "Consonants"], ["matra", "Vowel signs"], ["conjunct", "Conjuncts & words"]] as const;

export default function Script() {
  const q = useQuery({ queryKey: ["chart"], queryFn: () => api.get<Chart>("/api/script/chart") });
  const [kinds, setKinds] = useState<string[]>(KINDS.map(([k]) => k));
  const [i, setI] = useState(0);
  const [show, setShow] = useState(false);
  if (q.isLoading) return <Spinner />;
  if (q.error) return <ErrorBox error={q.error} />;
  const c = q.data!;
  const w = c.words[((i % c.words.length) + c.words.length) % c.words.length];

  return (
    <div>
      <h2>देवनागरी · Script trainer</h2>
      <Tabs tabs={[
        { label: "🔠 Letter chart", content: (
          <div className="stack">
            <h3>Vowels (स्वराः)</h3><Grid items={c.vowels} />
            {c.vargas.map((v) => <div key={v.name}><h3>{v.name}</h3><Grid items={v.letters} /></div>)}
            <h3>Marks</h3><Grid items={c.marks} />
            <h3>Vowel signs on क</h3><Grid items={c.matras} />
            <p className="muted small">Lessons 1.1–1.3 explain these in detail.</p>
          </div>) },
        { label: "🎯 Drills", content: (
          <div className="stack">
            <fieldset className="checks"><legend>Drill types</legend>
              {KINDS.map(([k, label]) => (
                <label key={k}><input type="checkbox" checked={kinds.includes(k)}
                  onChange={(e) => setKinds(e.target.checked ? [...kinds, k] : kinds.filter((x) => x !== k))} /> {label}</label>
              ))}
            </fieldset>
            <QuizRunner key={kinds.join(",")} start={{ kind: "script", n: 10, script_kinds: kinds.length ? kinds : undefined }}
              startLabel="Start 10-question drill" intro="Identify letters, read syllables and conjuncts. Every question is freshly generated." />
          </div>) },
        { label: "📖 Reading practice", content: (
          <div className="center stack">
            <p className="muted">Read the word aloud, then reveal the transliteration.</p>
            <div className="dev dev-huge" lang="sa">{w.sanskrit}</div>
            <label><input type="checkbox" checked={show} onChange={(e) => setShow(e.target.checked)} /> Show transliteration</label>
            {show && <div className="muted">{w.iast}</div>}
            <div className="row"><button className="btn" onClick={() => setI(i - 1)}>← Previous</button><button className="btn btn-primary" onClick={() => setI(i + 1)}>Next →</button></div>
          </div>) },
      ]} />
    </div>
  );
}
