import { Suspense } from "react"
import { KeywordsClient } from "./keywords-client"

export default function KeywordsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <KeywordsClient />
    </Suspense>
  )
}
