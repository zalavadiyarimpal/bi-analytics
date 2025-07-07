from sqlalchemy import select, text, func, and_
from backend.db_connector import get_engine_select, reflect_tables


def build_query(validated):
    engine = get_engine_select(validated["data_source"]["connection_id"])
    metadata = reflect_tables(engine)
    main_table = metadata.tables[validated["data_source"]["table"]]


    # Joins
    join_tables = {}
    for join in validated["data_source"].get("joins", []):
        join_table = metadata.tables[join["table"]]
        join_tables[join["table"]] = join_table
        main_table = main_table.join(join_table, text(" AND ".join(join["on"])), isouter=(join["type"] == "left"))

    # SELECT fields
    select_cols = []
    for axis in ["rows", "columns","measures"]:
        for col in validated["dimensions"].get(axis, []):
            # print(col)
            # continue
            if all(k in col for k in ['type', 'field', 'alias']):
                if col['type'] == "column":                    
                    select_cols.append(text(f"{col['field']} AS {col['alias']}"))  # e.g., "countries.name AS country"
                if col['type'] == "agg":                    
                    agg_func = getattr(func, col["agg"])
                    select_cols.append(agg_func(text(col["field"])).label(col["alias"]))
                # if col['type'] == "expr": 
                #     select_cols.append(text(f"{calc['field']} AS {calc['alias']}"))
   
    query = select(*select_cols).select_from(main_table)

    # WHERE filters
    filters = []
    for field, f in validated.get("filters", {}).items():
        op = f["operator"]
        value = f["value"]

        if op == "between":
            filters.append(text(f"{field} BETWEEN '{value[0]}' AND '{value[1]}'"))
        elif op == "in":
            in_values = ",".join(f"'{v}'" for v in value)
            filters.append(text(f"{field} IN ({in_values})"))
        else:
            filters.append(text(f"{field} {op} '{value}'"))

    if filters:
        query = query.where(and_(*filters))

    # GROUP BY
    if "group_by" in validated:
        group_fields = [text(col) for col in validated["group_by"]]
        query = query.group_by(*group_fields)

    # SORT BY
    for sort in validated.get("sort_by", []):
        field = sort["field"]
        direction = sort["order"].upper()
        query = query.order_by(text(f"{field} {direction}"))

    # LIMIT
    if "limit" in validated:
        query = query.limit(validated["limit"])

    return query, engine
   
