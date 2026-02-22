import sys
import types
try:
    import asyncore
except ImportError:
    import pyasyncore as asyncore
    sys.modules['asyncore'] = asyncore
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv
load_dotenv()
print("🔍 Connecting to Cassandra...")
try:
    auth_provider = PlainTextAuthProvider(
        username=os.getenv('CASSANDRA_USERNAME'),
        password=os.getenv('CASSANDRA_PASSWORD')
    )
    cluster = Cluster([os.getenv('CASSANDRA_CONTACT_POINT')], auth_provider=auth_provider)
    session = cluster.connect(os.getenv('CASSANDRA_KEYSPACE'))
    query = "SELECT server_id, error_type, log_time FROM error_logs LIMIT 20;"
    rows = session.execute(query)
    print("\n" + "="*85)
    print(f"{'TIMESTAMP':<30} | {'SERVER':<15} | {'ERROR TYPE':<20}")
    print("-" * 85)
    count = 0
    for row in rows:
        print(f"{str(row.log_time):<30} | {row.server_id:<15} | {row.error_type:<20}")
        count += 1
    print("="*85)
    print(f"✅ Total Records Found: {count}")
except Exception as e:
    print(f"❌ Error: {e}")