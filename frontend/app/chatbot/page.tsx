"use client";

import React from 'react';
import { ChatInterface } from '@/components/chatbot/chat-interface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Heart, Shield, Clock, Users } from 'lucide-react';

const features = [
  {
    icon: <Heart className="w-5 h-5 text-red-500" />,
    title: "Tư vấn y tế AI",
    description: "Hỗ trợ 24/7 với kiến thức y khoa cập nhật"
  },
  {
    icon: <Shield className="w-5 h-5 text-green-500" />,
    title: "Thông tin đáng tin cậy",
    description: "Dữ liệu từ WHO, CDC và các tổ chức y tế uy tín"
  },
  {
    icon: <Clock className="w-5 h-5 text-blue-500" />,
    title: "Phản hồi nhanh chóng",
    description: "Trả lời tức thì các thắc mắc về sức khỏe"
  },
  {
    icon: <Users className="w-5 h-5 text-purple-500" />,
    title: "Hỗ trợ đa dạng",
    description: "Từ triệu chứng đến phòng ngừa bệnh tật"
  }
];

export default function ChatbotPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="container mx-auto px-4 py-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-2">
              <div className="p-2 bg-blue-100 rounded-full">
                <Heart className="w-6 h-6 text-blue-600" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI Health Assistant
              </h1>
              <Badge className="bg-green-100 text-green-800 border-green-200">
                Beta
              </Badge>
            </div>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Trợ lý AI chăm sóc sức khỏe với kiến thức y khoa từ các nguồn uy tín. 
              Hỗ trợ tư vấn, tra cứu thông tin và hướng dẫn chăm sóc sức khỏe 24/7.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Features Sidebar */}
            <div className="lg:col-span-1 space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Tính năng nổi bật</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {feature.icon}
                      </div>
                      <div>
                        <h4 className="font-medium text-sm">{feature.title}</h4>
                        <p className="text-xs text-gray-600 mt-1">
                          {feature.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Thống kê</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Bệnh lý</span>
                      <Badge variant="secondary">100+</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Triệu chứng</span>
                      <Badge variant="secondary">500+</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Thuốc</span>
                      <Badge variant="secondary">1000+</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Người dùng</span>
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        Mới
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Chat Interface */}
            <div className="lg:col-span-3">
              <Card className="h-[70vh] flex flex-col">
                <ChatInterface className="flex-1" />
              </Card>
            </div>
          </div>

          {/* Important Notice */}
          <div className="mt-6">
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="p-1 bg-amber-100 rounded-full flex-shrink-0 mt-1">
                    <Shield className="w-4 h-4 text-amber-600" />
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-amber-800 mb-1">
                      ⚠️ Lưu ý quan trọng
                    </p>
                    <p className="text-amber-700">
                      Thông tin từ AI Health Assistant chỉ mang tính chất tham khảo, không thay thế việc khám bác sĩ. 
                      Trong trường hợp cấp cứu hoặc triệu chứng nghiêm trọng, hãy liên hệ ngay với cơ sở y tế gần nhất.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
