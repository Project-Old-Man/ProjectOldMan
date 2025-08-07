import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import AIPlayground from "@/components/ai-playground"

export default function PlaygroundPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">AI 실험실</h1>
            <p className="text-gray-600">다양한 AI 기능을 실험하고 테스트해보세요</p>
          </div>
          <AIPlayground />
        </main>
      </div>
    </div>
  )
}
