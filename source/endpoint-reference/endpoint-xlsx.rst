Xlsx
----

The ``xlsx`` endpoint takes as input a prepared table (intended for use
with multitables) and returns an xlsx file, with some basic formatting
conventions.

A POST request to ``/api/xlsx/`` will return an xlsx file directly, with
correct content-disposition and type headers.

POST
^^^^

.. language_specific::
   --HTTP
   .. code:: http

      POST /api/xlsx/ HTTP/1.1


--------------

.. language_specific::
   --HTTP
   .. code:: http

      HTTP/1.1 200 OK
      Content-Disposition: attachment; filename=Crunch-export.xlsx
      Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

   --JSON
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

+---------+-------+---------------------------------------------+--------------+
| Name    | Type  | Typical                                     | Description  |
|         |       | element                                     |              |
+=========+=======+=============================================+==============+
| rows    | array | ``{"value": 30, "class": "formatted"}``     | Cells are    |
|         |       |                                             | objects with |
|         |       |                                             | at least a   |
|         |       |                                             | ``value``    |
|         |       |                                             | member, and  |
|         |       |                                             | optional     |
|         |       |                                             | ``class``,   |
|         |       |                                             | where a      |
|         |       |                                             | value of     |
|         |       |                                             | ``"formatted |
|         |       |                                             | "``          |
|         |       |                                             | prevents the |
|         |       |                                             | exporter     |
|         |       |                                             | from         |
|         |       |                                             | applying any |
|         |       |                                             | number       |
|         |       |                                             | format to    |
|         |       |                                             | the result   |
|         |       |                                             | cell         |
+---------+-------+---------------------------------------------+--------------+
| colLabe | array | ``{"value": "All"}``                        | Array of     |
| ls      |       |                                             | objects with |
|         |       |                                             | a ``value``  |
|         |       |                                             | member       |
+---------+-------+---------------------------------------------+--------------+
| colTitl | array | ``"Age"``                                   | Array of     |
| es      |       |                                             | strings      |
+---------+-------+---------------------------------------------+--------------+
| spans   | array | ``4``                                       | array of     |
|         |       |                                             | integers     |
|         |       |                                             | matching the |
|         |       |                                             | length of    |
|         |       |                                             | colTitles,   |
|         |       |                                             | indicating   |
|         |       |                                             | the number   |
|         |       |                                             | of cells to  |
|         |       |                                             | be joined    |
|         |       |                                             | for each     |
|         |       |                                             | colTitle     |
|         |       |                                             | after the    |
|         |       |                                             | first one.   |
|         |       |                                             | The first    |
|         |       |                                             | colTitle is  |
|         |       |                                             | assumed to   |
|         |       |                                             | be only one  |
|         |       |                                             | column wide. |
+---------+-------+---------------------------------------------+--------------+
| rowTitl | strin | ``"Dog food brands"``                       | A title,     |
| e       | g     |                                             | which is     |
|         |       |                                             | formatted    |
|         |       |                                             | bold above   |
|         |       |                                             | the first    |
|         |       |                                             | column of    |
|         |       |                                             | the table    |
|         |       |                                             | (the         |
|         |       |                                             | rowLabels,   |
|         |       |                                             | below)       |
+---------+-------+---------------------------------------------+--------------+
| rowLabe | array | ``{"value": "Canine Crunch"}``              | labels for   |
| ls      |       |                                             | rows of the  |
|         |       |                                             | table        |
|         |       |                                             |              |
+---------+-------+---------------------------------------------+--------------+
| rowVari | strin | ``"Preferred dog food"``                    | title to     |
| ableNam | g     |                                             | display at   |
| e       |       |                                             | the very top |
|         |       |                                             | left of the  |
|         |       |                                             | result sheet |
+---------+-------+---------------------------------------------+--------------+
| filter\ | array | ``"Breed: Dachshund"``                      | Names of any |
| _names  |       |                                             | filters to   |
|         |       |                                             | print        |
|         |       |                                             | beneath the  |
|         |       |                                             | table, will  |
|         |       |                                             | be labeled   |
|         |       |                                             | "Filters".   |
|         |       |                                             | If multiple  |
|         |       |                                             | result       |
|         |       |                                             | objects are  |
|         |       |                                             | included in  |
|         |       |                                             | the payload, |
|         |       |                                             | the filter   |
|         |       |                                             | names from   |
|         |       |                                             | the *first*  |
|         |       |                                             | result are   |
|         |       |                                             | used, and    |
|         |       |                                             | placed at    |
|         |       |                                             | the bottom   |
|         |       |                                             | of the sheet |
|         |       |                                             | beneath all  |
|         |       |                                             | results.     |
+---------+-------+---------------------------------------------+--------------+

Display Settings
''''''''''''''''

Further customization for the resulting output.

+---------+-------+----------+--------------+-------------------------------+
| Name    | Type  | Default  | Description  | Example                       |
+=========+=======+==========+==============+===============================+
| decimal | objec | 0        | number of    | ``{"value": 0}``              |
| Places  | t     |          | decimal      |                               |
|         |       |          | places to    |                               |
|         |       |          | diaplay      |                               |
+---------+-------+----------+--------------+-------------------------------+
| countsO | objec | percent  | use counts   | ``{"value": "percent"}``      |
| rPercen | t     |          | or percents  |                               |
| ts      |       |          |              |                               |
+---------+-------+----------+--------------+-------------------------------+
| percent | objec | {"value" | row or       | ``{"value": "colPct"}``       |
| ageDire | t     | :        | column based |                               |
| ction   |       | "colPct" | percents     |                               |
|         |       | }        |              |                               |
+---------+-------+----------+--------------+-------------------------------+
| valuesA | objec | false    | are values   | ``{"value": false}``          |
| reMeans | t     |          | means? (If   |                               |
|         |       |          | so, will be  |                               |
|         |       |          | formatted    |                               |
|         |       |          | with decimal |                               |
|         |       |          | places)      |                               |
+---------+-------+----------+--------------+-------------------------------+

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

