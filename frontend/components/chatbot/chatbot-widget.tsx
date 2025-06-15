"use client";

import React, { useState } from 'react';
import { MessageCircle, X, Maximize2, Minimize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChatInterface } from './chat-interface';

interface ChatbotWidgetProps {
  position?: 'bottom-right' | 'bottom-left';
  className?: string;
}

export function ChatbotWidget({ position = 'bottom-right', className }: ChatbotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);

  const positionClass = position === 'bottom-right' 
    ? 'bottom-4 right-4' 
    : 'bottom-4 left-4';

  const widgetSize = isMaximized 
    ? 'w-full h-full top-0 left-0 right-0 bottom-0' 
    : 'w-80 h-96';

  return (
    <div className={`fixed z-50 ${positionClass} ${className}`}>
      {/* Chat Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full w-14 h-14 bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <MessageCircle className="w-6 h-6" />
        </Button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <Card 
          className={`${widgetSize} ${isMaximized ? 'rounded-none' : 'rounded-lg'} shadow-2xl flex flex-col`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-3 border-b bg-blue-600 text-white rounded-t-lg">
            <div className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              <span className="font-medium">Health Assistant</span>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMaximized(!isMaximized)}
                className="text-white hover:bg-blue-700 h-8 w-8 p-0"
              >
                {isMaximized ? (
                  <Minimize2 className="w-4 h-4" />
                ) : (
                  <Maximize2 className="w-4 h-4" />
                )}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setIsOpen(false);
                  setIsMaximized(false);
                }}
                className="text-white hover:bg-blue-700 h-8 w-8 p-0"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="flex-1 overflow-hidden">
            <ChatInterface className="h-full" />
          </div>
        </Card>
      )}
    </div>
  );
}

export default ChatbotWidget;
