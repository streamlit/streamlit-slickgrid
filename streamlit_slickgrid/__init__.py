import os
import streamlit.components.v1 as components

_RELEASE = False

_NAME = "streamlit-slickgrid"

if not _RELEASE:
    _component_func = components.declare_component(
        _NAME,
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(_NAME, path=build_dir)


def slickgrid(data, columns, options=None, on_click=None, key=None):
    """Display a SlickGrid component.

    Parameters
    ----------
    data: pandas.DataFrame
    columns: list of dict
    options: dict or None
    on_click: "rerun", "ignore", or None
        Custom Components do not support callbacks :(

    Returns
    -------
    None
        No return.

    """
    component_value = _component_func(
        data=data,
        columns=columns,
        options=options,
        onClick=on_click is not None and on_click != "ignore",
        key=key,
        default=None,
    )

    return component_value


def add_tree_info(data, tree_fields, join_fields_as=None, id_field="id"):
    """Calculates tree fields __indent and __parent from data structure. Returns a new data array.

    For example:

        Let's say `data` has the form:

            id, continent, country, city, population

        Then you'd call this:

            add_tree_info(data, ["continent", "country", "city"])

        And end up with something like:
            __parent __indent id continent country city population
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

            __parent __indent id my_field continent country city population
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

        new_item["__indent"] = P

        if P > 0:
            new_item["__parent"] = parents[-1][id_field]
        else:
            new_item["__parent"] = None

        if join_fields_as is not None:
            new_item[join_fields_as] = new_item[tree_fields[P]]

    return new_data


class _JsModuleProxy:
    def __init__(self, js_module_name):
        self.name = js_module_name

    def __getattr__(self, key):
        return f"js${self.name}.{key}"


def __getattr__(js_module_name):
    """Syntax sugar so you can do this:

        from streamlit_slickgrid import Foo

        Foo.bar
        # Returns "js$Foo.bar"!

    Why this is useful: SlickGrid's options are often JS functions that you need to pass by
    reference, and this allows us to pass them by name instead (since it's not possible to pass
    a function safely from Python to JS).

    On the JS side, see `replaceJsStrings`.

    """
    return _JsModuleProxy(js_module_name)
