import React from "react";

const App = () => {
  return (
    <div className="flex h-screen">
      {/* Left Sidebar (Chat Section) */}
      <div className="w-1/3 bg-gray-100 p-4 border-r border-gray-300 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Chat</h2>
        <div className="h-5/6 overflow-y-auto p-2 border rounded bg-white">
          {/* Chat messages will be displayed here */}
          <div className="mb-2">
            <p className="text-sm text-gray-600">Son cevapta kullanilan urunler bazinda yorumlar</p>
          </div>
        </div>
        <div className="flex gap-2 mt-2">
          <input
            type="text"
            placeholder="Mesajınızı yazın..."
            className="flex-1 p-2 border rounded"
          />
          <button
            type="button"
            onClick={() => handleSubmit()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:ring-2 focus:ring-blue-300 focus:outline-none"
            aria-label="Mesaj gönder"
          >
            Gönder
          </button>
        </div>
      </div>

      {/* Right Side (Three Info Sections) */}
      <div className="w-2/3 grid grid-cols-1 gap-4 p-4">
        <div className="border p-4 rounded bg-white shadow-md">
          <h2 className="text-lg font-bold mb-2">Toplam token</h2>
          <div className="w-full p-2 border rounded bg-gray-50">0</div>
        </div>
        
        <div className="border p-4 rounded bg-white shadow-md">
          <h2 className="text-lg font-bold mb-2">Cevap verme suresi</h2>
          <div className="w-full p-2 border rounded bg-gray-50">0ms</div>
        </div>

        <div className="border p-4 rounded bg-white shadow-md">
          <h2 className="text-lg font-bold mb-2">Son cevapta kullanilan urunler ve ozellikler</h2>
          <div className="w-full p-2 border rounded bg-gray-50">-</div>
        </div>
      </div>
    </div>
  );
};

export default App;