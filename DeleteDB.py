import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

 #--- Load Environment Variables ---
load_dotenv()

 #--- Connect to Cassandra ---
try:
    auth_provider = PlainTextAuthProvider(
        os.getenv('CASSANDRA_USERNAME'), 
        os.getenv('CASSANDRA_PASSWORD')
    )
    cluster = Cluster([os.getenv('CASSANDRA_CONTACT_POINT')], auth_provider=auth_provider)
    session = cluster.connect(os.getenv('CASSANDRA_KEYSPACE'))

    print(f"🧹 Connected to keyspace: {os.getenv('CASSANDRA_KEYSPACE')}")

    print("⚠️ Deleting all records from error_logs...")

     #Using TRUNCATE is the SRE way to wipe a table instantly
    session.execute("TRUNCATE error_logs")

    print("✅ Database cleared successfully!")

except Exception as e:
    print(f"❌ Failed to clear database: {e}")