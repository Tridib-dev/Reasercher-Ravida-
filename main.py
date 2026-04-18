from dotenv import load_dotenv
import streamlit as st
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import re
import prompt
from llm_changer import get_llm, MODELS
from datetime import datetime, timedelta


load_dotenv()

if "current_model" not in st.session_state:
    st.session_state.current_model = "⚡ Llama 3.3 70B (Groq)"

if "cooldown" not in st.session_state:
    st.session_state.cooldown = {}

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()


def is_available(model_name):
    cooldown = st.session_state.cooldown.get(model_name)
    if cooldown and datetime.now() < cooldown:
        return False
    return True


def mark_cooldown(model_name, minutes=1):
    st.session_state.cooldown[model_name] = datetime.now() + timedelta(minutes=minutes)


def get_next_available(current_model):
    for name in MODELS.keys():
        if name != current_model and is_available(name):
            return name
    return None


with st.container(horizontal=True):
    col1, col2 = st.columns(2)
    with col2:
        available_models = [m for m in MODELS.keys() if is_available(m)]
        model = st.selectbox(
            label="Models",
            options=available_models,
            index=0,
        )
    with col1:
        col1.title("🤖 Ravida")
        col1.space("stretch")

model_notification = st.empty()


st.space("small")
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.space("stretch")
    c2.subheader("Search Agent")
    c2.space("xxsmall")
    c3.space("stretch")
    #  need to be added special chat mode

llm = get_llm(model)
search = GoogleSerperAPIWrapper()


@tool
def search_google(query: str) -> str:
    """Search Google and return results."""
    return search.run(query)


if st.session_state.current_model != model:
    st.session_state.current_model = model
    st.session_state.agent = create_agent(
        model=get_llm(model),
        tools=[search_google],
        system_prompt=prompt.system_prompt,
        checkpointer=st.session_state.memory,
    )
    model_notification.success(f"✅ Switched to {model}", icon=None)

if "agent" not in st.session_state:
    st.session_state.agent = create_agent(
        model=get_llm(st.session_state.current_model),
        system_prompt=prompt.system_prompt,
        tools=[search_google],
        checkpointer=st.session_state.memory,
    )

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        c1, c2, c3, c4, c5 = st.columns(5)
        c5.caption(msg.get("time", ""))
        if msg.get("links", []):
            st.divider()
            st.caption("🔗 Sources")
            with st.container(height=200):
                for name, url in msg["links"]:
                    st.link_button(f"↗ {name}", url, use_container_width=True)


q = st.chat_input("Ask anything...")

if q:
    st.session_state.history.append({"role": "user", "content": q})
    st.chat_message("user").markdown(q)

    try:
        execution_steps = []
        with st.chat_message("assistant"):
            final_res = ""
            with st.status(
                "🔍 Thinking...", expanded=True
            ) as status:  # ✅ ONCE, outside loop
                for chunk in st.session_state.agent.stream(
                    {"messages": [{"role": "user", "content": q}]},
                    {"configurable": {"thread_id": "main_id"}},
                    stream_mode="messages",
                ):
                    msg = chunk[0]
                    msg_type = type(msg).__name__
                    if (
                        msg_type == "AIMessageChunk"
                        and hasattr(msg, "tool_calls")
                        and msg.tool_calls
                    ):
                        query_used = msg.tool_calls[0].get("args", {}).get("query", "")
                        status.update(label=f"🔎 Searching: {query_used}...")
                        execution_steps.append(f"• 🔎 Searching: {query_used}")

                    elif msg_type == "ToolMessage":
                        status.update(label="📄 Processing results...")
                        if (
                            not execution_steps
                            or "Got search results" not in execution_steps[-1]
                        ):
                            execution_steps.append(
                                "• 📄 Got search results, analyzing..."
                            )

                    elif msg_type == "AIMessageChunk" and msg.content:
                        status.update(label="✍️ Writing answer...")
                        content = msg.content
                        if isinstance(content, list):
                            content = "".join(
                                [
                                    c.get("text", "") if isinstance(c, dict) else str(c)
                                    for c in content
                                ]
                            )
                        final_res += content

                if execution_steps:
                    for step in execution_steps:
                        st.markdown(step)
                else:
                    st.markdown("• Analyzed users prompt")
                    st.markdown("• No tool used for answering")

            # ✅ AFTER loop ends, outside status block
            status.update(label="✅ Done!", state="complete", expanded=False)

            placeholder = st.empty()
            placeholder.markdown(final_res + " ▌")

            clean_res = re.sub(
                r"##\s*🔗\s*Sources.*$", "", final_res, flags=re.DOTALL
            ).strip()
            placeholder.markdown(clean_res)

            time = datetime.now().strftime("%I:%M %p")
            c1, c2, c3, c4, c5 = st.columns(5)
            c5.caption(time)

            links = re.findall(r"\[([^\]]+)\]\((https?://[^\)]+)\)", final_res)
            if links:
                st.divider()
                st.caption("🔗 Sources")
                with st.container(height=200):
                    for name, url in links:
                        st.link_button(f"↗ {name}", url, use_container_width=True)

            st.session_state.history.append(
                {
                    "role": "assistant",
                    "content": clean_res,
                    "links": links,
                    "time": time,
                }
            )

    except Exception as e:
        if "tool_use_failed" in str(e) or "Failed to call a function" in str(e):
            next_model = get_next_available(st.session_state.current_model)
            if next_model:
                mark_cooldown(
                    st.session_state.current_model
                )  # cooldown the failing model
                st.session_state.current_model = next_model
                st.session_state.agent = create_agent(
                    model=get_llm(next_model),
                    tools=[search_google],
                    system_prompt=prompt.system_prompt,
                    checkpointer=MemorySaver(),
                )
                model_notification.warning(
                    f"⚠️ Switched to {next_model}, please resend."
                )
                st.rerun()
            else:
                st.error("❌ All models unavailable. Try again in a moment.")

        elif (
            "429" in str(e)
            or "rate_limit" in str(e).lower()
            or "quota" in str(e).lower()
        ):
            mark_cooldown(st.session_state.current_model)
            next_model = get_next_available(st.session_state.current_model)
            if next_model:
                model_notification.warning(f"⚠️ Rate limited. Switched to {next_model}.")
                st.session_state.current_model = next_model
                st.session_state.agent = create_agent(
                    model=get_llm(next_model),
                    tools=[search_google],
                    system_prompt=prompt.system_prompt,
                    checkpointer=MemorySaver(),
                )
                st.rerun()
            else:
                model_notification.error("⛔ All models rate limited. Wait a minute.")

        else:
            st.error("❌ Something went wrong. Please try again.")
