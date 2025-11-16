# -*- coding: utf-8 -*-
# @Time : 2025/11/15 13:36
# @Author : Marcial
# @Project: LangGraph+AgentScope
# @File : workflows.py
# @Software: PyCharm

from langgraph.graph import StateGraph, END
from


def build_workflow():

    writer = create_writer_agent()

    def write_content(state):
        prompt = state["prompt"]
        result = writer.run(prompt)
        return {"result": result}

    workflow = StateGraph(dict)
    workflow.add_node("writer_node", write_content)
    workflow.set_entry_point("writer_node")
    workflow.add_edge("writer_node", END)

    return workflow.compile()
