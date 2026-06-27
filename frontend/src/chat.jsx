import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter }from "react-syntax-highlighter";
import { oneDark }from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
export default function Chat() {
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const bottomRef = useRef(null);
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const userId = localStorage.getItem("user");

  // ================= LOAD CHATS =================
  useEffect(() => {
    if (!userId) return;

    fetch(`https://chat-bot-xlrz.onrender.com/chat/list/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        setChats(data || []);

        if (data?.length > 0) {
          setActiveChat(data[0].id);
        }
      })
      .catch(console.error);
  }, [userId]);

  // ================= LOAD MESSAGES =================
 // ================= LOAD MESSAGES =================
useEffect(() => {
  if (!activeChat) {
    setMessages([]);
    setInput("");
    return;
  }

  setInput("");

  fetch(`https://chat-bot-xlrz.onrender.com/chat/history/${activeChat}`)
    .then((res) => res.json())
    .then((data) => {
      setMessages(data || []);
    })
    .catch(console.error);

}, [activeChat]);

//   console.log("SEND BUTTON CLICKED");
// console.log("Active Chat:", activeChat);
// console.log("User:", userId);
// console.log("Input:", input);
  const loadChats = async () => {
    try {
      const res = await fetch(`https://chat-bot-xlrz.onrender.com/chat/list/${userId}`);
      const data = await res.json();
      setChats(data);
    } catch (err) {
      console.log(err);
    }
  };
  // ================= CREATE CHAT =================
  const createNewChat = async () => {
  try {
    const res = await fetch(
      "https://chat-bot-xlrz.onrender.com/chat/create",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          title: "New Chat",
        }),
      }
      
    );

    const data = await res.json();

    const newChat = {
      id: data.chat_id,
      title: data.title,
    };

    setChats((prev) => [newChat, ...prev]);

    setActiveChat(newChat.id);

    setMessages([]);
    setInput("");

  } catch (err) {
    console.log(err);
  }
  setSidebarOpen(false);
};// console.log("chat:",data.id);
  // ================= DELETE CHAT =================
  const deleteChat = async (chatId) => {
    const confirmDelete = window.confirm("Delete this chat?");
    if (!confirmDelete) return;

    await fetch(
      `https://chat-bot-xlrz.onrender.com/chat/delete/${chatId}`,
      { method: "DELETE" }
    );

    setChats((prev) => prev.filter((c) => c.id !== chatId));

    if (activeChat === chatId) {
      setActiveChat(null);
      setMessages([]);
      setInput("");
    }
  };
  
  // ================= SEND MESSAGE =================
  const sendMessage = async () => {
  if (!input.trim() || !activeChat) return;

  const msg = input.trim();
  const token=localStorage.getItem("access_token");
  const isFirstMessage = messages.length === 0;

  setInput("");
  setLoading(true);

  setMessages(prev => [
    ...prev,
    {
      role: "user",
      content: msg
    }
  ]);

  try {

    const res = await fetch(
      "https://chat-bot-xlrz.onrender.com/chat/send",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          // user_id: userId,
          chat_id: activeChat,
          message: msg
        })
      }
    );

    const data = await res.json();

    setMessages(prev => [
      ...prev,
      {
        role: "assistant",
        content: data.message || "No response"
      }
    ]);

    // Auto rename first message
    if (isFirstMessage) {

      const smartTitle =
        msg.split(" ").slice(0, 4).join(" ") + "...";

      await fetch(
        `https://chat-bot-xlrz.onrender.com/chat/rename/${activeChat}?title=${encodeURIComponent(smartTitle)}`,
        {
          method: "PUT"
        }
      );

      await loadChats();
    }

  } catch (err) {

    console.error(err);

    setMessages(prev => [
      ...prev,
      {
        role: "assistant",
        content: "⚠️ Server Error"
      }
    ]);

  } finally {

    setLoading(false);

  }
};
  //=================Streaming response=================
  const sendStreamMessage = async () => {

  if (!input.trim() || !activeChat) return;

  const msg = input.trim();

  setInput("");

  setMessages(prev => [
    ...prev,
    {
      role: "user",
      content: msg
    }
  ]);

  // Empty assistant message
  setMessages(prev => [
    ...prev,
    {
      role: "assistant",
      content: ""
    }
  ]);

  const response = await fetch(
    "https://chat-bot-xlrz.onrender.com/chat/stream",
    {
      method: "POST",
      headers: {
        "Content-Type":"application/json"
      },
      body: JSON.stringify({
        user_id:userId,
        chat_id:activeChat,
        message:msg
      })
    }
  );
  if(!response.ok){

  setMessages(prev=>[
    ...prev,
    {
      role:"assistant",
      content:"Server Error"
    }
  ]);

  return;

}
  const reader = response.body.getReader();

  const decoder = new TextDecoder();

  let result = "";

  while(true){

    const {done,value}=await reader.read();

    if(done) break;

    result += decoder.decode(value);

    setMessages(prev=>{

      const updated=[...prev];

      updated[updated.length-1]={
        role:"assistant",
        content:result
      };

      return updated;

    });

  }

}

  // ================= LOGOUT =================
 const logout = () => {
  localStorage.clear();
  setChats([]);
  setMessages([]);
  setInput("");
  setActiveChat(null);
  navigate("/");
};
//================File download =================
const uploadFile = async () => {
  if (!file) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();

  formData.append("file", file);
  formData.append("user_id", userId);
  formData.append("chat_id", activeChat);

  try {
    const res = await fetch(
      "https://chat-bot-xlrz.onrender.com/upload/document",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();

    console.log("Status:", res.status);
    console.log(data);

    if (!res.ok) {
      alert(JSON.stringify(data));
      return;
    }

    alert("PDF uploaded successfully!");

  } catch (err) {
    console.log(err);
  }
};
//================ copy to clipboard =================
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 text-xs bg-slate-700 px-2 py-1 rounded"
    >
      {copied ? "Copied" : "Copy"}
    </button>
  );
}
// =================typing animation =================
function TypingIndicator() {
  return (
    <div className="flex gap-1 text-slate-400 p-2">
      <span className="animate-bounce">●</span>
      <span className="animate-bounce delay-150">●</span>
      <span className="animate-bounce delay-300">●</span>
    </div>
  );
}

  // ================= AUTO SCROLL =================
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
  <div className="h-screen w-screen flex flex-col md:flex-row bg-slate-950 text-white overflow-hidden">
        {/* Hamburger */}
    <div className="md:hidden absolute top-4 left-4 z-50">
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="bg-slate-800 p-2 rounded"
      >
        ☰
      </button>
    </div>

    {sidebarOpen && (
  <div
    className="fixed inset-0 bg-black/50 z-40 md:hidden"
    onClick={() => setSidebarOpen(false)}
  />
)}
    {/* ================= SIDEBAR ================= */}
    <div
  className={`
    fixed md:relative z-50
    h-full w-72 bg-slate-900 border-r border-slate-800
    transform transition-transform duration-300
    ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
    md:translate-x-0
  `}
>

      {/* TOP ACTIONS */}
      <div className="p-3 space-y-2 border-b border-slate-800">
         <button
    onClick={() => setSidebarOpen(false)}
    className="text-xl text-white"
  >
    ✕
  </button>
        <button
          onClick={logout}
          className="w-full bg-red-500 p-2 rounded hover:bg-red-400"
        >
          Logout
        </button>

        <button
          onClick={createNewChat}
          className="w-full bg-cyan-500 p-2 rounded text-black font-semibold"
        >
          + New Chat
        </button>

      </div>
        <div>
      <input
        type="file"
        accept=".pdf"
        className="w-full text-xs md:text-sm"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={() => uploadFile()}
        className="w-full bg-cyan-500 p-2 rounded text-black font-semibold">
        Upload PDF
      </button>
    </div>
      {/* CHAT LIST */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">

        {chats.map((c, index) => (
          <div
            key={c.id || index}
            className={`flex justify-between items-center p-2 rounded cursor-pointer ${
              activeChat === c.id
                ? "bg-cyan-500 text-black"
                : "bg-slate-800"
            }`}
          >
            <div
              className="flex-1"
              onClick={() => {
  setActiveChat(c.id);
  setInput("");
  setSidebarOpen(false);
}}
            >
              {c.title}
            </div>

            <button
              onClick={() => deleteChat(c.id)}
              className="text-red-400 hover:text-red-200"
            >
              ✕
            </button>
          </div>
        ))}

      </div>
      
    </div>

    {/* ================= CHAT AREA ================= */}
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/*mobile header */}
     
      {/* MESSAGES AREA */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">

     {messages.map((m, i) => (
  <div
    key={i}
    className={`flex mb-4 ${
      m.role === "user" ? "justify-end" : "justify-start"
    }`}
  >
    <div
      className={`relative max-w-[90%] md:max-w-[75%] p-4 rounded-xl text-left whitespace-pre-wrap break-words ${
        m.role === "user"
          ? "bg-cyan-500 text-black"
          : "bg-slate-900 text-white"
      }`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
         code({ className, children }) {
  const match = /language-(\w+)/.exec(className || "");
  const codeString = String(children).replace(/\n$/, "");

  if (match) {
    return (
      <div className="relative my-3">
        <CopyButton text={codeString} />

        <SyntaxHighlighter
            language={match?.[1] || "text"}
  style={oneDark}
  wrapLongLines={true}
  customStyle={{
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    overflowX: "auto",
    padding: "15px",
    borderRadius: "10px",
          }}
        >
          {codeString}
        </SyntaxHighlighter>
      </div>
    );
  }

  return (
    <code className="bg-slate-700 px-1 py-0.5 rounded">
      {children}
    </code>
  );
},

          p: ({ children }) => (
            <p className="mb-2 leading-relaxed">{children}</p>
          ),
        }}
      >
        {typeof m.content === "string"
          ? m.content
          : String(m.content)}
      </ReactMarkdown>
    </div>
  </div>
))}
        {loading && (
          <TypingIndicator />
        )}

        <div ref={bottomRef}></div>
      </div>

      {/* INPUT AREA */}
      <div className="p-2 md:p-3 border-t border-slate-800 bg-slate-900 flex gap-2">

        <input
          className="flex-1 p-2 md:p-3 bg-slate-800 rounded text-sm md:text-base"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type a message..."
        />

        <button
          onClick={sendMessage}
          className="bg-cyan-500 px-3 md:px-5 rounded text-sm md:text-base"
        >
          Send
        </button>

      </div>

    </div>
  </div>
);
}
