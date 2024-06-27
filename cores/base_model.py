import datetime
import decimal
import random
import time

import sqlalchemy
from loguru import logger
from sqlalchemy import DATETIME, DECIMAL, INTEGER, Column, DateTime, Integer, distinct, func, desc

#
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select, update, delete
from app.extensions.db_extras import get_db_session_async

# from app.extensions.database import db

# 创建基类
BaseModel = declarative_base()


class MixinFields:
    """公共字段"""

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created = Column(DateTime, nullable=True, index=True, default=func.now(), comment="添加数据时间")
    updated = Column(
        DateTime, nullable=True, index=True, default=func.now(), onupdate=func.now(), comment="修改数据时间"
    )


class MixinFunctions:

    @classmethod
    async def find_or_create_async(cls, unique_index_fields=[], **kwargs):
        async with get_db_session_async() as session:
            # 如果没有传入唯一索引字段，从表结构中提取
            if not unique_index_fields:
                # 从表结构中提取出唯一索引字段
                unique_index_fields = [column.name for column in cls.__table__.columns if column.unique]
            if not unique_index_fields:
                # 从表结构中提取主键
                unique_index_fields = [column.name for column in cls.__table__.primary_key.columns]

            # 用取出的唯一索引字段, 从kwargs中提取查询条件
            filter_kwargs = {k: v for k, v in kwargs.items() if k in unique_index_fields}
            filters = [getattr(cls, k) == v for k, v in filter_kwargs.items()]
            query = select(cls).where(*filters)
            result_set = await session.execute(query)

            row = result_set.first()
            # logger.debug(row)

            if row is None:
                row = await cls.create_at_async(**kwargs)
            else:
                row = cls.to_dict(row[0])
            return row

    @classmethod
    async def create_at_async(cls, commit_now=True, **kwargs):
        from sqlalchemy import insert

        async with get_db_session_async() as session:
            query = insert(cls).values(kwargs)
            resultset = await session.execute(query)
            await session.commit()
            pk = resultset.inserted_primary_key[0]
            result_set = await session.get(cls, pk)
            logger.debug(result_set)
            row = cls.to_dict(result_set)
            return row

    @classmethod
    def validate_fields(cls, declude_id: bool = True, **kwargs) -> dict:
        """更新字段校验

        校验字段是否在表中，以及是否要从更新字段中剔除主键

        Args:
            up_fields (dict): 待更新字段
            declude_id (bool, optional): 是否要剔除主键. Defaults to True.

        Returns:
            dict: 新的待更新字段
        """
        new_fields = {}
        for k, v in kwargs.items():
            if k in cls.__table__.columns:
                new_fields[k] = v
        pk_name = cls.__table__.primary_key.columns[0].name
        if pk_name in new_fields and declude_id:
            del new_fields[pk_name]

        return new_fields

    @classmethod
    async def update_by_async(cls, *conditions, commit_now=True, db_instance=None, **kwargs):
        """按条件更新

        args:
            *conditions: 更新条件，必填
            commit_now: 是否立即提交更新，选填，默认立即提交
            **kwargs: 更新字段，必填

        example:
            1. 按主键更新
            User.update_by(User.id == 1, username='test')

            2. 按条件更新
            User.update_by(User.username == 'test', username='test2')

            3. 按多条件更新
            User.update_by(User.id == 1, User.username == 'test', username='test2')

            4. 按多个条件更新，其中有些条件是或
            from sqlalchemy import or_
            User.update_by(
                # 条件
                User.id == 1,
                or_(User.username == 'test', User.username == 'test2'),
                # 更新
                username='test3')

            5. 复杂条件可以先用list进行组合
            from sqlalchemy import or_
            # 先组合条件
            filters = []
            filters.append(User.id == 1)
            filters.append(or_(User.username == 'test', User.username == 'test2'))
            filters.append(User.updated <= '2020-01-01')
            # 然后再更新
            User.update_by(*filters, username='test3')

        """
        async with get_db_session_async() as session:
            kwargs = cls.validate_fields(**kwargs)
            query = update(cls).where(*conditions).values(kwargs)
            result_set = await session.execute(query)
            await session.commit()
            affected = result_set.rowcount
            return affected

    @classmethod
    async def count_async(cls, *filters, distinct_field=None):
        async with get_db_session_async() as session:
            if distinct_field:
                query = select(func.count(distinct(getattr(cls, distinct_field))))
            else:
                pk = cls.__table__.primary_key.columns[0].name
                query = select(func.count(getattr(cls, pk)))

            if filters:
                query = query.where(*filters)
            result_set = await session.execute(query)
            count = result_set.scalar()
            return count

    @classmethod
    async def get_by_async(cls, *conditions):
        return await cls.get_all_async(*conditions, single=True)

    @classmethod
    async def delete_all_async(cls, *conditions):
        async with get_db_session_async() as session:
            query = delete(cls)
            if conditions:
                query = query.where(*conditions)
                result_set = await session.execute(query)
                await session.commit()
                return result_set.rowcount

    @classmethod
    async def get_all_async(cls, *conditions, single=False, limit=None, offset=None, order_by=None):
        async with get_db_session_async() as session:

            query = select(cls)
            if conditions:
                query = query.where(*conditions)

            if order_by is not None:
                if isinstance(order_by, list):
                    query = query.order_by(*order_by)
                else:
                    query = query.order_by(order_by)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result_set = await session.execute(query)
            if single:
                row = result_set.first()
                if row:
                    return cls.to_dict(row[0])
                else:
                    return None
            rows = result_set.all()
            return [cls.to_dict(row[0]) for row in rows]

    @classmethod
    def to_dict(
        cls,
        result_obj,
        include: list = None,
        exclude: list = None,
        handle_none: bool = True,
        debug: bool = False,
    ):
        """将对象转换为字典

        Args:
            result_obj (_type_): 传入对象
            include (_type_, optional): _description_. Defaults to None.
            exclude (_type_, optional): _description_. Defaults to None.
            handle_none (bool, optional): _description_. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        tmp_dict = {}
        # logger.debug(type(result_obj))
        # logger.debug(dict(zip(result_obj.keys(), result_obj)))
        # 判断是否是查询结果对象
        if isinstance(result_obj, sqlalchemy.engine.row.Row):
            result_obj = result_obj._asdict()

        keys = cls.__table__.columns.keys() if isinstance(result_obj, BaseModel) else result_obj.keys()
        for key in keys:
            value = getattr(result_obj, key) if isinstance(result_obj, BaseModel) else result_obj[key]

            if include and key not in include:
                if debug:
                    logger.debug(key)
                continue

            if exclude and key in exclude:
                continue

            if value is None and handle_none:
                # 判断是否是查询结果对象
                if isinstance(result_obj, BaseModel):
                    column_type = cls.__table__.columns[key].type
                    if isinstance(column_type, (INTEGER,)):
                        tmp_dict[key] = 0
                    elif isinstance(column_type, (DECIMAL,)):
                        tmp_dict[key] = 0.0
                    elif isinstance(column_type, (DATETIME,)):
                        tmp_dict[key] = None
                    else:
                        tmp_dict[key] = None
                else:
                    tmp_dict[key] = None  # 或者设置一个通用的默认值
            elif isinstance(value, decimal.Decimal):
                tmp_dict[key] = float(value)
            elif isinstance(value, datetime.datetime):
                tmp_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                tmp_dict[key] = value

            if debug:
                logger.debug(key)

        return tmp_dict

    @classmethod
    async def upsert_async(
        cls, records, batch_size=1000, commit_on_chunk=True, update_keys=['id'], exclude_keys=[], run_update=True
    ):
        if not records:
            return
        from sqlalchemy.dialects.mysql import insert

        async with get_db_session_async() as session:
            # 根据输入内容决定要更新的字段（否则会覆盖不需要更新的字段）
            include_keys = records[0].keys()

            # 新版本改成下面这样这样写，否则会报错
            for i in range(0, len(records), batch_size):
                batch_records = records[i : i + batch_size]
                ed = i + batch_size - 1
                if i + batch_size > len(records):
                    ed = len(records)
                logger.info(f'正在写入数据 {i} - {ed}')

                # 这里要注意insert方法的import位置，否则insert_stmt会报错
                # 正确的位置：from sqlalchemy.dialects.mysql import insert
                # insert_stmt = insert(cls).values(record)
                insert_stmt = insert(cls).values(batch_records)

                # 更新条件
                # 字段不是查询条件（主键，或唯一索引字段）
                # 且，字段不在排除列表内
                # 且，字段必须在records的keys范围内
                update_columns = {
                    x.name: x
                    for x in insert_stmt.inserted
                    if x.name not in update_keys and x.name not in exclude_keys and x.name in include_keys
                }

                if run_update:
                    # 主键/唯一键重复时，更新指定字段取值（覆盖）
                    # 该方法只有在出现 duplicate key 异常时才会生效
                    # 默认是ID重复
                    # 若需要按多字段组合唯一，需要给表增加唯一索引才会生效，否则会插入重复记录
                    upsert_stmt = insert_stmt.on_duplicate_key_update(**update_columns)
                else:
                    # 主键/唯一键重复时，忽略记录（不覆盖）
                    upsert_stmt = insert_stmt.on_duplicate_key_update(id=cls.id)

                await session.execute(upsert_stmt)
                if commit_on_chunk:
                    await session.commit()
                    # await session.expire_all()
            # 因为关闭了commit自动清理，这里需要自己手动清理
            await session.commit()
            # await session.expire_all()
