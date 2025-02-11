import React from "react"
import { createRoot } from "react-dom/client"
import StreamlitSlickGrid from "./StreamlitSlickGrid"

const element = document.getElementById("root")
const root = createRoot(element as HTMLElement)

root.render(
  <StreamlitSlickGrid />
)
