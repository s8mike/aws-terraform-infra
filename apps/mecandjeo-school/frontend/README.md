## `apps/mecandjeo-school/frontend/README.md`

````markdown
# Mecandjeo School — Frontend

The frontend application for the Mecandjeo School Learning Management System (LMS).

The application provides the user interface for authentication, role-aware navigation,
dashboard experiences, responsive layouts, and interaction with the Mecandjeo School
backend API.

---

## Overview

The Mecandjeo School frontend is built with React and TypeScript using Vite.

The frontend is responsible for:

- User authentication interface
- Authenticated application layout
- Role-aware navigation
- Administrator dashboard
- Responsive desktop, tablet, and mobile layouts
- Loading, empty, and error states
- Form validation and user feedback
- Accessible keyboard navigation and focus states
- Communication with the FastAPI backend

The frontend does not own authentication or authorization decisions.
Those responsibilities remain enforced by the backend.

---

## Technology Stack

| Technology | Purpose |
| --- | --- |
| React | UI development |
| TypeScript | Type-safe application development |
| Vite | Development server and production build |
| React Router | Client-side routing |
| Axios | Backend API communication |
| React Hook Form | Form management |
| Zod | Form validation |
| Lucide React | UI icons |
| TanStack React Table | Table/data presentation |
| Tailwind CSS | Styling and responsive design |

---

## Application Structure

```text
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── DashboardCard.tsx
│   │   │   ├── DashboardHeader.tsx
│   │   │   └── DashboardSection.tsx
│   │   │
│   │   └── layout/
│   │       ├── AppLayout.tsx
│   │       ├── Header.tsx
│   │       ├── Navigation.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx
│   │
│   ├── pages/
│   │   ├── auth/
│   │   │   └── LoginPage.tsx
│   │   └── DashboardPage.tsx
│   │
│   ├── services/
│   │   ├── adminService.ts
│   │   ├── authService.ts
│   │   ├── api.ts
│   │   └── rootApi.ts
│   │
│   └── ...
│
├── .env
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
````

The structure may expand as additional LMS features are implemented.

---

## Authentication

Authentication is handled through the backend API.

The frontend:

```text
LoginPage
    ↓
authService
    ↓
FastAPI authentication endpoint
    ↓
Authentication response
    ↓
AuthContext
    ↓
Authenticated application
```

The frontend stores the authenticated user state through `AuthContext`.

Logout clears the authenticated session and returns the user to the login page.

Authentication state must not be treated as the final authorization boundary.
Backend authorization remains authoritative.

---

## Role-Based Navigation

The application currently supports role-aware navigation for:

* Administrator
* Teacher
* Student
* Parent

The navigation is rendered according to the authenticated user's role.

```text
Authenticated User
        │
        ▼
    AuthContext
        │
        ▼
     Navigation
        │
        ├── Admin
        ├── Teacher
        ├── Student
        └── Parent
```

The navigation component is shared between desktop and mobile layouts.

---

## Application Layout

Authenticated pages use the shared application shell:

```text
AppLayout
├── Header
├── Sidebar
│   └── Navigation
└── Main Content
```

### Desktop

The sidebar remains visible beside the application content.

### Tablet / Mobile

The sidebar changes to a navigation drawer controlled by the header menu button.

The same role-aware `Navigation` component is reused in both layouts.

---

## Dashboard

The dashboard provides a common authenticated entry point.

Administrator dashboard information currently includes live statistics retrieved
from the backend API, including:

* Students
* Teachers
* Courses
* Users

Reusable dashboard components provide consistent presentation:

```text
DashboardPage
├── DashboardHeader
├── DashboardCard
└── DashboardSection
```

Dashboard cards support loading feedback while API data is being retrieved.

---

## API Integration

Frontend API communication is separated into service modules.

Examples include:

```text
services/
├── api.ts
├── rootApi.ts
├── authService.ts
└── adminService.ts
```

The service layer keeps API communication separate from page and presentation logic.

Example flow:

```text
DashboardPage
      ↓
adminService
      ↓
rootApi / API client
      ↓
FastAPI backend
      ↓
Response
      ↓
DashboardPage
```

Backend and API configuration should remain environment-driven rather than being
hardcoded into application components.

---

## Responsive Design

The frontend is designed for:

* Desktop
* Tablet
* Mobile

Responsive behaviour includes:

* Adaptive header layout
* Desktop sidebar
* Mobile/tablet navigation drawer
* Responsive dashboard cards
* Responsive form containers
* Flexible content areas
* Mobile-friendly controls

Horizontal overflow was checked during the Phase 19 responsive verification.

The intended responsive behaviour is:

```text
Desktop
    ↓
Persistent sidebar

Tablet
    ↓
Navigation drawer

Mobile
    ↓
Navigation drawer
```

---

## Accessibility

Accessibility improvements were implemented during Phase 19.

Current accessibility considerations include:

* Semantic HTML elements
* Associated form labels
* `aria-invalid` for validation state
* `aria-describedby` for form errors
* Accessible password visibility control
* Accessible mobile navigation state
* `aria-expanded` for menu state
* `aria-controls` for navigation relationship
* `aria-hidden` for decorative icons
* `role="status"` for loading feedback
* `role="alert"` for dashboard errors
* Visible keyboard focus states
* Keyboard navigation through interactive controls

Keyboard navigation was verified using the `Tab` and `Enter` keys.

---

## Loading, Empty, and Error States

The frontend provides user-facing feedback for common application states.

### Loading

Dashboard cards provide a visual loading placeholder while data is being retrieved.

### Empty

Dashboard sections can display an appropriate message when no data is available.

### Error

Backend/API failures are presented using user-safe error messages rather than
exposing internal implementation details.

---

## Local Development

From the frontend directory:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The development application is normally available at:

```text
http://localhost:5173/
```

---

## Production Build

Create a production build with:

```bash
npm run build
```

The build performs TypeScript compilation followed by the Vite production build.

A successful build should complete without TypeScript or Vite errors.

---

## Verification

Useful local verification commands:

```bash
npm run build
```

Check the working tree for whitespace errors:

```bash
git diff --check
```

Responsive overflow can be checked from the browser console:

```javascript
document.documentElement.scrollWidth >
document.documentElement.clientWidth
```

Expected result:

```text
false
```

---

## Phase 19 — Frontend UI/UX Design & Implementation

Phase 19 established the frontend UI/UX foundation.

### Completed

```text
19.1  Design Goals & Design System
19.2  Application Shell & Global Layout
19.3  Header & User Account Experience
19.4  Sidebar & Role-Aware Navigation UI
19.5  Responsive/Mobile Navigation
19.6  Dashboard Content & Information Hierarchy
19.7  Dashboard Visual Polish
19.8  Loading, Empty States & User Feedback
19.9  Forms & Interactions
19.10 Accessibility
19.11 Final Responsive Verification
19.12 Phase Close-out
```

### Verification Status

```text
Production build       PASS
TypeScript compilation PASS
Responsive behaviour   VERIFIED
Mobile navigation      VERIFIED
Keyboard navigation    VERIFIED
Accessibility          VERIFIED
No regression          VERIFIED
```

Phase 19 establishes the UI/UX foundation for subsequent LMS feature development.

---

## Development Principles

The frontend follows these principles:

* Keep presentation separate from API communication.
* Reuse shared components where practical.
* Keep navigation role-aware.
* Keep backend authorization authoritative.
* Prefer accessible semantic HTML.
* Design for desktop, tablet, and mobile.
* Validate locally before committing changes.
* Avoid unnecessary changes to existing infrastructure.
* Keep environment-specific configuration outside application code.

````

### Why I recommend this replacement

The old README is essentially **scaffold documentation** generated by Vite. It talks about:

```text
React + TypeScript + Vite
Oxlint
React Compiler
Vite plugins
````

Those things are useful for the original template, but they don't explain what someone actually needs to know about **our Mecandjeo School frontend**.

The new README instead documents the frontend we actually built during Phase 19:

```text
React
  ↓
Application Layout
  ↓
Authentication
  ↓
Role-aware Navigation
  ↓
Responsive UI
  ↓
Dashboard
  ↓
API Services
  ↓
FastAPI Backend
```

It also deliberately **does not document AWS infrastructure as though the frontend owns it**. That keeps the frontend README properly scoped.

### One important adjustment

Because this README is a **real project README**, unlike your detailed Phase 19 documentation, I recommend that **this one be committed**.

Your detailed phase documentation remains here and stays local:

```text
docs/
└── PHASE 19 — Frontend UI-UX Design & Implementation/
```

while the concise project README lives here:

```text
frontend/
└── README.md
```

So the next step should be:

1. Replace the existing `frontend/README.md` with the content above.
2. Run `npm run build`.
3. Run `git diff --check`.
4. Review the README diff.
5. Commit it as part of **19.12 Phase Close-out**.
6. Push.
7. Record Phase 19 as officially complete.

I would use the commit:

```bash
git commit -m "docs(frontend): document phase 19 frontend"
```

This keeps the documentation change separate and clearly identifiable from the 19.10 accessibility implementation commit.
