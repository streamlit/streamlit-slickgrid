// Copyright 2025 Snowflake Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { useCallback, useEffect, useState, ReactElement } from "react"
import {
  Column,
  createDomElement,
  decimalFormatter,
  FieldType,
  Filters,
  Formatters,
  getValueFromParamsOrFormatterOptions,
  GridOption,
  OperatorType,
  SlickGrid,
  SlickgridReact,
} from "slickgrid-react"
import { ExcelExportService } from "@slickgrid-universal/excel-export";
import { TextExportService } from "@slickgrid-universal/text-export";

import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"

import "./style.scss"

function StreamlitSlickGrid({ args, disabled, theme }: ComponentProps): ReactElement {
  const [columns, setColumns] = useState(() => replaceJsStrings(args.columns))
  const [options, setOptions] = useState(() => replaceJsStrings(args.options))
  const [data, setData] = useState(args.data)

  useEffect(() => {
    setColumns(replaceJsStrings(args.columns))
    setOptions(replaceJsStrings(args.options))
    setData(args.data)
  }, [args, args.data, args.columns, args.options])

  // @ts-ignore
  const onClick = useCallback((ev) => {
    // Ignore clicks on the expander element.
    if (ev.detail.eventData?.target?.classList.contains("slick-group-toggle"))
      return

    const data = ev.detail.args.grid.data
    const rowId = data.rows[ev.detail.args.row][data.idProperty]

    Streamlit.setComponentValue([
      rowId,
      ev.detail.args.cell,
    ])
  }, [])

  const onReactGridCreated = useCallback(() => {
    Streamlit.setFrameHeight()
  }, [])

  return (
    <SlickgridReact
      gridId="streamlit-slickgrid"
      columnDefinitions={columns}
      gridOptions={options}
      dataset={data}
      onReactGridCreated={onReactGridCreated}
      onClick={args.onClick ? onClick : undefined}
    />
  )
}

function replaceJsStrings(obj: any): any {
  const result = Array.isArray(obj) ? [] : {};
  const stack = [{ source: obj, target: result }];

  while (stack.length > 0) {
    const { source, target } = stack.pop() ?? {};

    for (const key in source) {
      if (typeof source[key] === "string" && source[key].startsWith("js$")) {
        const [moduleStr, memberStr] = source[key].slice(3).split(".");
        // @ts-ignore
        const module = MODULE_PROXIES[moduleStr];
        // @ts-ignore
        if (module && target) target[key] = module[memberStr]

      } else if (typeof source[key] === "object" && source[key] !== null) {
        // @ts-ignore
        target[key] = Array.isArray(source[key]) ? [] : {};
        // @ts-ignore
        stack.push({ source: source[key], target: target[key] });

      } else {
        // @ts-ignore
        target[key] = source[key];
      }
    }
  }

  return result;
}

type ColorDefs = [number | null, string, string][]
type ReplacementDefs = Record<any, string>

const StreamlitSlickGridFormatters = {
  /**
   * Adds styling and decorations to a number, inlcuding: colors, prefix, suffix,
   * number of decimal places, decimal separators, etc.
   *
   * Example:
   *
   * columns = {
   *   ...
   *   {
   *     ...
   *     "formatter": StreamlitSlickGridFormatters.numberFormatter,
   *
   *     # Everything below is optional.
   *     "params": {
   *
   *       # Define color bands. The format is [maxValue, foregroundColor, backgroundColor].
   *       # The color is selected by testing each triplet left to right. The first to match wins.
   *       # If a maxValue of null is reached, that set of colors is picked.
   *       "colors": [[20, "#f00"], [40, "#ff0"], [80, "#0b0"], [100, "#00f"]],
   *
   *       # Define number of decimal places.
   *       "minDecimal": 2,
   *       "maxDecimal": 4,
   *
   *       # Define suffix/prefix:
   *       "numberPrefix": "$",
   *       "numberSuffix": "!",
   *
   *       # Tweak locale information:
   *       "decimalSeparator": ".",
   *       "thousandSeparator": ",",
   *
   *       # Use parentheses for negative numbers:
   *       "wrapNegativeNumbers": false,
   *     }
   *   }
   * }
   *
   */
  numberFormatter(row: any, cell: number, value: number, columnDef: Column, dataContext: Record<string, any>, grid: SlickGrid) {
    const formattedStr = decimalFormatter(row, cell, value, columnDef, dataContext, grid)
    const [fgColor, bgColor] = getColor(value, columnDef, grid)

    const gridOptions = (grid && typeof grid.getOptions === "function" ? grid.getOptions() : {}) as GridOption
    const style: Record<string, any> = getValueFromParamsOrFormatterOptions("style", columnDef, gridOptions, [])

    return createDomElement("span", {
      style: {
        color: fgColor,
        backgroundColor: bgColor,
        ...style
      },
      textContent: formattedStr as string,
    })
  },

  /**
   * Replaces strings with others.
   *
   * Example:
   *
   * columns = {
   *   ...
   *   {
   *     ...
   *     "formatter": StreamlitSlickGridFormatters.stringReplacer,
   *
   *     # Everything below is optional.
   *     "params": {
   *       "replacements": {
   *          "true": "😃",
   *          "false": "😭",
   *          "null": "🫣",
   *       },
   *     }
   *   }
   * }
   *
   */
  stringReplacer(_row: any, _cell: number, value: any, columnDef: Column, _dataContext: Record<string, any>, grid: SlickGrid) {
    const gridOptions = (grid && typeof grid.getOptions === "function" ? grid.getOptions() : {}) as GridOption
    const replacementDefs: ReplacementDefs = getValueFromParamsOrFormatterOptions("replacements", columnDef, gridOptions, [])

    return replacementDefs?.[String(value)] ?? value
  },

  /**
   * Formats the number as a bar. Same as SlickGrid's percentComplete formatter, but with color
   * configuration, and not specific to percentages.
   *
   * Example:
   *
   * columns = {
   *   ...
   *   {
   *     ...
   *     "formatter": StreamlitSlickGridFormatters.barFormatter,
   *
   *     # Everything below is optional.
   *     "params": {
   *       # Supports everything numberFormatter does!
   *       # In particular, don't forget to configure the colors.
   *     }
   *   }
   * }
   *
   */
  barFormatter(row: any, cell: number, value: number, columnDef: Column, dataContext: Record<string, any>, grid: SlickGrid) {
    return StreamlitSlickGridFormatters.stackedBarFormatter(row, cell, [value], columnDef, dataContext, grid)
  },

  /**
   * Formats an array of numbers horizontally-stacked bar charts. The data should be in the format [number1, number2, ...].
   *
   * Example:
   *
   * columns = {
   *   ...
   *   {
   *     ...
   *     "formatter": StreamlitSlickGridFormatters.stackedBarFormatter,
   *
   *     # Everything below is optional.
   *     "params": {
   *       # Supports everything numberFormatter does!
   *       # In particular, don't forget to configure the colors.
   *     }
   *   }
   * }
   *
   */
  stackedBarFormatter(row: any, cell: number, values: number[], columnDef: Column, dataContext: Record<string, any>, grid: SlickGrid) {
    if (!Array.isArray(values)) return ""

    const gridOptions = (grid && typeof grid.getOptions === "function" ? grid.getOptions() : {}) as GridOption
    const min = getValueFromParamsOrFormatterOptions("min", columnDef, gridOptions, 0)
    const max = getValueFromParamsOrFormatterOptions("max", columnDef, gridOptions, 100)
    const style: Record<string, any> = getValueFromParamsOrFormatterOptions("style", columnDef, gridOptions, [])

    const container = createDomElement("div", {
      className: "progress",
      style: {
        gap: "1px"
      }
    })

    for (let inputNumber of values) {
      const [fgColor, bgColor] = getColor(inputNumber, columnDef, grid)
      const inputPct = (inputNumber - min) / max * 100
      const formattedStr = decimalFormatter(row, cell, inputNumber, columnDef, dataContext, grid) as string

      container.appendChild(
        createDomElement("div", {
          className: "progress-bar",
          role: "progressbar",
          ariaValueNow: formattedStr,
          ariaValueMin: "0",
          ariaValueMax: "100",
          textContent: formattedStr,
          style: {
            minWidth: "2em",
            width: `${inputPct}%`,
            color: fgColor,
            backgroundColor: bgColor,
            ...style,
          },
        })
      )
    }

    return container
  },
}

const StreamlitSlickGridSorters = {
  numberArraySorter(a: number[], b: number[]): number {
    const sumA = a.reduce((x, y) => x + y, 0)
    const sumB = b.reduce((x, y) => x + y, 0)
    return sumA - sumB
  },
}

function getColor(value: number, columnDef: Column, grid: SlickGrid): [string, string] | [] {
  const gridOptions = (grid && typeof grid.getOptions === "function" ? grid.getOptions() : {}) as GridOption
  const colorDefs: ColorDefs = getValueFromParamsOrFormatterOptions("colors", columnDef, gridOptions, [])

  for (let [v, fg, bg] of colorDefs) {
    if (!fg) fg = "unset"
    if (!bg) bg = "transparent"
    if (v == null) return [fg, bg] // null always wins.
    if (value <= v) return [fg, bg]
  }

  return []
}

const MODULE_PROXIES = {
  "Formatters": Formatters,
  "FieldType": FieldType,
  "Filters": Filters,
  "OperatorType": OperatorType,
  "ExportServices": {
    "ExcelExportService": new ExcelExportService(),
    "TextExportService": new TextExportService(),
  },
  "StreamlitSlickGridFormatters": StreamlitSlickGridFormatters,
  "StreamlitSlickGridSorters": StreamlitSlickGridSorters,
}

export default withStreamlitConnection(StreamlitSlickGrid)
