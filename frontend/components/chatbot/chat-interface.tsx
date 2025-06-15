"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Heart, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { chatbotAPI, validateHealthQuery, detectEmergencyKeywords, getHealthSuggestions } from '@/lib/api/chatbot';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'suggestion' | 'knowledge';
  metadata?: {
    disease?: string;
    symptoms?: string[];
    confidence?: number;
    sources?: string[];
  };
}

interface ChatInterfaceProps {
  className?: string;
}

const healthSuggestions = getHealthSuggestions().slice(0, 5);

export function ChatInterface({ className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Xin chào! Tôi là AI Health Assistant. Tôi có thể giúp bạn tư vấn y tế, tra cứu thông tin bệnh lý, và hướng dẫn chăm sóc sức khỏe. Bạn cần hỗ trợ gì?',
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API status on mount
  useEffect(() => {
    checkAPIStatus();
  }, []);

  const checkAPIStatus = async () => {
    try {
      await chatbotAPI.healthCheck();
      setApiStatus('online');
    } catch (error) {
      setApiStatus('offline');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Validate input
    const validation = validateHealthQuery(content);
    if (!validation.isValid) {
      // Show validation error as bot message
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: validation.message || 'Câu hỏi không hợp lệ',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    // Check for emergency keywords
    if (detectEmergencyKeywords(content)) {
      const userMessage: Message = {
        id: Date.now().toString(),
        content: content.trim(),
        sender: 'user',
        timestamp: new Date(),
        type: 'text'
      };

      const emergencyMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `🚨 **CẢNH BÁO KHẨN CẤP** 🚨

Tôi phát hiện câu hỏi của bạn có thể liên quan đến tình huống khẩn cấp. 

**HÀNH ĐỘNG NGAY:**
• **Gọi 115** (Cấp cứu) hoặc đến bệnh viện gần nhất
• **Gọi 114** (Thông tin y tế) để được hướng dẫn
• **Liên hệ bác sĩ** nếu có thể

**Thông tin tham khảo:**
${simulateHealthResponse(content)}

⚠️ **LỜI KHUYÊN:** Trong tình huống khẩn cấp, đừng chờ đợi. Hãy tìm kiếm sự giúp đỡ y tế ngay lập tức!`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };

      setMessages(prev => [...prev, userMessage, emergencyMessage]);
      setInputValue('');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: content.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Create conversation if not exists
      if (!conversationId) {
        const newConversation = await chatbotAPI.createConversation();
        setConversationId(newConversation.conversation_id);
      }

      // Call chatbot API
      const response = await chatbotAPI.sendMessage({
        message: content,
        conversation_id: conversationId,
      });
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau.',
        sender: 'bot',
        timestamp: new Date(),
        type: response.type || 'text',
        metadata: response.metadata
      };

      setMessages(prev => [...prev, botMessage]);
      setApiStatus('online');
    } catch (error) {
      console.error('Error sending message:', error);
      setApiStatus('offline');
      
      // Fallback response with knowledge base simulation
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `⚠️ **Kết nối API gặp sự cố** - Đang sử dụng chế độ ngoại tuyến

${simulateHealthResponse(content)}

💡 **Lưu ý:** Đây là phản hồi mô phỏng. Hãy thử lại sau khi kết nối ổn định để có câu trả lời chính xác hơn.`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'knowledge'
      };

      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const simulateHealthResponse = (userMessage: string): string => {
    const message = userMessage.toLowerCase();
    
    if (message.includes('đau đầu') || message.includes('sốt')) {
      return `Dựa trên triệu chứng bạn mô tả (đau đầu và sốt), đây có thể là dấu hiệu của:

**Các nguyên nhân có thể:**
• Cảm cúm hoặc nhiễm trùng virus
• Nhiễm trùng đường hô hấp
• Căng thẳng, mệt mỏi
• Thiếu nước

**Khuyến nghị:**
• Nghỉ ngơi đầy đủ
• Uống nhiều nước
• Có thể dùng paracetamol giảm đau
• Nếu sốt >39°C hoặc kéo dài >3 ngày, hãy đến khám bác sĩ

⚠️ **Lưu ý:** Đây chỉ là thông tin tham khảo, không thay thế việc khám bác sĩ.`;
    }
    
    if (message.includes('cảm cúm') || message.includes('phòng ngừa')) {
      return `**Cách phòng ngừa cảm cúm hiệu quả:**

🛡️ **Phòng ngừa cơ bản:**
• Rửa tay thường xuyên với xà phòng
• Đeo khẩu trang nơi đông người
• Tránh tiếp xúc gần với người bệnh
• Không chạm tay vào mặt

💉 **Tiêm vaccine:**
• Tiêm vaccine cúm hàng năm
• Đặc biệt quan trọng với người cao tuổi, trẻ em

🏋️ **Tăng cường sức đề kháng:**
• Ăn đủ chất dinh dưỡng
• Tập thể dục đều đặn
• Ngủ đủ giấc (7-8 tiếng/đêm)
• Giảm stress`;
    }
    
    if (message.includes('paracetamol') || message.includes('thuốc')) {
      return `**Thông tin về Paracetamol:**

💊 **Công dụng:**
• Giảm đau, hạ sốt
• An toàn cho hầu hết mọi người

⚠️ **Tác dụng phụ:**
• Hiếm gặp khi dùng đúng liều
• Tổn thương gan nếu quá liều
• Dị ứng (hiếm)

📋 **Liều dùng:**
• Người lớn: 500-1000mg/lần, tối đa 4g/ngày
• Trẻ em: theo cân nặng (10-15mg/kg/lần)

❌ **Chống chỉ định:**
• Suy gan nặng
• Dị ứng với paracetamol
• Uống nhiều rượu bia`;
    }
    
    return `Cảm ơn bạn đã đặt câu hỏi. Tôi đang học hỏi thêm để có thể hỗ trợ bạn tốt hơn về vấn đề này. 

Trong thời gian chờ đợi, bạn có thể:
• Tham khảo thông tin từ các nguồn y tế uy tín
• Liên hệ với bác sĩ nếu cần tư vấn cụ thể
• Thử đặt câu hỏi khác mà tôi có thể hỗ trợ

Tôi có thể giúp bạn về: triệu chứng bệnh, phòng ngừa, thông tin thuốc, chế độ dinh dưỡng, và nhiều chủ đề sức khỏe khác.`;
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Chat Header */}
      <Card className="rounded-none border-x-0 border-t-0">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <div className="p-2 bg-blue-100 rounded-full">
              <Heart className="w-5 h-5 text-blue-600" />
            </div>
            AI Health Assistant
            <Badge 
              variant="secondary" 
              className={`ml-auto ${apiStatus === 'online' ? 'bg-green-100 text-green-800' : apiStatus === 'offline' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}
            >
              {apiStatus === 'online' ? 'Online' : apiStatus === 'offline' ? 'Offline' : 'Checking...'}
            </Badge>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.sender === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <Avatar className="w-8 h-8">
                  <AvatarFallback className={
                    message.sender === 'user' 
                      ? 'bg-blue-100 text-blue-600' 
                      : 'bg-green-100 text-green-600'
                  }>
                    {message.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </AvatarFallback>
                </Avatar>
                
                <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'} flex-1 max-w-[80%]`}>
                  <div
                    className={`p-3 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm">
                      {message.content}
                    </div>
                    {message.metadata && (
                      <div className="mt-2 pt-2 border-t border-gray-200 text-xs">
                        {message.metadata.confidence && (
                          <div>Độ tin cậy: {Math.round(message.metadata.confidence * 100)}%</div>
                        )}
                        {message.metadata.sources && (
                          <div>Nguồn: {message.metadata.sources.join(', ')}</div>
                        )}
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 mt-1">
                    {formatTimestamp(message.timestamp)}
                  </span>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-start gap-3">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-green-100 text-green-600">
                    <Bot className="w-4 h-4" />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-gray-100 p-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm text-gray-600">Đang suy nghĩ...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </ScrollArea>
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="p-4 border-t bg-gray-50">
          <div className="mb-2 text-sm font-medium text-gray-700">
            Câu hỏi gợi ý:
          </div>
          <div className="flex flex-wrap gap-2">
            {healthSuggestions.map((suggestion, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-xs hover:bg-blue-50 hover:border-blue-200"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <Card className="rounded-none border-x-0 border-b-0">
        <CardContent className="p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Nhập câu hỏi về sức khỏe..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              type="submit" 
              disabled={isLoading || !inputValue.trim()}
              size="icon"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </form>
          <div className="mt-2 text-xs text-gray-500">
            💡 Tip: Mô tả triệu chứng cụ thể để được tư vấn chính xác hơn
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
