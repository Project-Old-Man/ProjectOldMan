"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bot, Zap, Brain, Sparkles, Star } from "lucide-react"

export default function ModelSelection() {
  const [selectedModel, setSelectedModel] = useState("gpt-4")

  const models = [
    {
      id: "gpt-4",
      name: "GPT-4",
      description: "가장 강력한 언어 모델로 복잡한 추론과 창작 작업에 최적화",
      capabilities: ["텍스트 생성", "코딩", "분석", "창작"],
      speed: "보통",
      quality: "최고",
      icon: Brain,
      color: "from-blue-500 to-purple-600",
      popular: true,
    },
    {
      id: "gpt-3.5",
      name: "GPT-3.5 Turbo",
      description: "빠르고 효율적인 모델로 일반적인 대화와 작업에 적합",
      capabilities: ["대화", "요약", "번역", "Q&A"],
      speed: "빠름",
      quality: "좋음",
      icon: Zap,
      color: "from-green-500 to-teal-600",
      popular: false,
    },
    {
      id: "claude",
      name: "Claude",
      description: "안전하고 도움이 되는 AI로 윤리적 고려사항이 중요한 작업에 최적",
      capabilities: ["분석", "글쓰기", "연구", "토론"],
      speed: "보통",
      quality: "높음",
      icon: Sparkles,
      color: "from-orange-500 to-red-600",
      popular: false,
    },
    {
      id: "gemini",
      name: "Gemini Pro",
      description: "Google의 최신 멀티모달 AI로 텍스트와 이미지를 함께 처리",
      capabilities: ["멀티모달", "이미지 분석", "코딩", "수학"],
      speed: "빠름",
      quality: "높음",
      icon: Bot,
      color: "from-yellow-500 to-orange-600",
      popular: false,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Current Selection */}
      <Card className="border-yellow-200 bg-yellow-50">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-gray-900">현재 선택된 모델</h3>
              <p className="text-gray-600">
                {models.find((m) => m.id === selectedModel)?.name} -{" "}
                {models.find((m) => m.id === selectedModel)?.description}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((model) => {
          const Icon = model.icon
          const isSelected = selectedModel === model.id

          return (
            <Card
              key={model.id}
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                isSelected ? "ring-2 ring-yellow-500 border-yellow-300" : "hover:border-gray-300"
              }`}
              onClick={() => setSelectedModel(model.id)}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-10 h-10 bg-gradient-to-br ${model.color} rounded-lg flex items-center justify-center`}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{model.name}</CardTitle>
                      {model.popular && (
                        <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300">
                          <Star className="w-3 h-3 mr-1" />
                          인기
                        </Badge>
                      )}
                    </div>
                  </div>
                  {isSelected && (
                    <div className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <p className="text-gray-600 text-sm leading-relaxed">{model.description}</p>

                <div className="space-y-3">
                  <div>
                    <h4 className="font-medium text-sm text-gray-900 mb-2">주요 기능</h4>
                    <div className="flex flex-wrap gap-1">
                      {model.capabilities.map((capability) => (
                        <Badge key={capability} variant="secondary" className="text-xs">
                          {capability}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">속도:</span>
                      <span className="ml-2 font-medium">{model.speed}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">품질:</span>
                      <span className="ml-2 font-medium">{model.quality}</span>
                    </div>
                  </div>
                </div>

                <Button
                  className={`w-full ${
                    isSelected
                      ? "bg-yellow-500 hover:bg-yellow-600 text-white"
                      : "bg-gray-100 hover:bg-gray-200 text-gray-700"
                  }`}
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedModel(model.id)
                  }}
                >
                  {isSelected ? "선택됨" : "선택하기"}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Model Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>모델 비교</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">모델</th>
                  <th className="text-left py-2">속도</th>
                  <th className="text-left py-2">품질</th>
                  <th className="text-left py-2">특징</th>
                </tr>
              </thead>
              <tbody>
                {models.map((model) => (
                  <tr key={model.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-medium">{model.name}</td>
                    <td className="py-3">{model.speed}</td>
                    <td className="py-3">{model.quality}</td>
                    <td className="py-3">{model.capabilities.join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
