import os
from typing import TypedDict, Annotated, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from schema import UserIntent, Project
from database import save_project, load_projects, delete_project
from langgraph.graph import StateGraph, END

load_dotenv()

# Define graph state
class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    extracted_data: Optional[dict]
    response: str
    
llm = ChatOpenAI(
    model="llama3",  # Make sure you've run: ollama run llama3
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama")
)

def classify_and_extract(state: AgentState) -> AgentState:
    structured_llm = llm.with_structured_output(UserIntent)
    
    prompt = f"""
    Analyze the user input and extract intent and project fields.
    Intents: 'create', 'list', 'delete', 'unclear'.
    Required fields for 'create': project_name, customer.
    If 'create' is intended but 'project_name' or 'customer' is missing, add them to missing_fields.
    
    User input: {state['user_input']}
    """
    
    result: UserIntent = structured_llm.invoke(prompt)
    
    return {
        **state,
        "intent": result.intent,
        "extracted_data": result.model_dump()
    }

def handle_create(state: AgentState) -> AgentState:
    data = state["extracted_data"]
    missing = data.get("missing_fields", [])
    
    if not data.get("project_name"):
        missing.append("project_name")
    if not data.get("customer"):
        missing.append("customer")
        
    missing = list(set(missing))

    if missing:
        fields_str = " and ".join(missing)
        return {**state, "response": f"Please provide the missing information: {fields_str}."}

    project = Project(
        project_name=data["project_name"],
        customer=data["customer"]
    )
    save_project(project.model_dump())
    return {**state, "response": f"Done. Created project \"{project.project_name}\" for customer {project.customer}."}

def handle_list(state: AgentState) -> AgentState:
    projects = load_projects()
    if not projects:
        return {**state, "response": "No projects found."}
    
    out = [f"Here are your projects ({len(projects)}):"]
    for idx, p in enumerate(projects, 1):
        out.append(f"{idx}. {p['project_name']} — customer: {p['customer']}")
    
    return {**state, "response": "\n".join(out)}

def handle_delete(state: AgentState) -> AgentState:
    name = state["extracted_data"].get("project_name")
    if not name:
        return {**state, "response": "Which project name would you like to delete?"}
    
    success = delete_project(name)
    if success:
        return {**state, "response": f"Successfully deleted project '{name}'."}
    return {**state, "response": f"Project '{name}' not found."}

def handle_unclear(state: AgentState) -> AgentState:
    return {**state, "response": "I didn't quite understand that. You can try asking to 'create a project' or 'list projects'."}

def route_intent(state: AgentState) -> str:
    return state.get("intent", "unclear")

# Build LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("classify", classify_and_extract)
workflow.add_node("create", handle_create)
workflow.add_node("list", handle_list)
workflow.add_node("delete", handle_delete)
workflow.add_node("unclear", handle_unclear)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    route_intent,
    {
        "create": "create",
        "list": "list",
        "delete": "delete",
        "unclear": "unclear"
    }
)

workflow.add_edge("create", END)
workflow.add_edge("list", END)
workflow.add_edge("delete", END)
workflow.add_edge("unclear", END)

graph = workflow.compile()