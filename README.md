# Databricks App Templates

Pre-built templates for creating [Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/).

See [Create an App from a Template](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/create-app-template) to get started.

## Templates

### Hello World

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `streamlit-hello-world-app` | Simple Streamlit app | None |
| `dash-hello-world-app` | Simple Dash app | None |
| `gradio-hello-world-app` | Simple Gradio app | None |
| `shiny-hello-world-app` | Simple Shiny app | None |
| `flask-hello-world-app` | Simple Flask app | None |
| `nodejs-fastapi-hello-world-app` | Simple Node.js app | None |

### Agents

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `agent-langgraph` | A conversational agent using LangGraph and MLflow AgentServer | MLflow experiment |
| `agent-langgraph-advanced` | LangGraph agent with short-term memory, long-term memory, and long-running background tasks | MLflow experiment, Database |
| `agent-openai-agents-sdk` | A conversational agent using OpenAI Agents SDK and MLflow AgentServer | MLflow experiment |
| `agent-openai-advanced` | OpenAI Agents SDK agent with short-term memory and long-running background tasks | MLflow experiment, Database |
| `agent-openai-agents-sdk-multiagent` | Multi-agent orchestrator using OpenAI Agents SDK with Genie and serving endpoint subagents | MLflow experiment |
| `agent-non-conversational` | A non-conversational agent that processes structured questions and provides answers with detailed reasoning | MLflow experiment |
| `agent-migration-from-model-serving` | Template for migrating a ResponsesAgent from Model Serving to Databricks Apps | MLflow experiment |
| `e2e-chatbot-app-next` | A chat UI that queries a remote agent endpoint or foundation model | Serving endpoint |
| `mcp-server-hello-world` | A basic MCP server | None |
| `mcp-server-open-api-spec` | An MCP server that exposes REST API operations from an OpenAPI specification stored in a Unity Catalog volume | UC volume |

### Dashboard

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `streamlit-data-app` | An app that reads from a SQL warehouse and visualizes data | SQL warehouse |
| `dash-data-app` | An app that reads from a SQL warehouse and visualizes data | SQL warehouse |
| `gradio-data-app` | An app that reads from a SQL warehouse and visualizes data | SQL warehouse |
| `shiny-data-app` | An app that reads from a SQL warehouse and visualizes data | SQL warehouse |

### Database

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `streamlit-database-app` | A todo app that stores tasks in a Postgres database hosted on Databricks | Database |
| `dash-database-app` | A todo app that stores tasks in a Postgres database hosted on Databricks | Database |
| `flask-database-app` | A todo app that stores tasks in a Postgres database hosted on Databricks | Database |

### AppKit

A collection of templates for building full-stack Databricks Apps with [AppKit](https://github.com/databricks/appkit).

<!-- appkit-start -->

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `appkit-all-in-one` | Full-stack Node.js app with SQL analytics dashboards, file browser, Genie AI conversations, Lakebase Autoscaling (Postgres) CRUD, and Model Serving | SQL warehouse, Volume, Genie Space, Database, Serving Endpoint |
| `appkit-analytics` | Node.js app with SQL analytics dashboards and charts | SQL warehouse |
| `appkit-genie` | Node.js app with AI/BI Genie for natural language data queries | Genie Space |
| `appkit-files` | Node.js app with file browser for Databricks Volumes | Volume |
| `appkit-serving` | Node.js app with Databricks Model Serving endpoint integration | Serving Endpoint |
| `appkit-lakebase` | Node.js app with Lakebase Autoscaling (Postgres) CRUD operations | Database |

<!-- appkit-end -->

### Showcase Examples

End-to-end example apps that bundle a full Databricks App with seed data, SQL queries, and (where applicable) Lakeflow pipelines and provisioning scripts. See each template's `README.md` for the runbook.

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `agentic-support-console` | End-to-end AI-powered support console combining Lakebase, Lakehouse Sync, a medallion pipeline, an LLM agent job, reverse sync, and a Databricks App with Genie analytics. | SQL warehouse, Database, Genie Space, MLflow experiment |
| `content-moderator` | Internal content moderation tool with per-channel guidelines, AI-powered compliance scoring via Model Serving, and a moderator review workflow backed by Lakebase and Genie analytics. | SQL warehouse, Database, Genie Space, Serving endpoint |
| `inventory-intelligence` | Retail inventory management with AI-powered demand forecasting, replenishment recommendations, and optional Genie analytics. Built on a live medallion pipeline synced to Lakebase. | SQL warehouse, Database, Genie Space |
| `rag-chat` | Streaming Retrieval-Augmented Generation chat app with pgvector retrieval from Lakebase, Wikipedia seed corpus, Model Serving generation, and Lakebase-backed chat history. Consumed via `databricks apps init`. | Database, Serving endpoint |
| `saas-tracker` | Internal tool for tracking team SaaS subscriptions, owners, costs, and renewals with Lakebase persistence and Genie spend analytics. | SQL warehouse, Database, Genie Space |
| `vacation-rentals` | Vacation rental ops dashboard with revenue analytics from a SQL Warehouse, a booking queue with Lakebase-backed flags and agent notes, and an embedded Genie chat panel. | SQL warehouse, Database, Genie Space |

# DatabricksHackathonChallenge

Claude was used to create a master plan to help with timing and splitting up work between the team. The plan was followed loosely and used as a guideline to understand what tasks needed to be done. Here is the link to the plan: https://claude.ai/artifact/MNqeRcLEiRUUkHLWVc1e5i

Claude was also used to generate code to download the data from the website, https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/#files-panel, into Databricks. Here is the code that was generated: 

    import os, requests
    
    spark.sql("CREATE VOLUME IF NOT EXISTS workspace.default.glycemic_raw")
    
    BASE = "https://physionet.org/files/big-ideas-glycemic-wearable/1.1.3"
    DEST = "/Volumes/workspace/default/glycemic_raw"
    PID = "001"
    
    FILES = [
        f"Dexcom_{PID}.csv",
        f"Food_Log_{PID}.csv",
        f"HR_{PID}.csv",
        f"IBI_{PID}.csv",
        f"TEMP_{PID}.csv",
        f"EDA_{PID}.csv",
        f"ACC_{PID}.csv",   # ~838 MB
        f"BVP_{PID}.csv",   # ~1.3 GB
    ]
    
    def fetch(url, path):
        # Skip files that are already complete
        head = requests.head(url, timeout=60, allow_redirects=True)
        size = int(head.headers.get("Content-Length", 0))
        if size and os.path.exists(path) and os.path.getsize(path) == size:
            print(f"Already have {os.path.basename(path)}, skipping")
            return

    tmp = path + ".part"
    done = 0
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as out:
            for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                out.write(chunk)
                done += len(chunk)
                if size:
                    print(f"\r{os.path.basename(path)}: {done/1e6:,.0f} / {size/1e6:,.0f} MB", end="")
    os.replace(tmp, path)
    print(f"\nSaved {os.path.basename(path)}")

    # Shared file for all participants
    fetch(f"{BASE}/Demographics.csv", f"{DEST}/Demographics.csv")
    
    # Everything for participant 001
    os.makedirs(f"{DEST}/{PID}", exist_ok=True)
    for name in FILES:
        fetch(f"{BASE}/{PID}/{name}", f"{DEST}/{PID}/{name}")
    
    print("\nDone. Files in volume:")
    for f in sorted(os.listdir(f"{DEST}/{PID}")):
        print(f"  {f}: {os.path.getsize(f'{DEST}/{PID}/{f}')/1e6:,.1f} MB")

Used the following link to figure out how to style text in python uing html and inline css styling:
https://stackoverflow.com/questions/70932538/how-to-center-the-title-and-an-image-in-streamlit
