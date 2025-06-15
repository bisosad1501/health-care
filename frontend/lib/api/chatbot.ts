// API configuration and utilities for chatbot service
const CHATBOT_API_BASE = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8007';

export interface ChatMessage {
  message: string;
  conversation_id?: string | null;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  type?: 'text' | 'suggestion' | 'knowledge';
  metadata?: {
    disease?: string;
    symptoms?: string[];
    confidence?: number;
    sources?: string[];
    knowledge_used?: boolean;
  };
  suggestions?: string[];
}

export interface KnowledgeQuery {
  query: string;
  limit?: number;
  type?: 'disease' | 'symptom' | 'knowledge' | 'all';
}

export interface KnowledgeResponse {
  results: {
    diseases: any[];
    symptoms: any[];
    knowledge: any[];
    medical_terms: any[];
  };
  total_count: number;
  query_time: number;
}

class ChatbotAPI {
  private baseURL: string;

  constructor(baseURL: string = CHATBOT_API_BASE) {
    this.baseURL = baseURL;
  }

  async sendMessage(data: ChatMessage): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/api/ai/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async searchKnowledge(data: KnowledgeQuery): Promise<KnowledgeResponse> {
    const params = new URLSearchParams({
      query: data.query,
      ...(data.limit && { limit: data.limit.toString() }),
      ...(data.type && { type: data.type }),
    });

    const response = await fetch(`${this.baseURL}/api/knowledge/search/?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getConversationHistory(conversationId: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/conversations/${conversationId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async createConversation(userId?: string): Promise<{ conversation_id: string }> {
    const response = await fetch(`${this.baseURL}/api/conversations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        title: 'Health Consultation',
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Health check endpoint
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await fetch(`${this.baseURL}/api/health/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      return {
        status: 'error',
        timestamp: new Date().toISOString(),
      };
    }
  }
}

// Export singleton instance
export const chatbotAPI = new ChatbotAPI();

// Export utility functions
export const formatHealthResponse = (response: string): string => {
  // Format markdown-like response for better display
  return response
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/•/g, '•')
    .replace(/\n/g, '<br>');
};

export const getHealthSuggestions = (): string[] => [
  "Tôi có triệu chứng đau đầu và sốt",
  "Làm sao để phòng ngừa cảm cúm?",
  "Tác dụng phụ của thuốc paracetamol",
  "Chế độ ăn cho người tiểu đường",
  "Cách đo huyết áp tại nhà",
  "Triệu chứng của COVID-19",
  "Lịch tiêm vaccine cho trẻ em",
  "Cách chăm sóc da mặt hàng ngày",
  "Bài tập cho người đau lưng",
  "Dấu hiệu cảnh báo đột quỵ"
];

export const validateHealthQuery = (query: string): { isValid: boolean; message?: string } => {
  if (!query || query.trim().length < 3) {
    return {
      isValid: false,
      message: 'Vui lòng nhập câu hỏi ít nhất 3 ký tự'
    };
  }

  if (query.length > 500) {
    return {
      isValid: false,
      message: 'Câu hỏi quá dài, vui lòng nhập dưới 500 ký tự'
    };
  }

  return { isValid: true };
};

// Emergency keywords detection
export const detectEmergencyKeywords = (message: string): boolean => {
  const emergencyKeywords = [
    'cấp cứu', 'khẩn cấp', 'nguy hiểm', 'nguy kịch',
    'khó thở', 'ngất xỉu', 'đau ngực', 'tai nạn',
    'chảy máu', 'co giật', 'bất tỉnh', 'sốc',
    'đột quỵ', 'nhồi máu', 'dị ứng nặng'
  ];

  const lowerMessage = message.toLowerCase();
  return emergencyKeywords.some(keyword => lowerMessage.includes(keyword));
};

export default chatbotAPI;
