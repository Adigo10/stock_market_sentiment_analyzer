# AI Stock Market Sentiment Analyzer - Frontend

Modern TypeScript + React frontend for the AI Stock Market Sentiment Analyzer.

## Features

- 🎨 Clean, modern UI with Tailwind CSS
- 🌓 Dark/Light theme toggle with persistence
- ⚡ Smooth animations with Framer Motion
- 📊 Real-time analysis progress tracking
- 📱 Fully responsive design
- 🔍 Comprehensive sentiment analysis visualization
- 📥 Export analysis results to JSON

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animation library
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Prerequisites

- Node.js 16+ and Yarn
- Backend server running on `http://localhost:8000`

## Installation

```bash
# Install dependencies
yarn install

# Start development server
yarn dev

# Build for production
yarn build

# Preview production build
yarn preview
```

## Development

The development server runs on `http://localhost:3000` with hot module replacement enabled.

API requests are proxied to `http://localhost:8000` automatically.

## Project Structure

```
src/
├── components/       # React components
│   ├── ArticleCard.tsx
│   ├── Badge.tsx
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Dashboard.tsx
│   ├── DataTable.tsx
│   ├── LoadingSpinner.tsx
│   ├── MetricCard.tsx
│   ├── StepCard.tsx
│   └── ThemeToggle.tsx
├── contexts/        # React contexts
│   └── ThemeContext.tsx
├── services/        # API services
│   └── api.ts
├── types/          # TypeScript types
│   └── index.ts
├── utils/          # Helper functions
│   └── helpers.ts
├── App.tsx         # Main app component
├── main.tsx        # Entry point
└── index.css       # Global styles
```

## Usage

1. Ensure the backend server is running
2. Start the frontend development server
3. Open `http://localhost:3000` in your browser
4. Select a company from the dropdown
5. Click "Analyze with AI" to start the analysis
6. View the results in three steps:
   - Step 1: Fetch & Rank articles
   - Step 2: AI Sentiment Analysis
   - Step 3: Keyphrase Intelligence
7. Download results as JSON if needed

## Theme

The app supports both light and dark themes. The theme preference is saved to localStorage and persists across sessions. The app also respects the system theme preference on first load.

## Building for Production

```bash
yarn build
```

The production-ready files will be in the `dist/` directory.

## License

Same as parent project.

