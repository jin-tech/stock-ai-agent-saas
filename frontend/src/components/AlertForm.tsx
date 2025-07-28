'use client'

import { useState } from 'react'
import axios from 'axios'

interface AlertData {
  stockName: string
  keywords: string
}

interface AlertFormProps {
  onSuccess?: (data: AlertData) => void
  onError?: (error: string) => void
}

export default function AlertForm({ onSuccess, onError }: AlertFormProps) {
  const [formData, setFormData] = useState<AlertData>({
    stockName: '',
    keywords: ''
  })
  const [errors, setErrors] = useState<Partial<AlertData>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const validateForm = (): boolean => {
    const newErrors: Partial<AlertData> = {}

    if (!formData.stockName.trim()) {
      newErrors.stockName = 'Stock name is required'
    }

    if (!formData.keywords.trim()) {
      newErrors.keywords = 'Keywords are required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (errors[name as keyof AlertData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setSubmitMessage(null)

    try {
      // API endpoint for creating alerts - update this URL based on your backend
      await axios.post('/api/alerts', formData, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      setSubmitMessage({ type: 'success', text: 'Alert created successfully!' })
      setFormData({ stockName: '', keywords: '' })
      onSuccess?.(formData)
    } catch (error) {
      const errorMessage = axios.isAxiosError(error) 
        ? error.response?.data?.message || 'Failed to create alert'
        : 'An unexpected error occurred'
      
      setSubmitMessage({ type: 'error', text: errorMessage })
      onError?.(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Create Stock Alert</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="stockName" className="block text-sm font-medium text-gray-700 mb-1">
            Stock Name *
          </label>
          <input
            type="text"
            id="stockName"
            name="stockName"
            value={formData.stockName}
            onChange={handleInputChange}
            placeholder="e.g., AAPL, MSFT, TSLA"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.stockName ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.stockName && (
            <p className="text-red-500 text-sm mt-1">{errors.stockName}</p>
          )}
        </div>

        <div>
          <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-1">
            Keywords *
          </label>
          <textarea
            id="keywords"
            name="keywords"
            value={formData.keywords}
            onChange={handleInputChange}
            placeholder="e.g., earnings, revenue, profit, merger"
            rows={3}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.keywords ? 'border-red-500' : 'border-gray-300'
            }`}
          />
          {errors.keywords && (
            <p className="text-red-500 text-sm mt-1">{errors.keywords}</p>
          )}
          <p className="text-gray-500 text-sm mt-1">
            Separate multiple keywords with commas
          </p>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
            isSubmitting
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
          } text-white`}
        >
          {isSubmitting ? 'Creating Alert...' : 'Create Alert'}
        </button>
      </form>

      {submitMessage && (
        <div className={`mt-4 p-3 rounded-md ${
          submitMessage.type === 'success' 
            ? 'bg-green-100 text-green-700' 
            : 'bg-red-100 text-red-700'
        }`}>
          {submitMessage.text}
        </div>
      )}
    </div>
  )
}