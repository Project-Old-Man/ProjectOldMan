import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import StockList from "@/components/stock-list"

export default function StocksPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">주식 관리</h1>
            <p className="text-gray-600">투자 포트폴리오를 관리하고 분석하세요</p>
          </div>
          <StockList />
        </main>
      </div>
    </div>
  )
}
