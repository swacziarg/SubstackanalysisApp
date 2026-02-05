import { useEffect, useState } from "react";
import { compareAuthors } from "../api";
import { api } from "../api";


export default function Compare() {
const [authors, setAuthors] = useState([]);
const [a, setA] = useState("");
const [b, setB] = useState("");
const [result, setResult] = useState(null);


useEffect(() => {
api.get("/authors").then(r => setAuthors(r.data));
}, []);


const run = async () => {
if (!a || !b) return;
const r = await compareAuthors(a,b);
setResult(r.data);
};


return (
<div style={{ maxWidth: 900, margin: "auto" }}>
<h1>Compare Thinkers</h1>


<div style={{ display:"flex", gap:10 }}>
<select value={a} onChange={e=>setA(e.target.value)}>
<option value="">Author A</option>
{authors.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}
</select>


<select value={b} onChange={e=>setB(e.target.value)}>
<option value="">Author B</option>
{authors.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}
</select>


<button onClick={run}>Compare</button>
</div>


{result && (
<div style={{ marginTop:30 }}>
<h2>Agreement</h2>
<ul>{result.agreement?.map((x,i)=><li key={i}>{x}</li>)}</ul>


<h2>Disagreement</h2>
<ul>{result.disagreement?.map((x,i)=><li key={i}>{JSON.stringify(x)}</li>)}</ul>


<h2>Unique to A</h2>
<ul>{result.unique_to_a?.map((x,i)=><li key={i}>{x}</li>)}</ul>


<h2>Unique to B</h2>
<ul>{result.unique_to_b?.map((x,i)=><li key={i}>{x}</li>)}</ul>
</div>
)}
</div>
);
}