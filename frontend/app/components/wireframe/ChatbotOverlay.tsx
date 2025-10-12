import React, { useState } from 'react';
import { WireframeBox } from './WireframeBox';
import { WireframeButton } from './WireframeButton';
import { WireframeIcon } from './WireframeIcon';
import { Annotation } from './Annotation';

export function ChatbotOverlay() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'bot'; text: string }>>([]);

  return (
    <>
      {/* Chatbot Toggle Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-16 h-16 rounded-full border-4 border-gray-900 bg-gray-900 text-white flex items-center justify-center hover:scale-110 transition-transform shadow-lg"
          >
            <span className="text-xl">{isOpen ? '×' : '💬'}</span>
          </button>
          {!isOpen && (
            <Annotation type="action" text="Click to open chatbot" position="left" />
          )}
        </div>
      </div>

      {/* Chatbot Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] border-4 border-gray-900 bg-white shadow-2xl z-50 flex flex-col">
          {/* Header */}
          <div className="border-b-2 border-gray-400 p-4 flex items-center justify-between bg-gray-100 relative">
            <div className="flex items-center gap-3">
              <WireframeIcon size="md" label="BOT" />
              <div>
                <div className="h-4 w-32 border border-gray-600 mb-1"></div>
                <div className="h-3 w-20 border border-gray-400"></div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-xl">×</button>
            <Annotation type="state" text="Online status indicator" position="top" />
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 relative">
            <Annotation type="flow" text="Chat message thread" position="right" />
            
            {/* Welcome Message */}
            <div className="flex gap-2">
              <WireframeIcon size="sm" label="B" />
              <div className="flex-1">
                <WireframeBox label="WELCOME MESSAGE" height="h-16" variant="filled" />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-2 relative">
              <Annotation type="interaction" text="Quick action buttons" position="right" />
              {['Service 1', 'Service 2', 'FAQ', 'Support'].map((action) => (
                <WireframeButton 
                  key={action} 
                  label={action} 
                  variant="secondary" 
                  size="sm"
                  onClick={() => setMessages([...messages, { type: 'user', text: action }])}
                />
              ))}
            </div>

            {/* Sample Messages */}
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-2 ${msg.type === 'user' ? 'justify-end' : ''}`}>
                {msg.type === 'bot' && <WireframeIcon size="sm" label="B" />}
                <div className={`max-w-[70%]`}>
                  <WireframeBox 
                    label={msg.text} 
                    height="h-12" 
                    variant={msg.type === 'user' ? 'filled' : 'outline'} 
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="border-t-2 border-gray-400 p-4 relative">
            <Annotation type="action" text="Type message & send" position="top" />
            <div className="flex gap-2">
              <WireframeBox label="TYPE MESSAGE..." height="h-12" variant="outline" className="flex-1" />
              <WireframeButton label="SEND" variant="primary" />
            </div>
            <div className="flex gap-2 mt-2 justify-center">
              <WireframeIcon size="sm" label="📎" />
              <WireframeIcon size="sm" label="🎤" />
              <WireframeIcon size="sm" label="😊" />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
