'use client'

import { useState, useRef, useEffect } from 'react'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showEmbedding, setShowEmbedding] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSearch = async (e) => {
    e.preventDefault()

    if (!input.trim()) return

    const userMessage = {
      role: 'user',
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const botMessage = {
        role: 'bot',
        content: data.results,
        queryEmbedding: data.query_embedding,
        userQuery: input,
      }

      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        role: 'bot',
        content: [
          {
            score: 0,
            text: `Erro ao conectar ao servidor: ${error.message}`,
          },
        ],
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const formatEmbedding = (embedding) => {
    if (!embedding) return ''
    const preview = embedding.slice(0, 10)
    return `[${preview.map(n => n.toFixed(4)).join(', ')}... (${embedding.length} números)]`
  }

  return (
    <div className="w-full max-w-2xl h-screen flex flex-col bg-white rounded-lg shadow-lg">
      <div className="border-b border-gray-200 p-4 bg-gradient-to-r from-gray-50 to-gray-100">
        <h1 className="text-2xl font-bold text-gray-800">IA de Similaridade em Esportes de Areia</h1>
        <p className="text-sm text-gray-600 mt-1">Encontre respostas inteligentes sobre futevôlei, vôlei de praia e esportes relacionados usando busca semântica baseada em IA — resultados relevantes direto de múltiplas fontes.</p>
        <button
          onClick={() => setShowEmbedding(!showEmbedding)}
          className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
        >
          {showEmbedding ? 'Ocultar' : 'Mostrar'} embeddings da busca
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <div className="text-6xl mb-4">💬</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Olá! Como posso ajudar?
              </h2>
              <p className="text-gray-600">
                Digite uma mensagem para começar a buscar por similaridade
              </p>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className="space-y-2">
            <div
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'user' ? (
                <div className="bg-blue-500 text-white rounded-lg px-4 py-3 max-w-xs lg:max-w-md break-words">
                  {message.content}
                </div>
              ) : (
                <div className="w-full max-w-md">
                  <div className="text-sm font-semibold text-gray-700 mb-2">
                    Encontrei isso pra você:
                  </div>
                  <div className="space-y-2">
                    {Array.isArray(message.content) && message.content.length > 0 ? (
                      message.content.map((item, itemIndex) => (
                        <div
                          key={itemIndex}
                          className="bg-gray-100 border border-gray-300 rounded-lg p-3 hover:shadow-md transition-shadow"
                        >
                          <div className="text-xs font-semibold text-blue-600 mb-1">
                            Relevância: {Math.round(item.score * 100)}%
                          </div>
                          <div className="text-sm text-gray-800 leading-relaxed">
                            {item.text}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="bg-gray-100 border border-gray-300 rounded-lg p-3">
                        <div className="text-sm text-gray-600">
                          Nenhum resultado encontrado
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            {showEmbedding && message.queryEmbedding && (
              <div className="flex justify-start">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 max-w-full">
                  <div className="text-xs font-mono text-gray-500 break-all">
                    <div className="font-semibold text-gray-700 mb-1">Embedding da busca: "{message.userQuery}"</div>
                    <div className="text-[10px]">{formatEmbedding(message.queryEmbedding)}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua busca..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
      </div>
    </div>
  )
}