import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import PortfolioOverview from "@/components/portfolio-overview"

export default function PortfolioPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">내 자산</h1>
            <p className="text-gray-600">포트폴리오 현황과 수익률을 확인하세요</p>
          </div>
          <PortfolioOverview />
        </main>
      </div>
    </div>
  )
}
