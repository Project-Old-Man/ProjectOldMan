"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, MessageSquare, Calendar, Trash2, Star } from "lucide-react"

export default function ChatHistory() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedFilter, setSelectedFilter] = useState("전체")

  const filters = ["전체", "즐겨찾기", "오늘", "이번 주", "이번 달"]

  const chatHistory = [
    {
      id: 1,
      title: "Python 웹 스크래핑 도움",
      preview: "BeautifulSoup을 사용해서 웹사이트에서 데이터를 추출하는 방법을 알려주세요...",
      date: "2024-01-15",
      time: "14:30",
      messageCount: 12,
      model: "GPT-4",
      isFavorite: true,
      category: "코딩",
    },
    {
      id: 2,
      title: "일본 여행 계획 세우기",
      preview: "3박 4일 도쿄 여행 일정을 짜고 싶어요. 추천 장소와 맛집을 알려주세요...",
      date: "2024-01-15",
      time: "10:15",
      messageCount: 8,
      model: "GPT-3.5",
      isFavorite: false,
      category: "여행",
    },
    {
      id: 3,
      title: "영어 이메일 작성 도움",
      preview: "비즈니스 이메일을 영어로 작성하는데 도움이 필요해요...",
      date: "2024-01-14",
      time: "16:45",
      messageCount: 6,
      model: "Claude",
      isFavorite: true,
      category: "언어",
    },
    {
      id: 4,
      title: "React 컴포넌트 최적화",
      preview: "React 컴포넌트의 렌더링 성능을 개선하는 방법에 대해 알려주세요...",
      date: "2024-01-14",
      time: "09:20",
      messageCount: 15,
      model: "GPT-4",
      isFavorite: false,
      category: "코딩",
    },
    {
      id: 5,
      title: "건강한 다이어트 식단",
      preview: "체중 감량을 위한 건강한 식단을 추천해주세요...",
      date: "2024-01-13",
      time: "19:30",
      messageCount: 10,
      model: "Gemini",
      isFavorite: false,
      category: "건강",
    },
    {
      id: 6,
      title: "창업 아이디어 브레인스토밍",
      preview: "IT 분야에서 창업할 수 있는 아이디어들을 함께 생각해봐요...",
      date: "2024-01-12",
      time: "13:15",
      messageCount: 20,
      model: "GPT-4",
      isFavorite: true,
      category: "비즈니스",
    },
  ]

  const filteredHistory = chatHistory.filter((chat) => {
    const matchesSearch =
      chat.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chat.preview.toLowerCase().includes(searchTerm.toLowerCase())

    let matchesFilter = true
    if (selectedFilter === "즐겨찾기") {
      matchesFilter = chat.isFavorite
    } else if (selectedFilter === "오늘") {
      matchesFilter = chat.date === "2024-01-15"
    } else if (selectedFilter === "이번 주") {
      matchesFilter = ["2024-01-15", "2024-01-14", "2024-01-13"].includes(chat.date)
    }

    return matchesSearch && matchesFilter
  })

  const getCategoryColor = (category: string) => {
    const colors = {
      코딩: "bg-blue-100 text-blue-800",
      여행: "bg-green-100 text-green-800",
      언어: "bg-purple-100 text-purple-800",
      건강: "bg-red-100 text-red-800",
      비즈니스: "bg-yellow-100 text-yellow-800",
    }
    return colors[category as keyof typeof colors] || "bg-gray-100 text-gray-800"
  }

  return (
    <div className="space-y-6">
      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            type="text"
            placeholder="대화 내용 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex space-x-2">
          {filters.map((filter) => (
            <Button
              key={filter}
              variant={selectedFilter === filter ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedFilter(filter)}
              className={`whitespace-nowrap ${
                selectedFilter === filter ? "bg-yellow-500 hover:bg-yellow-600 text-white" : ""
              }`}
            >
              {filter}
            </Button>
          ))}
        </div>
      </div>

      {/* Chat History List */}
      <div className="space-y-4">
        {filteredHistory.map((chat) => (
          <Card key={chat.id} className="hover:shadow-md transition-all duration-200 cursor-pointer group">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1 space-y-3">
                  <div className="flex items-center space-x-3">
                    <MessageSquare className="w-5 h-5 text-yellow-500" />
                    <h3 className="font-bold text-lg text-gray-900 group-hover:text-yellow-600 transition-colors">
                      {chat.title}
                    </h3>
                    {chat.isFavorite && <Star className="w-4 h-4 text-yellow-500 fill-current" />}
                  </div>

                  <p className="text-gray-600 text-sm leading-relaxed line-clamp-2">{chat.preview}</p>

                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3" />
                      <span>
                        {chat.date} {chat.time}
                      </span>
                    </div>
                    <span>{chat.messageCount}개 메시지</span>
                    <Badge variant="secondary" className="text-xs">
                      {chat.model}
                    </Badge>
                    <Badge className={`text-xs ${getCategoryColor(chat.category)}`}>{chat.category}</Badge>
                  </div>
                </div>

                <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={(e) => {
                      e.stopPropagation()
                      // Toggle favorite
                    }}
                  >
                    <Star className={`w-4 h-4 ${chat.isFavorite ? "text-yellow-500 fill-current" : "text-gray-400"}`} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-red-500 hover:text-red-600"
                    onClick={(e) => {
                      e.stopPropagation()
                      // Delete chat
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredHistory.length === 0 && (
        <div className="text-center py-12">
          <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">검색 결과가 없습니다.</p>
          <p className="text-gray-400 text-sm mt-1">다른 검색어를 시도해보세요.</p>
        </div>
      )}
    </div>
  )
}
