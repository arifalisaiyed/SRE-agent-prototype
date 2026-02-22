import os
import sys
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
try:
    import asyncore
except ImportError:
    import pyasyncore as asyncore
    sys.modules['asyncore'] = asyncore
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
load_dotenv()
def raw_uptime(server_id):
    return f"Server {server_id} uptime is 145 days."
def raw_history(error_type):
    return f"Last {error_type} was fixed with a service restart."
@tool
def get_server_uptime(server_id: str):
    """Checks server uptime."""
    return raw_uptime(server_id)
@tool
def get_incident_history(error_type: str):
    """Checks incident history."""
    return raw_history(error_type)
tools = [get_server_uptime, get_incident_history]
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
llm_with_tools = llm.bind_tools(tools)
auth_provider = PlainTextAuthProvider(os.getenv('CASSANDRA_USERNAME'), os.getenv('CASSANDRA_PASSWORD'))
cluster = Cluster([os.getenv('CASSANDRA_CONTACT_POINT')], auth_provider=auth_provider)
session = cluster.connect(os.getenv('CASSANDRA_KEYSPACE'))
consumer = KafkaConsumer('system-alerts', bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVER'), security_protocol="SASL_PLAINTEXT", sasl_mechanism="SCRAM-SHA-256", sasl_plain_username=os.getenv('KAFKA_USERNAME'), sasl_plain_password=os.getenv('KAFKA_PASSWORD'), value_deserializer=lambda x: json.loads(x.decode('utf-8')), auto_offset_reset='latest', group_id='sre-agent-v24', consumer_timeout_ms=1000)
print("🤖 SRE Agent Online...")
try:
    while True:
        try:
            message = next(consumer)
            alert = message.value
            print(f"\n[ALERT] {alert['error_type']} on {alert['server_id']}")
            query = f"What is the CLI fix for {alert['error_type']} on {alert['server_id']}? Check uptime first."
            # Direct LLM call bypassing the runnable pipe
            ai_msg = llm_with_tools.invoke([HumanMessage(content=query)])
            ai_fix = ""
            if ai_msg.tool_calls:
                obs_list = []
                for call in ai_msg.tool_calls:
                    name = call["name"]
                    args = call["args"]
                    print(f"🛠️ Executing: {name}")
                    if name == "get_server_uptime":
                        obs_list.append(raw_uptime(args.get("server_id", alert["server_id"])))
                    elif name == "get_incident_history":
                        obs_list.append(raw_history(args.get("error_type", alert["error_type"])))
                context = "|".join(obs_list)
                final_res = llm.invoke(f"Context: {context}\n\nFix this: {query}\n\nCLI Fix ONLY:")
                ai_fix = final_res.content
            else:
                ai_fix = ai_msg.content
            print(f"🤖 AI Suggestion: {ai_fix}")
            query_save = "INSERT INTO error_logs (server_id, error_type, fix_suggestion, log_time) VALUES (%s, %s, %s, toTimestamp(now()))"
            session.execute(query_save, (alert['server_id'], alert['error_type'], ai_fix))
            print("💾 Saved to database!")
        except StopIteration: continue
        except Exception as e:
            print(f"⚠️ Process Error: {e}")
except KeyboardInterrupt:
    print("\n👋 Shutting down gracefully...")
finally:
    consumer.close()
    cluster.shutdown()