import './globals.css'

export const metadata = {
  title: 'Stock AI Agent - PE Ratio Dashboard',
  description: 'AI-powered stock analysis with PE ratio tracking',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  Stock AI Agent
                </h1>
                <nav className="space-x-4">
                  <a href="/" className="text-primary-600 hover:text-primary-700">
                    Dashboard
                  </a>
                  <a href="/pe-ratios" className="text-gray-600 hover:text-gray-700">
                    PE Ratios
                  </a>
                </nav>
              </div>
            </div>
          </header>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}