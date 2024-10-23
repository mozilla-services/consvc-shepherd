import { useEffect } from "react";
import * as Sentry from "@sentry/react";

import {
  createBrowserRouter,
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from "react-router-dom";


const isLocal = process.env.NODE_ENV === 'development';
const options: Sentry.BrowserOptions = {
  dsn: process.env.SENTRY_DSN,
  integrations: [
    // See docs for support of different versions of variation of react router
    // https://docs.sentry.io/platforms/javascript/guides/react/configuration/integrations/react-router/
    Sentry.reactRouterV6BrowserTracingIntegration({
      useEffect: useEffect,
      useLocation,
      useNavigationType,
      createRoutesFromChildren,
      matchRoutes,
    }),
    Sentry.browserTracingIntegration(),
  ],
  environment: process.env.NODE_ENV,
  // Set tracesSampleRate to 1.0 to capture 100%
  // of transactions for tracing.
  tracesSampleRate: 1.0,
}

// Log sentry events to the console, not sentry when on local dev
if (isLocal) {
  options.beforeSend = (event: Sentry.ErrorEvent) => {
    console.log('Sentry Event:', event); // Log the event for testing
    return null; // Prevent sending to real sentry
  }
}

Sentry.init(options)


export const sentryCreateBrowserRouter = Sentry.wrapCreateBrowserRouter(
  createBrowserRouter,
);
