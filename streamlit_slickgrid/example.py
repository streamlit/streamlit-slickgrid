import streamlit as st
import numpy as np
import pandas as pd
import math
import random
from streamlit_slickgrid import (
    add_tree_info,
    slickgrid,
    Formatters,
    Filters,
    FieldType,
    OperatorType,
    ExportServices,
)

st.set_page_config(
    layout="wide",
)


def mockData(count):
    mockDataset = []

    epics_in_milestone = 0
    tasks_in_epic = 0
    m = 0
    e = 0
    t = 0

    for i in range(count):
        randomYear = 2000 + math.floor(random.random() * 10)
        randomMonth = math.floor(random.random() * 11)
        randomDay = math.floor((random.random() * 29))
        randomPercent = round(random.random() * 100)

        if t >= tasks_in_epic:
            tasks_in_epic = random.randint(2, 10)
            t = 0
            e += 1
        else:
            t += 1

        if e >= epics_in_milestone:
            epics_in_milestone = random.randint(2, 10)
            tasks_in_epic = 0
            m += 1
            e = 0
            t = 0

        mockDataset.append(
            {
                "id": i,
                "milestone": f"Milestone M{m:02}",
                "epic": None if e == 0 else f"Epic M{m:02}/E{e:02}",
                "task": None if t == 0 else f"Task M{m:02}/E{e:02}/T{t:02}",
                "duration": str(round(random.random() * 100)),
                "percentComplete": randomPercent,
                "start": f"{randomYear:02}-{randomMonth + 1:02}-{randomDay:02}",
                "finish": f"{randomYear + 1:02}-{randomMonth + 1:02}-{randomDay:02}",
                "effortDriven": (i % 5 == 0),
            }
        )

    return mockDataset


"""
# SlickGrid-Streamlit demo
"""

data = add_tree_info(
    mockData(1000),
    tree_fields=["milestone", "epic", "task"],
    join_fields_as="title",
)

columns = [
    {
        "id": "title",
        "name": "Title",
        "field": "title",
        "sortable": True,
        "minWidth": 50,
        "type": FieldType.string,
        "filterable": True,
        "formatter": Formatters.tree,
        "exportCustomFormatter": Formatters.treeExport,
    },
    {
        "id": "duration",
        "name": "Duration (days)",
        "field": "duration",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.number,
        "filterable": True,
        "filter": {
            "model": Filters.slider,
            "operator": ">=",
        },
    },
    {
        "id": "%",
        "name": "% Complete",
        "field": "percentComplete",
        "sortable": True,
        "minWidth": 100,
        "formatter": Formatters.progressBar,
        "type": FieldType.number,
        "filterable": True,
        "filter": {
            "model": Filters.sliderRange,
            "maxValue": 100,
            "operator": OperatorType.rangeInclusive,
            "filterOptions": {"hideSliderNumbers": False, "min": 0, "step": 5},
        },
    },
    {
        "id": "start",
        "name": "Start",
        "field": "start",
        "formatter": Formatters.dateIso,
        "type": FieldType.date,
        "filterable": True,
        "filter": {"model": Filters.compoundDate},
    },
    {
        "id": "finish",
        "name": "Finish",
        "field": "finish",
        "formatter": Formatters.dateIso,
        "type": FieldType.date,
        "filterable": True,
        "filter": {"model": Filters.dateRange},
    },
    {
        "id": "effort-driven",
        "name": "Effort Driven",
        "field": "effortDriven",
        "sortable": True,
        "minWidth": 100,
        "formatter": Formatters.checkmarkMaterial,
        "type": FieldType.boolean,
        "filterable": True,
        "filter": {
            "model": Filters.singleSelect,
            "collection": [
                {"value": "", "label": ""},
                {"value": True, "label": "True"},
                {"value": False, "label": "False"},
            ],
        },
    },
]

options = {
    "enableFiltering": True,
    #
    # You could debounce/throttle the input text filter if you have lots of data
    # filterTypingDebounce: 250,
    "enableExcelExport": True,
    #
    # Set up export options.
    "enableTextExport": True,
    "excelExportOptions": {"sanitizeDataExport": True},
    "textExportOptions": {"sanitizeDataExport": True},
    "externalResources": [
        ExportServices.ExcelExportService,
        ExportServices.TextExportService,
    ],
    #
    # Pin columns.
    # "frozenColumn": 0,
    #
    # Pin rows.
    # "frozenRow": 0,
    #
    # Don't scroll table when too big. Instead, just let it grow.
    # "autoHeight": True,
    #
    "autoResize": {
        "minHeight": 500,
    },
    # You must enable this flag for the filtering & sorting to work as expected
    "enableTreeData": True,
    "treeDataOptions": {
        "columnId": "title",
        "parentPropName": "__parent",
        # This is optional, you can define the tree level property name that will be used for the sorting/indentation, internally it will use "__treeLevel"
        "levelPropName": "__indent",
        "indentMarginLeft": 15,
        "initiallyCollapsed": True,
    },
    #
    # For tree, must turn off multicolumn sorting
    "multiColumnSort": False,
}

out = slickgrid(data, columns, options, key="mygrid", on_click="rerun")


@st.dialog("Details", width="large")
def show_dialog(item):
    st.write("Congrats! You clicked on the row below:")
    st.write(item)

    st.write("Here's a random chart for you:")
    st.write("")

    st.scatter_chart(np.random.randn(100, 5))


if out is not None:
    row, col = out
    show_dialog(data[row])

st.markdown(f"Return: {out}")
