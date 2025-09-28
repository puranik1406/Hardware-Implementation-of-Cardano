# Arduino Masumi Network Simulator - Copilot Instructions

## Project Overview
This is a React application that simulates Arduino boards with Masumi Network integration for agentic payments using Sokosumi agents on the Cardano blockchain.

## Key Technologies
- React 18 + Vite
- Tailwind CSS
- CodeMirror 6 (C++ syntax highlighting)
- Lucide React (icons)
- Masumi Network API simulation
- Sokosumi agent framework

## Project Structure
```
src/
├── components/
│   ├── ArduinoBoard.jsx      # Arduino Uno simulation with pins and code editor
│   ├── CodeEditor.jsx        # CodeMirror-based C++ editor
│   ├── MasumiPaymentPanel.jsx # Payment interface and transaction history
│   └── AgentStatusPanel.jsx   # Network monitoring and agent status
├── App.jsx                   # Main application component
├── index.css                 # Tailwind CSS and custom styles
└── main.jsx                  # React entry point
```

## Development Guidelines

### Arduino Simulation
- Use realistic Arduino C++ code with proper libraries (WiFi.h, HTTPClient.h, ArduinoJson.h)
- Implement proper pin visualization for digital (0-13) and analog (A0-A5) pins
- Simulate serial monitor output with timestamps
- Include realistic networking and Masumi API integration code

### Masumi Network Features
- Implement agent registration and payment sending functionality
- Use proper Cardano wallet address formats (addr1q...)
- Simulate WebSocket connections to Sokosumi platform
- Include real-time network statistics (latency, throughput, block height)

### UI/UX Guidelines
- Use Arduino green (#00979D), Masumi purple (#6366f1), and Sokosumi purple (#8b5cf6) color scheme
- Implement smooth animations for status changes and payments
- Ensure responsive design for desktop and mobile
- Use proper loading states and error handling

### Code Standards
- Use functional components with React Hooks
- Implement proper prop validation and default values
- Follow React best practices for state management
- Use Tailwind CSS utility classes for styling
- Maintain consistent component structure and naming

## Testing Scenarios
- Arduino code compilation and execution simulation
- Payment transactions between agents
- Real-time network monitoring
- Pin state changes and serial output
- Responsive design on different screen sizes

## API Integration Points
- Masumi Network agent registration
- Payment sending and receiving
- Balance checking and transaction history
- Sokosumi WebSocket connections
- Real-time network statistics

When working on this project, focus on creating realistic Arduino simulations while maintaining the Masumi Network integration for seamless agentic payments.