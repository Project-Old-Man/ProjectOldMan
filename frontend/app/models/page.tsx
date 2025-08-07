import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import ModelSelection from "@/components/model-selection"

export default function ModelsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">AI 모델 선택</h1>
            <p className="text-gray-600">다양한 AI 모델 중에서 선택하여 대화해보세요</p>
          </div>
          <ModelSelection />
        </main>
      </div>
    </div>
  )
}
