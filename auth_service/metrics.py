from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy import event
import time

total_login_attempts=Counter("total_login_attempts","Total Login Attempts",["result"])
refresh_token_attempts = Counter("refresh_token_attempts","Total Number of refresh tokens attempted/issued",
                                 ["result"])

active_connections = Gauge("active_connections","Total Number of Connections Active")
db_query_duration = Histogram("db_query_duration","Time spent on database queries",)
db_active_queries = Gauge('db_active_queries',
        'Total number of database queries currently executing')

def register_db_metrics(engine):
        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(conn,*args):
                conn.info["query_start_time"] = time.perf_counter()


        @event.listens_for(engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(conn,*args):
                start = conn.info.pop("query_start_time", None)

                if start is not None:
                        db_query_duration.observe(time.perf_counter() - start)

        @event.listens_for(engine.sync_engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
                active_connections.inc()


        @event.listens_for(engine.sync_engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
                active_connections.dec()