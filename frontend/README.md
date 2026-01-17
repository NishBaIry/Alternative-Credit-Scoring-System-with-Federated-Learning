# CashFlow Frontend

Alternative Credit Scoring Platform - Frontend Application

## Tech Stack

- **React 19** - UI Framework
- **Vite** - Build tool and dev server
- **TailwindCSS 3** - Utility-first CSS framework
- **React Router v7** - Client-side routing
- **Axios** - HTTP client for API calls

## Project Structure

```
frontend/
├── src/
│   ├── assets/          # Images, icons, illustrations
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── context/        # React context providers
│   ├── lib/            # Utilities and configurations
│   └── styles/         # Global CSS and Tailwind config
├── public/             # Static assets
└── package.json
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your backend API URL (default: http://localhost:8000)

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Features

### Client UI
- **Bank Selection & Login** - Choose bank and authenticate
- **Credit Score Dashboard** - View alternative credit score (300-900)
- **Score Details** - Understand factors affecting the score
- **Profile Management** - Limited profile editing
- **Recommendations** - Tips to improve credit score

### Bank Staff UI
- **Staff Dashboard** - Overview of metrics and quick actions
- **Customer Management** - View and search customer data
- **Application Scoring** - Score new loan applications
- **Model Training** - Train local models and participate in FL
- **Analytics** - Feature importance, fairness metrics, trends

## Routing

### Client Routes
- `/` - Landing page
- `/auth` - Authentication choice
- `/client/bank-select` - Bank selection
- `/client/login` - Client login
- `/client/dashboard` - Client dashboard
- `/client/score-details` - Score details
- `/client/profile` - Profile page

### Staff Routes
- `/staff/login` - Staff login
- `/staff/dashboard` - Staff dashboard
- `/staff/customers` - Customer list
- `/staff/customers/:id` - Customer details
- `/staff/score-application` - Score applications
- `/staff/model-training` - Model training & FL
- `/staff/analytics` - Analytics dashboard

## Styling

TailwindCSS is configured with:
- Custom color palette (primary blue, secondary purple)
- Component classes (`.btn-primary`, `.card`, `.input-field`)
- Responsive design utilities

## Next Steps

1. Implement actual API integration with backend
2. Add authentication guards with ProtectedRoute
3. Add chart libraries for analytics
4. Implement form validation
5. Add unit/E2E tests
