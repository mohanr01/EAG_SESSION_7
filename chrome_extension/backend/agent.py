import asyncio
import time
import os
import datetime
from perception import extract_perception
from memory import MemoryManager, MemoryItem
from decision import generate_plan
from action import execute_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logger
 # use this to connect to running server

import shutil
import sys


max_steps = 3

async def main(user_input: str):
    try:
        logger.loggingInfo("[agent] Starting agent...")
        logger.loggingInfo(f"[agent] Current working directory: {os.getcwd()}")
        
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )

        try:
            async with stdio_client(server_params) as (read, write):
                logger.loggingInfo("Connection established, creating session...")
                try:
                    async with ClientSession(read, write) as session:
                        logger.loggingInfo("[agent] Session created, initializing...")
 
                        try:
                            await session.initialize()
                            logger.loggingInfo("[agent] MCP session initialized")

                            # Your reasoning, planning, perception etc. would go here
                            tools = await session.list_tools()
                            logger.loggingInfo(f"Available tools:{[t.name for t in tools.tools]}")

                            # Get available tools
                            logger.loggingInfo("Requesting tool list...")
                            tools_result = await session.list_tools()
                            tools = tools_result.tools
                            tool_descriptions = "\n".join(
                                f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                for tool in tools
                            )

                            logger.loggingInfo(f"[agent] {len(tools)} tools loaded")

                            memory = MemoryManager()
                            session_id = f"session-{int(time.time())}"
                            query = user_input  # Store original intent
                            step = 0

                            while step < max_steps:
                                logger.loggingInfo(f"[loop] Step {step + 1} started")

                                perception = extract_perception(user_input)
                                logger.loggingInfo(f"[perception] Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                                retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                                logger.loggingInfo(f"[memory] Retrieved {len(retrieved)} relevant memories")

                                plan = generate_plan(perception, retrieved, tool_descriptions=tool_descriptions)
                                logger.loggingInfo(f"[plan] Plan generated: {plan}")

                                if plan.startswith("FINAL_ANSWER:"):
                                    logger.loggingInfo(f"[agent] FINAL RESULT: {plan}")
                                    result = plan
                                    logger.loggingInfo(f"[agent] Agent session complete.")
                                    return result
                                try:
                                    result = await execute_tool(session, tools, plan)
                                    logger.loggingInfo(f"[tool] {result.tool_name} returned")

                                    memory.add(MemoryItem(
                                        text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                                        type="tool_output",
                                        tool_name=result.tool_name,
                                        user_query=user_input,
                                        tags=[result.tool_name],
                                        session_id=session_id
                                    ))

                                    user_input = f"Original task: {query}\nPrevious output: {result.result}\nWhat should I do next?"

                                except Exception as e:
                                    logger.loggingError(f" Tool execution failed: {e}")
                                    break

                                step += 1
                        except Exception as e:
                            logger.loggingInfo(f"[agent] Session initialization error: {e}")
                except Exception as e:
                    logger.loggingInfo(f"[agent] Session creation error: {str(e)}")
        except Exception as e:
            logger.loggingInfo(f"[agent] Connection error: {str(e)}")
    except Exception as e:
        logger.loggingInfo(f"[agent] Overall error: {str(e)}")

def search(query:str):
    logger.loggingInfo(f"search agent {query}")
    
    return asyncio.run(main(query))
    
