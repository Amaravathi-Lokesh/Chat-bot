export default function ChatSidebar({ chats, activeChat, setActiveChat }) {
  return (
    <div className="h-full flex flex-col bg-gray-900 border-r border-gray-800">

      {/* HEADER */}
      <div className="p-4 text-cyan-400 font-bold border-b border-gray-800">
        My Chats
      </div>
             <button
    onClick={logout}
    className="px-3 py-1 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg"
  >
    Logout
  </button>
      {/* CHAT LIST */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">

        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => setActiveChat(chat.id)}
            className={`p-3 rounded-lg cursor-pointer transition
              ${
                activeChat === chat.id
                  ? "bg-cyan-500 text-black"
                  : "bg-gray-800 hover:bg-gray-700"
              }`}
          >
            {chat.title}
          </div>
        ))}
  
      </div>
    </div>
    
  );

}