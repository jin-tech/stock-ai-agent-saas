'use client'

import AlertForm from '@/components/AlertForm'

export default function Home() {
  const handleAlertSuccess = (data: { stockName: string; keywords: string }) => {
    console.log('Alert created successfully:', data)
  }

  const handleAlertError = (error: string) => {
    console.error('Alert creation failed:', error)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Stock AI Agent
          </h1>
          <p className="text-gray-600">
            Create intelligent alerts for your stock portfolio
          </p>
        </header>

        <main className="flex justify-center">
          <AlertForm 
            onSuccess={handleAlertSuccess}
            onError={handleAlertError}
          />
        </main>
      </div>
    </div>
  )
}
