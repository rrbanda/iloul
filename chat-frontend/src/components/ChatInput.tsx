import React, { useState, useRef, KeyboardEvent } from 'react'
import { Send, Paperclip, X, FileText, Image } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { useChat } from '../context/ChatContext'
import toast from 'react-hot-toast'

interface ChatInputProps {
  disabled?: boolean
}

function ChatInput({ disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [attachedFiles, setAttachedFiles] = useState<File[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const { sendMessage, uploadFiles } = useChat()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() && attachedFiles.length === 0) return
    if (disabled) return

    try {
      if (attachedFiles.length > 0) {
        await uploadFiles(message || 'Please analyze these documents:', attachedFiles)
      } else {
        await sendMessage(message)
      }

      // Clear input
      setMessage('')
      setAttachedFiles([])
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  // Auto-resize textarea
  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    
    // Auto-resize
    const textarea = e.target
    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
  }

  // File upload handling
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const newFiles = [...attachedFiles, ...acceptedFiles]
      if (newFiles.length > 5) {
        toast.error('Maximum 5 files allowed')
        return
      }
      setAttachedFiles(newFiles)
      setIsDragOver(false)
    },
    onDragEnter: () => setIsDragOver(true),
    onDragLeave: () => setIsDragOver(false),
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    noClick: true
  })

  const removeFile = (index: number) => {
    setAttachedFiles(files => files.filter((_, i) => i !== index))
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-4 h-4" />
    }
    return <FileText className="w-4 h-4" />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-3">
      {/* File Attachments */}
      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {attachedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg text-sm"
            >
              {getFileIcon(file)}
              <span className="text-blue-800 font-medium">{file.name}</span>
              <span className="text-blue-600">({formatFileSize(file.size)})</span>
              <button
                onClick={() => removeFile(index)}
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg transition-all duration-200 ${
          isDragActive || isDragOver
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-200'
        }`}
      >
        <input {...getInputProps()} />
        
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end gap-3 p-4">
            {/* File Upload Button */}
            <button
              type="button"
              onClick={() => (document.querySelector('input[type="file"]') as HTMLInputElement)?.click()}
              disabled={disabled}
              className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              title="Attach files"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            {/* Text Input */}
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleTextareaChange}
              onKeyPress={handleKeyPress}
              placeholder={
                attachedFiles.length > 0
                  ? 'Add a message about your documents (optional)...'
                  : 'Ask me about mortgage requirements, upload documents, or start a new application...'
              }
              disabled={disabled}
              className="flex-1 resize-none border-0 bg-transparent focus:ring-0 focus:outline-none placeholder-gray-500 min-h-[24px] max-h-[120px] disabled:opacity-50"
              rows={1}
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={disabled || (!message.trim() && attachedFiles.length === 0)}
              className="flex-shrink-0 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Send message"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>

        {/* Drag & Drop Overlay */}
        {(isDragActive || isDragOver) && (
          <div className="absolute inset-0 bg-blue-50 bg-opacity-90 border-2 border-blue-400 border-dashed rounded-lg flex items-center justify-center">
            <div className="text-center">
              <FileText className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-blue-800 font-medium">Drop files here to upload</p>
              <p className="text-blue-600 text-sm">PDF, images, and text files supported</p>
            </div>
          </div>
        )}
      </div>

      {/* Helper Text */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {attachedFiles.length > 0 && (
            <span className="text-blue-600">
              {attachedFiles.length} file(s) attached
            </span>
          )}
        </div>
        <span>Max 5 files, 10MB each</span>
      </div>
    </div>
  )
}

export default ChatInput
