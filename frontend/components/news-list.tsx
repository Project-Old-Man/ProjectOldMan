"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Clock, ExternalLink, TrendingUp } from "lucide-react"

export default function NewsList() {
  const [selectedCategory, setSelectedCategory] = useState("전체")

  const categories = ["전체", "시장동향", "기업뉴스", "경제지표", "해외증시"]

  const news = [
    {
      title: "삼성전자, 3분기 실적 시장 예상치 상회... 주가 상승 전망",
      summary: "삼성전자가 발표한 3분기 실적이 시장 예상치를 크게 상회하며 투자자들의 관심이 집중되고 있다.",
      category: "기업뉴스",
      time: "2시간 전",
      source: "한국경제",
      isHot: true,
    },
    {
      title: "미국 연준, 기준금리 동결 결정... 국내 증시에 미치는 영향은?",
      summary:
        "미국 연방준비제도가 기준금리를 현 수준에서 동결하기로 결정하면서 국내 증시에 미칠 파급효과에 관심이 모아지고 있다.",
      category: "해외증시",
      time: "4시간 전",
      source: "매일경제",
      isHot: true,
    },
    {
      title: "KOSPI 2,500선 돌파... 외국인 순매수 지속",
      summary: "KOSPI 지수가 2,500선을 돌파하며 강세를 보이고 있는 가운데, 외국인 투자자들의 순매수가 지속되고 있다.",
      category: "시장동향",
      time: "6시간 전",
      source: "서울경제",
      isHot: false,
    },
    {
      title: "SK하이닉스, HBM 수요 급증으로 4분기 실적 개선 기대",
      summary: "AI 반도체 수요 증가로 HBM(고대역폭메모리) 시장이 급성장하면서 SK하이닉스의 실적 개선이 기대된다.",
      category: "기업뉴스",
      time: "8시간 전",
      source: "전자신문",
      isHot: false,
    },
    {
      title: "10월 소비자물가 상승률 3.2%... 인플레이션 우려 지속",
      summary:
        "10월 소비자물가 상승률이 3.2%를 기록하며 인플레이션 우려가 지속되고 있어 통화정책에 미칠 영향이 주목된다.",
      category: "경제지표",
      time: "12시간 전",
      source: "연합뉴스",
      isHot: false,
    },
    {
      title: "NAVER, 클라우드 사업 확장으로 신성장 동력 확보",
      summary: "NAVER가 클라우드 사업 확장을 통해 새로운 성장 동력을 확보하고 있어 향후 실적 개선이 기대된다.",
      category: "기업뉴스",
      time: "1일 전",
      source: "IT조선",
      isHot: false,
    },
  ]

  const filteredNews = news.filter((item) => selectedCategory === "전체" || item.category === selectedCategory)

  return (
    <div className="space-y-6">
      {/* Category Filter */}
      <div className="flex space-x-2 overflow-x-auto pb-2">
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

      {/* News List */}
      <div className="space-y-4">
        {filteredNews.map((item, index) => (
          <Card key={index} className="hover:shadow-md transition-all duration-200 cursor-pointer group">
            <CardContent className="p-6">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center space-x-2">
                      {item.isHot && (
                        <Badge variant="destructive" className="text-xs">
                          <TrendingUp className="w-3 h-3 mr-1" />
                          HOT
                        </Badge>
                      )}
                      <Badge variant="secondary" className="text-xs">
                        {item.category}
                      </Badge>
                    </div>

                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors leading-tight">
                      {item.title}
                    </h3>

                    <p className="text-gray-600 text-sm leading-relaxed">{item.summary}</p>

                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{item.time}</span>
                      </div>
                      <span>출처: {item.source}</span>
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="icon"
                    className="ml-4 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredNews.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">해당 카테고리의 뉴스가 없습니다.</p>
        </div>
      )}
    </div>
  )
}
