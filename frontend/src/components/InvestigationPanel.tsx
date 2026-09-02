import { Bot, Send, UserRound } from "lucide-react";
import { useState } from "react";
import type { Project } from "../types";

interface InvestigationPanelProps { project: Project; }

export function InvestigationPanel({ project }: InvestigationPanelProps) {
  const [messages, setMessages] = useState([
    { from: "ai", text: `The highest-risk project is ${project.title}. Main drivers are ${project.anomalyTypes.join(", ") || "routine monitoring signals"}.` },
    { from: "officer", text: "What should the district officer verify first?" },
    { from: "ai", text: "Verify physical progress photos, BOQ line items, and latest fund-release vouchers before approving the next tranche." }
  ]);
  const [draft, setDraft] = useState("");

  function sendMessage() {
    if (!draft.trim()) return;
    setMessages((existing) => [
      ...existing,
      { from: "officer", text: draft.trim() },
      { from: "ai", text: "Mock AI response: I would cross-check project similarity, agency history, geo-tagged inspection evidence, and utilization variance. Backend integration can replace this response later." }
    ]);
    setDraft("");
  }

  return (
    <section className="panel investigation-panel">
      <div className="panel-header"><div><span className="eyebrow">Level 4</span><h2>AI investigation workspace</h2></div><Bot size={20} /></div>
      <div className="chat-window">
        {messages.map((message, index) => (
          <div className={`chat-bubble ${message.from}`} key={`${message.from}-${index}`}>{message.from === "ai" ? <Bot size={16} /> : <UserRound size={16} />}<p>{message.text}</p></div>
        ))}
      </div>
      <div className="chat-input">
        <input value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => event.key === "Enter" && sendMessage()} placeholder="Ask about risk, evidence, duplicate work, or agency history" />
        <button onClick={sendMessage} aria-label="Send investigation question"><Send size={16} /></button>
      </div>
    </section>
  );
}

