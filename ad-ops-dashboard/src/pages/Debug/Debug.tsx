
import * as Sentry from "@sentry/react";
import { useEffect, useState } from "react";
import Page404 from "../Page404";
export default function Debug() {

  const [isPageBroken, setIsPageBroken] = useState(false)
  const [errorCount, setErrorCount] = useState(0)

  useEffect(() => {
    if (errorCount > 0) {
      throw new Error("SENTRY TEST: A use effect errored!")
    }

  }, [errorCount]
  )

  const makeError = () => {
    try {
      throw new Error("SENTRY TEST: Uh oh! We did an error!")
    } catch (err) {
      Sentry.captureException(err);
    }
  }

  if (process.env.NODE_ENV === "development") {
    return (
      <div style={{ textAlign: "center", padding: 20 }}>
        <div>
          <h2> Debug pannel! (Dev Env Only) </h2>
          <p>Include any buttons here that force certain actions or frontend states. This page is only visible running `npm run dev` and cannot be viewed in production builds</p>
        </div>
        <div style={{ display: "flex", paddingTop: 20, gap: 20, justifyContent: "center" }}>
          <button
            type="button"
            onClick={makeError}> Throw caught sentry error
          </button>
          <button
            type="button"
            onClick={() => { setErrorCount(1); }}> Break useEffect
          </button>
          <button
            type="button"
            onClick={() => { setIsPageBroken(true); }}> Break Page
          </button>
        </div>
        { /* eslint-disable-next-line */}
        <div> {isPageBroken && <ErrorComponent />} </div>
      </div>
    )
  } else {
    return < Page404 />
  }

} 
