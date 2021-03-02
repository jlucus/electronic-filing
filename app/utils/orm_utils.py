import traceback
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
from app.utils.dict_utils import (
    get_value_at_path,
    map_keys,
)
from app.utils.string_utils import (
    is_str,
    is_float,
    is_int,
    is_bool,
    is_date,
    is_uuid,
    to_date,
    to_float2,
    to_bool,
)


# database utility helper

def get_row_by_key_value(db_session, model, key, value):
    try:
        filter_attr = getattr(model, key)
        row = db_session.execute(
            select(model)
            .filter(filter_attr == value)
        ).first()
        return row[0] if row is not None else None
    except:
        return None


def add_table_row(db_session, model, **key_values):
    row = model(**key_values)
    try:
        db_session.add(row)
        db_session.commit()
        db_session.refresh(row)
        return row
    except Exception as inst:
        print(
            f'failed to create "{model.__tablename__}" record', traceback.format_exc()
        )


def upsert_table_row(db_session, model, pk_name, **key_values):
    row = model(**key_values)
    pk_value = key_values.get(pk_name)
    try:
        current_row = get_row_by_key_value(db_session, model, pk_name, pk_value)
        if current_row is None:
            db_session.add(row)
        else:
            row = db_session.merge(row)

        db_session.commit()
        db_session.flush()
        db_session.refresh(row)
        return row
    except Exception as inst:
        print(
            f'failed to create "{model.__tablename__}" record', traceback.format_exc()
        )


# dictionary to table mapping helpers

# POSTGRESQL DATA TYPES
orm_type_mappings = {
    "UUID": (is_uuid, str),
    "VARCHAR": (is_str, str),
    "INTEGER": (is_int, str),
    "BOOLEAN": (is_bool, to_bool),
    "DATE": (is_date, to_date),
    "NUMERIC": (is_float, to_float2),
}


def json_to_orm_mapper(model, path: list = [], map_pks=False):
    # create row mapping
    map = {}
    for col in model.__table__.columns:
        if col.primary_key and map_pks == False:
            # don't map primary keys
            continue
        col_type = str(col.type)
        col_name = str(col.name)
        map_tuple = orm_type_mappings.get(col_type, ())

        # handle key name mapping
        if "name_map" in dir(model) and model.name_map.get(col_name, False):
            input_name = model.name_map.get(col_name, None)
            map_tuple = (*map_tuple, col_name)
            col_name = input_name

        map.update({col_name: map_tuple})

    # handle path
    if path == [] and "path" in dir(model):
        path = model.path

    mapper = {
        "model": model,
        "map": map,
        "path": path,
    }

    return mapper


# Injective mapping between a dictionary and a database model


class TableMapper:
    def __init__(self, db_session, data: dict):
        self.__db_session = db_session
        self.__data = data

    def __add_table_row(self, model, coldata: dict):
        pkname = [col.name for col in model.__table__.columns if col.primary_key][0]
        pkvalue = coldata.get(pkname)
        new_row = model(**coldata)
        current_row = get_row_by_key_value(self.__db_session, model, pkname, pkvalue) if pkvalue else None
        if current_row is None:
            self.__db_session.add(new_row)
            self.__db_session.commit()
            self.__db_session.flush()
            self.__db_session.refresh(new_row)
            return new_row
        else:
            new_row = self.__db_session.merge(new_row)
            self.__db_session.commit()
            self.__db_session.flush()
            self.__db_session.refresh(new_row)
            return new_row

    def __add_mapped_table_row(self, model, path, map, **foreign_keys):
        # 1. get dict at path
        sub_tree = get_value_at_path(self.__data, path)
        if sub_tree == None:
            return None

        if isinstance(sub_tree, list):
            print(f"FAILED ON: sub_tree is of type list")
            return None

        # 2. map key values
        mapped_dict = map_keys(map, sub_tree)
        mapped_dict.update(foreign_keys)

        # 3. add row to database table and return return primary key (id)
        return self.__add_table_row(model, mapped_dict)

    def add_row(self, mapper, **foreign_keys):
        # 0. destructure the mapper
        model = mapper.get("model", None)
        path = mapper.get("path", None)
        map = mapper.get("map", {})
        if path == None or len(map) == 0 or model == None:
            return None

        return self.__add_mapped_table_row(model, path, map, **foreign_keys)

    def add_rows(self, mapper, **foreign_keys):
        # 0. destructure the mapper
        model = mapper.get("model", None)
        path = mapper.get("path", None)
        map = mapper.get("map", {})
        if path == None or len(map) == 0 or model == None:
            return None

        rows = []

        # get value(s) at path
        sub_tree = get_value_at_path(self.__data, path)

        # case: a single item at path
        if not isinstance(sub_tree, list):
            row = self.__add_mapped_table_row(model, path, map, **foreign_keys)
            if row != None:
                rows.append(row)
            return rows

        # case: an array of items at path
        item_count = len(sub_tree)
        for i in range(item_count):
            item_path = path + [f"[{i}]"]
            row = self.__add_mapped_table_row(model, item_path, map, **foreign_keys)
            if row != None:
                rows.append(row)

        return rows
