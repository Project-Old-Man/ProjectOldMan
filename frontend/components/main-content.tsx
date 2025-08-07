"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { TrendingUp, TrendingDown, DollarSign, Activity } from "lucide-react"

export default function MainContent() {
  const [activeTab, setActiveTab] = useState("전체")

  const tabs = ["전체", "국내", "해외"]

  const marketData = [
    {
      name: "KOSPI",
      value: "2,456.78",
      change: "+12.34",
      changePercent: "+0.51%",
      isPositive: true,
    },
    {
      name: "KOSDAQ",
      value: "756.89",
      change: "-3.21",
      changePercent: "-0.42%",
      isPositive: false,
    },
    {
      name: "S&P 500",
      value: "4,123.45",
      change: "+8.76",
      changePercent: "+0.21%",
      isPositive: true,
    },
  ]

  const popularStocks = [
    { name: "삼성전자", code: "005930", price: "71,200", change: "+1,200", changePercent: "+1.71%", isPositive: true },
    { name: "SK하이닉스", code: "000660", price: "89,400", change: "-800", changePercent: "-0.89%", isPositive: false },
    { name: "NAVER", code: "035420", price: "234,500", change: "+3,500", changePercent: "+1.52%", isPositive: true },
    { name: "카카오", code: "035720", price: "56,700", change: "-1,300", changePercent: "-2.24%", isPositive: false },
    {
      name: "LG에너지솔루션",
      code: "373220",
      price: "412,000",
      change: "+8,000",
      changePercent: "+1.98%",
      isPositive: true,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {marketData.map((market, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{market.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{market.value}</p>
                </div>
                <div className={`flex items-center space-x-1 ${market.isPositive ? "text-green-600" : "text-red-600"}`}>
                  {market.isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <div className="text-right">
                    <p className="text-sm font-medium">{market.change}</p>
                    <p className="text-xs">{market.changePercent}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
        {tabs.map((tab) => (
          <Button
            key={tab}
            variant={activeTab === tab ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium transition-all duration-200 ${
              activeTab === tab ? "bg-white text-gray-900 shadow-sm" : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab}
          </Button>
        ))}
      </div>

      {/* Popular Stocks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>인기 종목</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {popularStocks.map((stock, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors duration-200 cursor-pointer group"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{stock.name.charAt(0)}</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                      {stock.name}
                    </p>
                    <p className="text-sm text-gray-500">{stock.code}</p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="font-bold text-gray-900">{stock.price}원</p>
                  <div
                    className={`flex items-center space-x-1 ${stock.isPositive ? "text-green-600" : "text-red-600"}`}
                  >
                    {stock.isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    <span className="text-sm font-medium">{stock.change}</span>
                    <span className="text-sm">({stock.changePercent})</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow duration-200 cursor-pointer group">
          <CardContent className="p-6 text-center">
            <DollarSign className="w-8 h-8 mx-auto mb-2 text-green-600 group-hover:scale-110 transition-transform" />
            <p className="font-medium text-gray-900">매수 주문</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow duration-200 cursor-pointer group">
          <CardContent className="p-6 text-center">
            <TrendingDown className="w-8 h-8 mx-auto mb-2 text-red-600 group-hover:scale-110 transition-transform" />
            <p className="font-medium text-gray-900">매도 주문</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow duration-200 cursor-pointer group">
          <CardContent className="p-6 text-center">
            <Activity className="w-8 h-8 mx-auto mb-2 text-blue-600 group-hover:scale-110 transition-transform" />
            <p className="font-medium text-gray-900">시장 분석</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow duration-200 cursor-pointer group">
          <CardContent className="p-6 text-center">
            <TrendingUp className="w-8 h-8 mx-auto mb-2 text-purple-600 group-hover:scale-110 transition-transform" />
            <p className="font-medium text-gray-900">포트폴리오</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
