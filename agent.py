import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
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

# Provider-agnostic LLM Initialization
llm_model = os.getenv("LLM_MODEL", "llama3")
api_key = os.getenv("OPENAI_API_KEY", "ollama")
base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

llm_kwargs = {
    "model": llm_model,
    "temperature": 0,
    "api_key": api_key,
}

if base_url:
    llm_kwargs["base_url"] = base_url

llm = ChatOpenAI(**llm_kwargs)


def classify_and_extract(state: AgentState) -> AgentState:
    structured_llm = llm.with_structured_output(UserIntent)
    
    prompt = f"""
    Analyze the user input and extract intent and all matching project fields.
    
    Field Requirements:
    - Mandatory: project_name, customer
    - Optional: start_date, location, notes, status
    
    Supported Intents: 'create', 'list', 'delete', 'unclear'.
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
    data = state["extracted_data"] or {}
    missing = data.get("missing_fields") or []
    
    if not data.get("project_name"):
        missing.append("project_name")
    if not data.get("customer"):
        missing.append("customer")
        
    missing = list(set(missing))

    if missing:
        fields_str = " and ".join(missing)
        return {**state, "response": f"Please provide the missing information: {fields_str}."}

    # Construct Pydantic model passing mandatory + optional fields
    project = Project(
        project_name=data["project_name"],
        customer=data["customer"],
        start_date=data.get("start_date"),
        location=data.get("location"),
        status=data.get("status") or "Active",
        notes=data.get("notes")
    )
    save_project(project.model_dump())

    # Format response including optional metadata
    details = []
    if project.start_date:
        details.append(f"Start: {project.start_date}")
    if project.location:
        details.append(f"Location: {project.location}")
    if project.notes:
        details.append(f"Notes: {project.notes}")
    
    extra_str = f" ({', '.join(details)})" if details else ""
    return {**state, "response": f"Done. Created project \"{project.project_name}\" for customer {project.customer}{extra_str}."}


def handle_list(state: AgentState) -> AgentState:
    projects = load_projects()
    if not projects:
        return {**state, "response": "No projects found."}
    
    out = [f"Here are your projects ({len(projects)}):"]
    for idx, p in enumerate(projects, 1):
        details = []
        if p.get("start_date"):
            details.append(f"Start: {p['start_date']}")
        if p.get("location"):
            details.append(f"Location: {p['location']}")
        if p.get("status"):
            details.append(f"Status: {p['status']}")
        
        detail_str = f" | {', '.join(details)}" if details else ""
        out.append(f"{idx}. {p['project_name']} — customer: {p['customer']}{detail_str}")
    
    return {**state, "response": "\n".join(out)}


def handle_delete(state: AgentState) -> AgentState:
    data = state["extracted_data"] or {}
    name = data.get("project_name")
    if not name:
        return {**state, "response": "Which project name would you like to delete?"}
    
    success = delete_project(name)
    if success:
        return {**state, "response": f"Successfully deleted project '{name}'."}
    return {**state, "response": f"Project '{name}' not found."}


def handle_unclear(state: AgentState) -> AgentState:
    return {**state, "response": "I didn't quite understand that. You can try asking to 'create a project', 'list projects', or 'delete project'."}


def route_intent(state: AgentState) -> str:
    return state.get("intent") or "unclear"


# Build LangGraph workflow
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