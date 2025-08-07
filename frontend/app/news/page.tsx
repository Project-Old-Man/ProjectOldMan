import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import NewsList from "@/components/news-list"

export default function NewsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">투자 뉴스</h1>
            <p className="text-gray-600">최신 금융 뉴스와 시장 동향을 확인하세요</p>
          </div>
          <NewsList />
        </main>
      </div>
    </div>
  )
}
