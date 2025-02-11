import React, { useCallback, useState, ReactElement } from "react"
import {
  FieldType,
  Filters,
  Formatters,
  OperatorType,
  SlickgridReact,
} from 'slickgrid-react'
import { ExcelExportService } from '@slickgrid-universal/excel-export';
import { TextExportService } from '@slickgrid-universal/text-export';

import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"

import "./style.scss"

function StreamlitSlickGrid({ args, disabled, theme }: ComponentProps): ReactElement {
  const [columns, useColumns] = useState(() => replaceJsStrings(args.columns))
  const [options, setOptions] = useState(() => replaceJsStrings(args.options))
  const [data, setData] = useState(args.data)

  // @ts-ignore
  const onClick = useCallback((ev) => {
    // Ignore clicks on the expander element.
    if (ev.detail.eventData?.target?.classList.contains("slick-group-toggle"))
      return

    Streamlit.setComponentValue([
      ev.detail.args.row,
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

const MODULES = {
  "Formatters": Formatters,
  "FieldType": FieldType,
  "Filters": Filters,
  "OperatorType": OperatorType,
  "ExportServices": {
    "ExcelExportService": new ExcelExportService(),
    "TextExportService": new TextExportService(),
  }
}

function replaceJsStrings(obj: any): any {
  const result = Array.isArray(obj) ? [] : {};
  const stack = [{ source: obj, target: result }];

  while (stack.length > 0) {
    const { source, target } = stack.pop() ?? {};

    for (const key in source) {
      if (typeof source[key] === 'string' && source[key].startsWith('js$')) {
        const [moduleStr, memberStr] = source[key].slice(3).split('.');
        // @ts-ignore
        const module = MODULES[moduleStr];
        // @ts-ignore
        if (module && target) target[key] = module[memberStr]

      } else if (typeof source[key] === 'object' && source[key] !== null) {
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

export default withStreamlitConnection(StreamlitSlickGrid)
