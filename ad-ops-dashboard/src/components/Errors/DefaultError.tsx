import { useRouteError } from "react-router-dom";
import * as Sentry from "@sentry/react";
import { useEffect } from "react";

export function DefaultError() {
  const error = useRouteError() as Error;

  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <div>
      <h1> :( This is the default error page. </h1>
    </div>
  );
}
