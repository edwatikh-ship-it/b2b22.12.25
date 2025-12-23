import { Suspense } from "react"
import { SuppliersClient } from "./suppliers-client"

export default function SuppliersPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SuppliersClient />
    </Suspense>
  )
}
