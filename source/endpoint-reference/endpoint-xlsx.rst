Xlsx
----

The ``xlsx`` endpoint takes as input a prepared table (intended for use
with multitables) and returns an xlsx file, with some basic formatting
conventions.

A POST request to ``/api/xlsx/`` will return an xlsx file directly, with
correct content-disposition and type headers.

POST
^^^^

.. code:: http

    POST /api/xlsx/ HTTP/1.1

--------------

.. code:: http

    HTTP/1.1 200 OK
    Content-Disposition: attachment; filename=Crunch-export.xlsx
    Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

.. code:: json

    {
        "element": "shoji:entity",
        "body": {
            "result": [
                {
                    "rows": [],
                    "etc.": "described below"
                }
            ]
        }
    }

Endpoint Parameters
^^^^^^^^^^^^^^^^^^^

At the top level, the xlsx takes a ``result`` *array* and
``display_settings`` object which defines some formatting to be used on
the values. Multiple tables can be placed on a single sheet.

Result
''''''

+---------+-------+----------+--------------+----------------+
| Name    | Type  | Typical  | Description  |
|         |       | element  |              |
+=========+=======+==========+==============+================+
| rows    | array | ``{"valu | Cells are    |
|         |       | e": 30,  | objects with |
|         |       | "class": | at least a   |
|         |       |  "format | ``value``    |
|         |       | ted"}``  | member, and  |
|         |       |          | optional     |
|         |       |          | ``class``,   |
|         |       |          | where a      |
|         |       |          | value of     |
|         |       |          | ``"formatted |
|         |       |          | "``          |
|         |       |          | prevents the |
|         |       |          | exporter     |
|         |       |          | from         |
|         |       |          | applying any |
|         |       |          | number       |
|         |       |          | format to    |
|         |       |          | the result   |
|         |       |          | cell         |
+---------+-------+----------+--------------+----------------+
| colLabe | array | ``{"valu | Array of     |
| ls      |       | e": "All | objects with |
|         |       | "}``     | a ``value``  |
|         |       |          | member       |
+---------+-------+----------+--------------+----------------+
| colTitl | array | ``"Age"` | Array of     |
| es      |       | `        | strings      |
+---------+-------+----------+--------------+----------------+
| spans   | array | ``4``    | array of     |
|         |       |          | integers     |
|         |       |          | matching the |
|         |       |          | length of    |
|         |       |          | colTitles,   |
|         |       |          | indicating   |
|         |       |          | the number   |
|         |       |          | of cells to  |
|         |       |          | be joined    |
|         |       |          | for each     |
|         |       |          | colTitle     |
|         |       |          | after the    |
|         |       |          | first one.   |
|         |       |          | The first    |
|         |       |          | colTitle is  |
|         |       |          | assumed to   |
|         |       |          | be only one  |
|         |       |          | column wide. |
+---------+-------+----------+--------------+----------------+
| rowTitl | strin | ``"Dog f | A title,     |
| e       | g     | ood bran | which is     |
|         |       | ds"``    | formatted    |
|         |       |          | bold above   |
|         |       |          | the first    |
|         |       |          | column of    |
|         |       |          | the table    |
|         |       |          | (the         |
|         |       |          | rowLabels,   |
|         |       |          | below)       |
+---------+-------+----------+--------------+----------------+
| rowLabe | array | ``{"valu | labels for   |
| ls      |       | e": "Can | rows of the  |
|         |       | ine Crun | table        |
|         |       | ch"}``   |              |
+---------+-------+----------+--------------+----------------+
| rowVari | strin | ``"Prefe | title to     |
| ableNam | g     | rred dog | display at   |
| e       |       |  food"`` | the very top |
|         |       |          | left of the  |
|         |       |          | result sheet |
+---------+-------+----------+--------------+----------------+
| filter\ | array | ``"Breed | Names of any |
| _names  |       | : Dachsh | filters to   |
|         |       | und"``   | print        |
|         |       |          | beneath the  |
|         |       |          | table, will  |
|         |       |          | be labeled   |
|         |       |          | "Filters".   |
|         |       |          | If multiple  |
|         |       |          | result       |
|         |       |          | objects are  |
|         |       |          | included in  |
|         |       |          | the payload, |
|         |       |          | the filter   |
|         |       |          | names from   |
|         |       |          | the *first*  |
|         |       |          | result are   |
|         |       |          | used, and    |
|         |       |          | placed at    |
|         |       |          | the bottom   |
|         |       |          | of the sheet |
|         |       |          | beneath all  |
|         |       |          | results.     |
+---------+-------+----------+--------------+----------------+

Display Settings
''''''''''''''''

Further customization for the resulting output.

+---------+-------+----------+--------------+----------------+
| Name    | Type  | Default  | Description  | Example        |
+=========+=======+==========+==============+================+
| decimal | objec | 0        | number of    | ``{"value": 0} |
| Places  | t     |          | decimal      | ``             |
|         |       |          | places to    |                |
|         |       |          | diaplay      |                |
+---------+-------+----------+--------------+----------------+
| countsO | objec | percent  | use counts   | ``{"value": "p |
| rPercen | t     |          | or percents  | ercent"}``     |
| ts      |       |          |              |                |
+---------+-------+----------+--------------+----------------+
| percent | objec | {"value" | row or       | ``{"value": "c |
| ageDire | t     | :        | column based | olPct"}``      |
| ction   |       | "colPct" | percents     |                |
|         |       | }        |              |                |
+---------+-------+----------+--------------+----------------+
| valuesA | objec | false    | are values   | ``{"value": fa |
| reMeans | t     |          | means? (If   | lse}``         |
|         |       |          | so, will be  |                |
|         |       |          | formatted    |                |
|         |       |          | with decimal |                |
|         |       |          | places)      |                |
+---------+-------+----------+--------------+----------------+

Quirks
''''''

Because the formatted output was designed to display values computed by
other clients, it abuses some assumptions about the tables it is
displaying. Some of these are enumerated below.

1. Rows have a ‘marginal’ column positioned first after the row label.
2. If display settings indicate ``rowPct``, rows have an additional
   marginal column intended to show unconditional N for each row.
3. The remaining row labels are all accounted for in the sum of
   ``spans``.
4. Column titles are placed in merged cells above one or more labels.
5. The same filter(s) are applied to all tables on a page.
6. No “freeze panes” are applied to the result.
7. If the table contains percentages, they should be percentages, not
   proportions (0 to 100, not 0 to 1).

Complete example
~~~~~~~~~~~~~~~~

.. code:: json

    {"element":"shoji:entity",
    "body":{
        "result": [
      {
        "filter_names": ["Name_of_filter"],
        "rows": [
          [
            {
              "value": 50,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 50,
              "pValue": 0,
              "class": "subtable-0 col-0"
            },
            {
              "value": 50,
              "pValue": 0,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 50,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 50,
              "pValue": 0,
              "class": "subtable-0 col-0"
            },
            {
              "value": 50,
              "pValue": 0,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 0,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 0,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-1"
            }
          ]
        ],
        "colLabels": [
          {
            "value": "All"
          },
          {
            "value": "2014",
            "class": "col-0"
          },
          {
            "value": "2015",
            "class": "col-1"
          }
        ],
        "spans": [
          2
        ],
        "rowLabels": [
          {
            "value": "a",
            "class": "row-label"
          },
          {
            "value": "b",
            "class": "row-label"
          },
          {
            "value": "c",
            "class": "row-label"
          },
          {
            "value": "d",
            "class": "row-label"
          }
        ],
        "rowTitle": "ca_subvar_1",
        "rowVariableName": "categorical_array",
        "colTitles": [
          "quarter"
        ]
      },
      {
        "rows": [
          [
            {
              "value": 16.666666666666664,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 25,
              "pValue": 0.24821309601845032,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": -0.2482130960184501,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 50,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 50,
              "pValue": 0,
              "class": "subtable-0 col-0"
            },
            {
              "value": 50,
              "pValue": 0,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 33.33333333333333,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 25,
              "pValue": -0.5464935495198773,
              "class": "subtable-0 col-0"
            },
            {
              "value": 50,
              "pValue": 0.5464935495198773,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 0,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-1"
            }
          ]
        ],
        "colLabels": [
          {
            "value": "All"
          },
          {
            "value": "2014",
            "class": "col-0"
          },
          {
            "value": "2015",
            "class": "col-1"
          }
        ],
        "spans": [
          2
        ],
        "rowLabels": [
          {
            "value": "a",
            "class": "row-label"
          },
          {
            "value": "b",
            "class": "row-label"
          },
          {
            "value": "c",
            "class": "row-label"
          },
          {
            "value": "d",
            "class": "row-label"
          }
        ],
        "rowTitle": "ca_subvar_2",
        "rowVariableName": "categorical_array",
        "colTitles": [
          "quarter"
        ]
      },
      {
        "rows": [
          [
            {
              "value": 0,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": null,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 33.33333333333333,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 50,
              "pValue": 0.045500259780248964,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": -0.045500259780248964,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 16.666666666666664,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 25,
              "pValue": 0.24821309601845032,
              "class": "subtable-0 col-0"
            },
            {
              "value": 0,
              "pValue": -0.2482130960184501,
              "class": "subtable-0 col-1"
            }
          ],
          [
            {
              "value": 50,
              "class": "marginal marginal-percentage"
            },
            {
              "value": 25,
              "pValue": -0.0005320055485602548,
              "class": "subtable-0 col-0"
            },
            {
              "value": 100,
              "pValue": 0.0005320055485602548,
              "class": "subtable-0 col-1"
            }
          ]
        ],
        "colLabels": [
          {
            "value": "All"
          },
          {
            "value": "2014",
            "class": "col-0"
          },
          {
            "value": "2015",
            "class": "col-1"
          }
        ],
        "spans": [
          2
        ],
        "rowLabels": [
          {
            "value": "a",
            "class": "row-label"
          },
          {
            "value": "b",
            "class": "row-label"
          },
          {
            "value": "c",
            "class": "row-label"
          },
          {
            "value": "d",
            "class": "row-label"
          }
        ],
        "rowTitle": "ca_subvar_3",
        "rowVariableName": "categorical_array",
        "colTitles": [
          "quarter"
        ]
      }
    ],
    "display_settings":{
            "valuesAreMeans": {"value": false},
            "countsOrPercents": {"value": "percent"},
            "percentageDirection": {"value": "colPct"},
            "decimalPlaces": {"value": 1}
        }
    }
    }
