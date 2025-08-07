import { Suspense } from "react"
import Header from "@/components/header"
import Sidebar from "@/components/sidebar"
import ChatInterface from "@/components/chat-interface"
import LoadingSkeleton from "@/components/loading-skeleton"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1">
          <Suspense fallback={<LoadingSkeleton />}>
            <ChatInterface />
          </Suspense>
        </main>
      </div>
    </div>
  )
}
