"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Send, User, Copy, ThumbsUp, ThumbsDown, Sparkles } from "lucide-react"

interface Message {
  id: number
  type: "user" | "ai"
  content: string
  timestamp: Date
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: "ai",
      content:
        "안녕하세요! AI놀이터에 오신 것을 환영합니다! 🎉\n\n저는 여러분의 AI 어시스턴트입니다. 무엇이든 물어보세요:\n\n• 코딩 도움이 필요하신가요?\n• 창작 활동을 도와드릴까요?\n• 학습이나 연구 질문이 있으신가요?\n• 일상적인 대화를 나누고 싶으신가요?\n\n편하게 말씀해 주세요!",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: Date.now() + 1,
        type: "ai",
        content: `좋은 질문이네요! "${inputValue}"에 대해 답변드리겠습니다.\n\n이것은 시뮬레이션된 AI 응답입니다. 실제 AI 모델을 연결하면 더 정확하고 유용한 답변을 받을 수 있습니다.\n\n더 궁금한 것이 있으시면 언제든 물어보세요! 😊`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`flex space-x-3 max-w-3xl ${message.type === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === "user" ? "bg-gray-600" : "bg-gradient-to-br from-yellow-400 to-yellow-600"
                }`}
              >
                {message.type === "user" ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Sparkles className="w-4 h-4 text-white" />
                )}
              </div>

              {/* Message Content */}
              <Card className={`${message.type === "user" ? "bg-gray-600 text-white" : "bg-white border-gray-200"}`}>
                <CardContent className="p-4">
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>

                  {message.type === "ai" && (
                    <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-gray-100">
                      <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                        <Copy className="w-3 h-3 mr-1" />
                        복사
                      </Button>
                      <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                        <ThumbsUp className="w-3 h-3" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                        <ThumbsDown className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex space-x-3 max-w-3xl">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <Card className="bg-white border-gray-200">
                <CardContent className="p-4">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="AI에게 무엇이든 물어보세요..."
                className="pr-12 py-3 text-sm border-gray-300 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                disabled={isTyping}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                size="sm"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-white"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <p className="text-xs text-gray-500 mt-2 text-center">
            AI는 실수할 수 있습니다. 중요한 정보는 다시 한 번 확인해 주세요.
          </p>
        </div>
      </div>
    </div>
  )
}
