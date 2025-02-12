# Copyright 2025 Snowflake Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import os
import streamlit.components.v1 as components

_RELEASE = True
_NAME = "streamlit-slickgrid"

if _RELEASE:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        _NAME,
        path=build_dir,
    )
else:
    _component_func = components.declare_component(
        _NAME,
        url="http://localhost:3001",
    )


def slickgrid(data, columns, options=None, on_click=None, key=None):
    """Display a SlickGrid component.

    The best way to learn use SlickGrid is to check out the demos at:
    - https://ghiscoding.github.io/slickgrid-react-demos/#/example1

    Parameters
    ----------
    data: list of dict
        The dataset to display, as a list of dicts. For example:

        data = [
          {"id": 0, "continent": "america", "revenue": 20000, "paused": False},
          {"id": 1, "continent": "africa",  "revenue": 40100, "paused": False},
          {"id": 2, "continent": "asia",    "revenue": 10300, "paused": True},
          {"id": 3, "continent": "europe",  "revenue": 30200, "paused": False},
          ...
        ]

    columns: list of dict
        Column definitions. Which columns to show, how to show them, how to
        filter them, etc.

        See full list of options at:
        - https://github.com/ghiscoding/slickgrid-universal/blob/master/packages/common/src/interfaces/column.interface.ts#L40

        Not all column options are supported, though!

    options: dict or None
        Global grid options.

        See full list of options at:
        - https://github.com/ghiscoding/slickgrid-universal/blob/master/packages/common/src/interfaces/gridOption.interface.ts#L76

        Not all grid options are supported, though!

    on_click: "rerun", "ignore", or None
        If "rerun", then the clicked cell [row, col] will be returned
        by this function.

    Returns
    -------
    None or list of numbers
        If on_click is set to "rerun", the [row, col] indices of the clicked
        cell is returned. Otherwise, None.

    """
    session_key = f"-streamlit-slickgrid-{key}"
    if session_key not in st.session_state:
        st.session_state[session_key] = None

    component_value = _component_func(
        data=data,
        columns=columns,
        options=options,
        onClick=on_click is not None and on_click != "ignore",
        key=key,
        default=None,
    )

    change_detected = component_value != st.session_state[session_key]

    st.session_state[session_key] = component_value

    if change_detected:
        return component_value
    else:
        return None


def add_tree_info(data, tree_fields, join_fields_as=None, id_field="id"):
    """Calculates tree fields data's structure. Returns a new data array.

    Parameters
    ----------
    data: list of dict
        See slickgrid() data field.

    tree_fields: list of str
        List with name of fields to coalesce into a tree structure.

    join_fields_as: str
        Name of the new column that will be added with the coalesced fields.

    id_field: str
        Name of the ID field used in data. Defaults to "id".

    Returns
    -------
    list of dict
        A copy of the data, but with 3 additional fields:
        - The join field: see join_field_as
        - __parent: a field holding parent/child relationships
        - __depth: a field holding parent/child depth information

    Example
    -------

        Let's say `data` has the form:

            id, continent, country, city, population

        Then you'd call this:

            add_tree_info(data, ["continent", "country", "city"])

        And end up with something like:
            __parent __depth id continent country city population
            None     0        0  A0        None    None P1
            0        1        1  A0        B1      C1   P2
            None     0        2  A2        None    None P3
            None     2        3  A2        B3      None P4
            None     3        4  A2        B3      C4   P5
            None     3        5  A2        B3      C5   P6

        Which implies the following structure:

            id     continent country city population
            + 0    A0        None    None P1
            └─ 1   A0        B1      C1   P2
            + 2    A2        None    None P3
            └─+ 3  A2        B3      None P4
              ├─ 4 A2        B3      C4   P5
              └─ 5 A2        B3      C5   P6

        You can also set join_fields_as to some string "my_field" to join
        all the tree fields into a new column, like this:

            __parent __depth id my_field continent country city population
            None     0        0  A0       A0        None    None P1
            0        1        1  B1       A0        B1      C1   P2
            None     0        2  A2       A2        None    None P3
            None     2        3  B3       A2        B3      None P4
            None     3        4  C4       A2        B3      C5   P5
            None     3        5  C5       A2        B3      C6   P6

        Because, then, you can hide the other columns and get a pretty
        tree like this:

            my_field population
            + A0     P1
            └─ B1    P2
            + A2     P3
            └─+ B3   P4
              ├─ C4  P5
              └─ C5  P6
    """

    new_data = []
    parents = []

    for i, item in enumerate(data):
        num_equal_fields = 0

        if i > 0:
            prev_item = data[i - 1]

            for field in tree_fields:
                if item[field] == prev_item[field]:
                    num_equal_fields += 1
                else:
                    break

            if num_equal_fields > len(parents):
                parents.append(prev_item)
            elif num_equal_fields < len(parents):
                parents = parents[:num_equal_fields]

        P = len(parents)
        new_item = {**item}
        new_data.append(new_item)

        new_item["__depth"] = P

        if P > 0:
            new_item["__parent"] = parents[-1][id_field]
        else:
            new_item["__parent"] = None

        if join_fields_as is not None:
            new_item[join_fields_as] = new_item[tree_fields[P]]

    return new_data


class _JsModuleProxy:
    """Dummy class that produces strings pointing to JS functions."""

    def __init__(self, js_module_name):
        self.name = js_module_name

    def __getattr__(self, key):
        return f"js${self.name}.{key}"


def __getattr__(js_module_name):
    """Syntax sugar so you can do this:

        from streamlit_slickgrid import Foo

        Foo.bar
        # Returns "js$Foo.bar"!

    Why this is useful: SlickGrid's options are often JS functions that you
    need to pass by reference, and this allows us to pass them by name
    instead (since it's not possible to pass a function safely from Python
    to JS).

    This allows you to use any of the modules listed in the MODULE_PROXIES
    object, on the JS side.
    """
    return _JsModuleProxy(js_module_name)
