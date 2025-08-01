"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { MessageSquare, Bot, Beaker, History, Settings, HelpCircle, Plus, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Sidebar() {
  const pathname = usePathname()

  const sidebarItems = [
    { href: "/", icon: MessageSquare, label: "새 채팅", key: "chat" },
    { href: "/models", icon: Bot, label: "AI 모델", key: "models" },
    { href: "/playground", icon: Beaker, label: "실험실", key: "playground" },
    { href: "/history", icon: History, label: "대화 기록", key: "history" },
  ]

  const bottomItems = [
    { href: "/settings", icon: Settings, label: "설정", key: "settings" },
    { href: "/help", icon: HelpCircle, label: "도움말", key: "help" },
  ]

  const recentChats = [
    { id: 1, title: "Python 코딩 도움", time: "2시간 전" },
    { id: 2, title: "여행 계획 세우기", time: "어제" },
    { id: 3, title: "레시피 추천", time: "2일 전" },
    { id: 4, title: "영어 번역", time: "3일 전" },
  ]

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <div className="p-4">
        {/* New Chat Button */}
        <Button className="w-full mb-6 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-white">
          <Plus className="w-4 h-4 mr-2" />새 채팅 시작
        </Button>

        {/* Main Navigation */}
        <nav className="space-y-2 mb-6">
          {sidebarItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href

            return (
              <Link
                key={item.key}
                href={item.href}
                className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-yellow-50 text-yellow-600 border-r-2 border-yellow-600"
                    : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? "text-yellow-600" : "text-gray-500"}`} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Recent Chats */}
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">최근 대화</h3>
          <div className="space-y-1">
            {recentChats.map((chat) => (
              <Link
                key={chat.id}
                href={`/chat/${chat.id}`}
                className="block px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-200 group"
              >
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-3 h-3 text-yellow-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="flex-1 min-w-0">
                    <p className="truncate font-medium">{chat.title}</p>
                    <p className="text-xs text-gray-500">{chat.time}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="pt-6 border-t border-gray-200">
          <nav className="space-y-2">
            {bottomItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href

              return (
                <Link
                  key={item.key}
                  href={item.href}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive ? "bg-yellow-50 text-yellow-600" : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? "text-yellow-600" : "text-gray-500"}`} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </aside>
  )
}
