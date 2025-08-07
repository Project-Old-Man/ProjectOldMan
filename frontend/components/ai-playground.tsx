"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Beaker, Wand2, FileText, Code, ImageIcon, Music } from "lucide-react"

export default function AIPlayground() {
  const [prompt, setPrompt] = useState("")
  const [temperature, setTemperature] = useState([0.7])
  const [maxTokens, setMaxTokens] = useState([1000])
  const [isGenerating, setIsGenerating] = useState(false)

  const experiments = [
    {
      id: "text",
      name: "텍스트 생성",
      icon: FileText,
      description: "창작, 요약, 번역 등 다양한 텍스트 작업",
      color: "from-blue-500 to-cyan-600",
    },
    {
      id: "code",
      name: "코드 생성",
      icon: Code,
      description: "프로그래밍 코드 작성 및 디버깅",
      color: "from-green-500 to-emerald-600",
    },
    {
      id: "image",
      name: "이미지 분석",
      icon: ImageIcon,
      description: "이미지 설명 및 분석 (곧 출시)",
      color: "from-purple-500 to-pink-600",
    },
    {
      id: "audio",
      name: "오디오 처리",
      icon: Music,
      description: "음성 인식 및 생성 (곧 출시)",
      color: "from-orange-500 to-red-600",
    },
  ]

  const presetPrompts = [
    {
      category: "창작",
      prompts: ["SF 소설의 첫 문단을 써주세요", "로맨틱 코미디 영화 시나리오 아이디어", "판타지 세계관 설정 만들기"],
    },
    {
      category: "코딩",
      prompts: ["React 컴포넌트 만들기", "Python 데이터 분석 스크립트", "API 설계 및 구현"],
    },
    {
      category: "비즈니스",
      prompts: ["마케팅 전략 수립", "사업 계획서 작성", "프레젠테이션 구성"],
    },
  ]

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)
    // Simulate API call
    setTimeout(() => {
      setIsGenerating(false)
    }, 2000)
  }

  return (
    <div className="space-y-6">
      {/* Experiment Types */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {experiments.map((experiment) => {
          const Icon = experiment.icon

          return (
            <Card key={experiment.id} className="hover:shadow-md transition-all duration-200 cursor-pointer group">
              <CardContent className="p-6 text-center">
                <div
                  className={`w-12 h-12 bg-gradient-to-br ${experiment.color} rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform`}
                >
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{experiment.name}</h3>
                <p className="text-sm text-gray-600">{experiment.description}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Playground */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Beaker className="w-5 h-5" />
                <span>AI 실험실</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="prompt">프롬프트</Label>
                <Textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="AI에게 요청할 작업을 자세히 설명해주세요..."
                  className="min-h-32 mt-2"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>창의성 (Temperature): {temperature[0]}</Label>
                  <Slider
                    value={temperature}
                    onValueChange={setTemperature}
                    max={1}
                    min={0}
                    step={0.1}
                    className="mt-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">높을수록 더 창의적이고 예측하기 어려운 결과</p>
                </div>

                <div>
                  <Label>최대 토큰 수: {maxTokens[0]}</Label>
                  <Slider
                    value={maxTokens}
                    onValueChange={setMaxTokens}
                    max={2000}
                    min={100}
                    step={100}
                    className="mt-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">생성할 텍스트의 최대 길이</p>
                </div>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="w-full bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-white"
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    생성 중...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4 mr-2" />
                    생성하기
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Results */}
          <Card>
            <CardHeader>
              <CardTitle>결과</CardTitle>
            </CardHeader>
            <CardContent>
              {isGenerating ? (
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-4/6"></div>
                </div>
              ) : (
                <div className="text-gray-500 text-center py-8">
                  <Beaker className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>프롬프트를 입력하고 생성하기 버튼을 눌러보세요!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Preset Prompts */}
          <Card>
            <CardHeader>
              <CardTitle>프롬프트 예시</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="창작" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="창작">창작</TabsTrigger>
                  <TabsTrigger value="코딩">코딩</TabsTrigger>
                  <TabsTrigger value="비즈니스">비즈니스</TabsTrigger>
                </TabsList>

                {presetPrompts.map((category) => (
                  <TabsContent key={category.category} value={category.category} className="space-y-2">
                    {category.prompts.map((presetPrompt, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="w-full text-left justify-start h-auto p-3 text-wrap bg-transparent"
                        onClick={() => setPrompt(presetPrompt)}
                      >
                        {presetPrompt}
                      </Button>
                    ))}
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle>💡 팁</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <h4 className="font-medium text-gray-900">구체적으로 요청하세요</h4>
                <p className="text-gray-600">원하는 결과를 자세히 설명할수록 더 좋은 결과를 얻을 수 있습니다.</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">예시를 포함하세요</h4>
                <p className="text-gray-600">원하는 형식이나 스타일의 예시를 제공하면 도움이 됩니다.</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">단계별로 요청하세요</h4>
                <p className="text-gray-600">복잡한 작업은 여러 단계로 나누어 요청하는 것이 효과적입니다.</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
