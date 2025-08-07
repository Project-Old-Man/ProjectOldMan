"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Search, Bell, User, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function Header() {
  const pathname = usePathname()

  const navItems = [
    { href: "/", label: "채팅", key: "chat" },
    { href: "/models", label: "AI 모델", key: "models" },
    { href: "/playground", label: "실험실", key: "playground" },
    { href: "/history", label: "대화 기록", key: "history" },
  ]

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl text-gray-900">AI놀이터</span>
            </Link>

            <nav className="hidden md:flex items-center space-x-6">
              {navItems.map((item) => (
                <Link
                  key={item.key}
                  href={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    pathname === item.href
                      ? "text-yellow-600 bg-yellow-50"
                      : "text-gray-700 hover:text-yellow-600 hover:bg-gray-50"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                type="text"
                placeholder="대화 내용 검색..."
                className="pl-10 pr-4 py-2 w-64 bg-gray-50 border-0 focus:bg-white focus:ring-2 focus:ring-yellow-500"
              />
            </div>

            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-500 rounded-full"></span>
            </Button>

            <Button variant="ghost" size="icon">
              <User className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
