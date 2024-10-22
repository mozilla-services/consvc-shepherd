
import * as Sentry from "@sentry/react";
import { useEffect, useState } from "react";
export default function Debug() {

  const [isPageBroken, setIsPageBroken] = useState(false)
  const [errorCount, setErrorCount] = useState(0)

  useEffect(() => {
    if (errorCount > 0) {
      throw new Error("Use effect errored!")
    }

  }, [errorCount]
  )

  const makeError = () => {
    try {
      throw new Error("Uh oh! We did an error!")
    } catch (err) {
      Sentry.captureException(err);
    }
  }

  return (
    <div style={{ textAlign: "center", padding: 20 }}>    <h1> Debug pannel </h1>
      <div style={{ display: "flex", gap: 20, justifyContent: "center" }}>
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
} 
