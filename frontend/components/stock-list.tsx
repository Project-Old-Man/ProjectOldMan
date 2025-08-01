"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, TrendingUp, TrendingDown, Star } from "lucide-react"

export default function StockList() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("전체")

  const categories = ["전체", "대형주", "중형주", "소형주", "ETF"]

  const stocks = [
    {
      name: "삼성전자",
      code: "005930",
      price: "71,200",
      change: "+1,200",
      changePercent: "+1.71%",
      isPositive: true,
      category: "대형주",
      volume: "12,345,678",
    },
    {
      name: "SK하이닉스",
      code: "000660",
      price: "89,400",
      change: "-800",
      changePercent: "-0.89%",
      isPositive: false,
      category: "대형주",
      volume: "8,765,432",
    },
    {
      name: "NAVER",
      code: "035420",
      price: "234,500",
      change: "+3,500",
      changePercent: "+1.52%",
      isPositive: true,
      category: "대형주",
      volume: "5,432,109",
    },
    {
      name: "카카오",
      code: "035720",
      price: "56,700",
      change: "-1,300",
      changePercent: "-2.24%",
      isPositive: false,
      category: "대형주",
      volume: "9,876,543",
    },
    {
      name: "LG에너지솔루션",
      code: "373220",
      price: "412,000",
      change: "+8,000",
      changePercent: "+1.98%",
      isPositive: true,
      category: "대형주",
      volume: "3,210,987",
    },
    {
      name: "셀트리온",
      code: "068270",
      price: "156,800",
      change: "-2,400",
      changePercent: "-1.51%",
      isPositive: false,
      category: "중형주",
      volume: "4,567,890",
    },
    {
      name: "현대차",
      code: "005380",
      price: "198,500",
      change: "+4,500",
      changePercent: "+2.32%",
      isPositive: true,
      category: "대형주",
      volume: "6,789,012",
    },
    {
      name: "KODEX 200",
      code: "069500",
      price: "34,250",
      change: "+125",
      changePercent: "+0.37%",
      isPositive: true,
      category: "ETF",
      volume: "15,432,876",
    },
  ]

  const filteredStocks = stocks.filter((stock) => {
    const matchesSearch = stock.name.toLowerCase().includes(searchTerm.toLowerCase()) || stock.code.includes(searchTerm)
    const matchesCategory = selectedCategory === "전체" || stock.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-6">
      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            type="text"
            placeholder="종목명 또는 종목코드 검색"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex space-x-2">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="whitespace-nowrap"
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Stock List */}
      <div className="grid gap-4">
        {filteredStocks.map((stock, index) => (
          <Card key={index} className="hover:shadow-md transition-all duration-200 cursor-pointer group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">{stock.name.charAt(0)}</span>
                  </div>

                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 transition-colors">
                        {stock.name}
                      </h3>
                      <Badge variant="secondary" className="text-xs">
                        {stock.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500">{stock.code}</p>
                    <p className="text-xs text-gray-400">거래량: {stock.volume}</p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-xl font-bold text-gray-900">{stock.price}원</p>
                  <div
                    className={`flex items-center justify-end space-x-1 ${stock.isPositive ? "text-green-600" : "text-red-600"}`}
                  >
                    {stock.isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    <span className="font-medium">{stock.change}</span>
                    <span className="text-sm">({stock.changePercent})</span>
                  </div>

                  <div className="flex items-center justify-end space-x-2 mt-2">
                    <Button size="sm" variant="outline" className="h-8 bg-transparent">
                      <Star className="w-3 h-3 mr-1" />
                      관심
                    </Button>
                    <Button size="sm" className="h-8">
                      매수
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredStocks.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">검색 결과가 없습니다.</p>
        </div>
      )}
    </div>
  )
}
