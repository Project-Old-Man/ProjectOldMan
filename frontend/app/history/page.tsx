import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import ChatHistory from "@/components/chat-history"

export default function HistoryPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">대화 기록</h1>
            <p className="text-gray-600">이전 AI와의 대화 내용을 확인하고 이어서 대화하세요</p>
          </div>
          <ChatHistory />
        </main>
      </div>
    </div>
  )
}
