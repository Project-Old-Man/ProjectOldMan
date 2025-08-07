"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, DollarSign, PieChart, BarChart3 } from "lucide-react"

export default function PortfolioOverview() {
  const portfolioData = {
    totalValue: "12,450,000",
    totalInvestment: "10,000,000",
    totalProfit: "+2,450,000",
    profitPercent: "+24.5%",
    isPositive: true,
  }

  const holdings = [
    {
      name: "삼성전자",
      quantity: "50",
      avgPrice: "68,000",
      currentPrice: "71,200",
      value: "3,560,000",
      profit: "+160,000",
      profitPercent: "+4.71%",
      isPositive: true,
      weight: 28.6,
    },
    {
      name: "SK하이닉스",
      quantity: "20",
      avgPrice: "92,000",
      currentPrice: "89,400",
      value: "1,788,000",
      profit: "-52,000",
      profitPercent: "-2.83%",
      isPositive: false,
      weight: 14.4,
    },
    {
      name: "NAVER",
      quantity: "15",
      avgPrice: "220,000",
      currentPrice: "234,500",
      value: "3,517,500",
      profit: "+217,500",
      profitPercent: "+6.59%",
      isPositive: true,
      weight: 28.3,
    },
    {
      name: "카카오",
      quantity: "30",
      avgPrice: "60,000",
      currentPrice: "56,700",
      value: "1,701,000",
      profit: "-99,000",
      profitPercent: "-5.50%",
      isPositive: false,
      weight: 13.7,
    },
    {
      name: "LG에너지솔루션",
      quantity: "4",
      avgPrice: "400,000",
      currentPrice: "412,000",
      value: "1,648,000",
      profit: "+48,000",
      profitPercent: "+3.00%",
      isPositive: true,
      weight: 13.2,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="w-5 h-5" />
              <span>총 자산</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-gray-900">{portfolioData.totalValue}원</p>
              <div
                className={`flex items-center space-x-2 ${portfolioData.isPositive ? "text-green-600" : "text-red-600"}`}
              >
                {portfolioData.isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span className="font-medium">{portfolioData.totalProfit}원</span>
                <span className="text-sm">({portfolioData.profitPercent})</span>
              </div>
              <p className="text-sm text-gray-500">투자원금: {portfolioData.totalInvestment}원</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <PieChart className="w-5 h-5" />
              <span>보유 종목</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-gray-900">{holdings.length}개</p>
            <p className="text-sm text-gray-500">다양한 섹터에 분산투자</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>수익률</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">+24.5%</p>
            <p className="text-sm text-gray-500">연간 수익률 기준</p>
          </CardContent>
        </Card>
      </div>

      {/* Holdings */}
      <Card>
        <CardHeader>
          <CardTitle>보유 종목</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {holdings.map((holding, index) => (
              <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-sm">{holding.name.charAt(0)}</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{holding.name}</h3>
                      <p className="text-sm text-gray-500">{holding.quantity}주 보유</p>
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="font-bold text-gray-900">{holding.value}원</p>
                    <div
                      className={`flex items-center justify-end space-x-1 ${holding.isPositive ? "text-green-600" : "text-red-600"}`}
                    >
                      {holding.isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                      <span className="text-sm font-medium">{holding.profit}</span>
                      <span className="text-xs">({holding.profitPercent})</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>평균단가: {holding.avgPrice}원</span>
                    <span>현재가: {holding.currentPrice}원</span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">비중:</span>
                    <Progress value={holding.weight} className="flex-1 h-2" />
                    <span className="text-sm font-medium">{holding.weight}%</span>
                  </div>
                </div>

                <div className="flex space-x-2 mt-3">
                  <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                    추가매수
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                    매도
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
