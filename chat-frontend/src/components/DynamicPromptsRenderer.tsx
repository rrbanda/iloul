
import { useChat } from '../context/ChatContext'

interface DynamicPrompt {
  text: string
  icon: string
  category: string
}

interface DynamicPromptsData {
  type: string
  phase: string
  prompts: DynamicPrompt[]
  completion_status: string
}

interface DynamicPromptsRendererProps {
  content: string
}

export default function DynamicPromptsRenderer({ content }: DynamicPromptsRendererProps) {
  const { sendMortgageMessage, state } = useChat()

  // Parse the DYNAMIC_PROMPTS content
  const parsePrompts = (content: string): DynamicPromptsData | null => {
    try {
      const jsonStr = content.replace('DYNAMIC_PROMPTS: ', '')
      return JSON.parse(jsonStr)
    } catch (error) {
      console.error('Error parsing dynamic prompts:', error)
      return null
    }
  }

  const promptsData = parsePrompts(content)

  if (!promptsData) {
    return <p className="text-gray-800">{content}</p>
  }

  const handlePromptClick = async (prompt: DynamicPrompt) => {
    if (state.mortgageApplication.isActive) {
      await sendMortgageMessage(prompt.text)
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'personal': return 'bg-blue-50 border-blue-200 text-blue-800'
      case 'employment': return 'bg-green-50 border-green-200 text-green-800'
      case 'property': return 'bg-purple-50 border-purple-200 text-purple-800'
      case 'financial': return 'bg-orange-50 border-orange-200 text-orange-800'
      case 'action': return 'bg-red-50 border-red-200 text-red-800'
      case 'help': return 'bg-gray-50 border-gray-200 text-gray-800'
      default: return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm font-medium text-gray-600">Choose what you'd like to share:</span>
        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
          {promptsData.completion_status}
        </span>
      </div>
      
      <div className="grid grid-cols-1 gap-2 max-w-lg">
        {promptsData.prompts.map((prompt, index) => (
          <button
            key={index}
            onClick={() => handlePromptClick(prompt)}
            className={`
              flex items-center gap-3 p-3 rounded-lg border-2 transition-all duration-200
              hover:shadow-md hover:scale-[1.02] active:scale-[0.98]
              ${getCategoryColor(prompt.category)}
            `}
          >
            <span className="text-lg">{prompt.icon}</span>
            <span className="text-sm font-medium flex-1 text-left">
              {prompt.text}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
