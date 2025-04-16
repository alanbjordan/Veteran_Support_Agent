# server/services/chat_service.py

import os
import json
from openai import OpenAI
from datetime import datetime
import pytz
from helpers.token_utils import calculate_token_cost
from services.analytics_service import store_request_analytics

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# This is the model that we are using for the chat service
model="gpt-3.5-turbo"

"""
# Define the tools for the OpenAI API
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_cars",
            "description": (
                "Fetch car inventory details based on filter criteria. Users can provide filters "
                "such as make, model, model year range, price range, mileage, color, stock number, or VIN for a precise lookup. "
                "If a parameter is not applicable, please provide -1 for numeric values or an empty string for text values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "make": {
                        "type": "string",
                        "description": "Car manufacturer (e.g., Toyota, Ford)"
                    },
                    "model": {
                        "type": "string",
                        "description": "Car model (e.g., Camry, Mustang)"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Minimum car model year. Use -1 to indicate no minimum."
                    },
                    "max_year": {
                        "type": "integer",
                        "description": "Maximum car model year. Use -1 to indicate no maximum."
                    },
                    "price": {
                        "type": "number",
                        "description": "Minimum price. Use -1 to indicate no minimum."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price. Use -1 to indicate no maximum."
                    },
                    "mileage": {
                        "type": "integer",
                        "description": "Maximum mileage. Use -1 to indicate no maximum."
                    },
                    "color": {
                        "type": "string",
                        "description": "Car color. Use empty string to indicate no color filter."
                    },
                    "stock_number": {
                        "type": "string",
                        "description": "Exact stock number. Use empty string to indicate no stock number filter."
                    },
                    "vin": {
                        "type": "string",
                        "description": "Exact VIN. Use empty string to indicate no VIN filter."
                    }
                },
                "required": ["make", "model"]
            }
        }
    }
]
"""
def get_system_message():
    """Return the system message for the chat."""
    return {
        "role": "system",
        "content": (
            """ 
            You are a helpful assistant.
            """
        )
    }

def get_time_context_message():
    """Get the current time in EST and return a time context message."""
    try:
        # Get current time in EST using a reliable method
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        current_time_formatted = current_time.strftime('%Y-%m-%d %H:%M:%S EST')
    except Exception as e:
        # Fallback to a simpler approach
        from datetime import datetime, timedelta
        # EST is UTC-5
        utc_now = datetime.utcnow()
        est_offset = timedelta(hours=-5)
        est_time = utc_now + est_offset
        current_time_formatted = est_time.strftime('%Y-%m-%d %H:%M:%S EST')
    
    return {
        "role": "system",
        "content": f"Current time: {current_time_formatted}"
    }

def process_chat(user_message, conversation_history):
    """Process a chat message and return the response."""
    if not user_message:
        return {"error": "No 'message' provided"}, 400
    
    # Ensure conversation_history is a list
    if not isinstance(conversation_history, list):
        conversation_history = []
    
    # Check if the conversation history already has a system message
    has_system_message = any(msg.get("role") == "system" and "You are Patricia" in msg.get("content", "") for msg in conversation_history)
    
    # If no conversation history or no system message, add the system message
    if not conversation_history or not has_system_message:
        # Insert the system message at the beginning of the conversation history
        conversation_history.insert(0, get_system_message())
    
    # Check if there's a time context message in the conversation history
    has_time_context = any(msg.get("role") == "system" and "Current time:" in msg.get("content", "") for msg in conversation_history)
    
    # If no time context message, add one
    if not has_time_context:
        # Add time context message
        conversation_history.append(get_time_context_message())
    
    # Call ChatCompletion API using the new tools syntax
    completion = client.chat.completions.create(
        model=model,
        messages=conversation_history,
        #tools=tools,
        max_completion_tokens=750
    )
    
    message = completion.choices[0].message
    
    # Calculate token usage and cost
    token_usage = completion.usage
    cost_info = calculate_token_cost(
        prompt_tokens=token_usage.prompt_tokens,
        completion_tokens=token_usage.completion_tokens
    )
    
    # Store analytics data
    store_request_analytics(token_usage, cost_info)
    
    """
    # Check if a tool call was triggered
    tool_call_detected = False
    if message.tool_calls and len(message.tool_calls) > 0:
        tool_call_detected = True
        tool_call = message.tool_calls[0]
        func_name = tool_call.function.name
        args_str = tool_call.function.arguments
        
        try:
            func_args = json.loads(args_str)
        except Exception as parse_error:
            assistant_response = "Error parsing tool arguments."
        else:
            # For tool calls, we'll just return a placeholder response
            # The actual tool call processing will happen in the tool-call-result endpoint
            assistant_response = "Processing your request..."
    else:
        assistant_response = message.content or ""
    """
    assistant_response = message.content or ""
    # Append the assistant's response to the conversation history
    # Include the tool_calls property if it exists
    assistant_message = {
        "role": "assistant",
        "content": assistant_response
    }
    
    # If there are tool calls, include them in the message
    if message.tool_calls and len(message.tool_calls) > 0:
        # Convert tool_calls to a dictionary format that can be serialized
        tool_calls_dict = []
        for tool_call in message.tool_calls:
            tool_calls_dict.append({
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            })
        assistant_message["tool_calls"] = tool_calls_dict
    
    conversation_history.append(assistant_message)
        
    return {
        "chat_response": assistant_response,
        "conversation_history": conversation_history,
        #"tool_call_detected": tool_call_detected,
        #"summary": summary,
        "token_usage": {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens
        },
        "cost": cost_info
    }, 200

def process_tool_call(conversation_history):
    "Process a tool call and return the final response."
    if not isinstance(conversation_history, list):
        return {"error": "Invalid conversation history format"}, 400
    
    # Find the assistant message with tool calls
    tool_call_message = None
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            tool_call_message = msg
            break
    
    if not tool_call_message:
        return {"error": "No assistant message found in conversation history"}, 400
        
    # Check if the message has tool_calls
    if not tool_call_message.get("tool_calls"):
        # If the message doesn't have tool_calls, check if it's the "Processing your request..." message
        if tool_call_message.get("content") == "Processing your request...":
            # This is likely the message we're looking for, but it doesn't have tool_calls
            # We need to find the original message with tool_calls from the OpenAI response
            # For now, we'll just return an error
            print("DEBUG: Found 'Processing your request...' message without tool_calls")
            
            # As a fallback, we'll try to process a default fetch_cars call
            print("DEBUG: Using fallback mechanism to process fetch_cars with default parameters")
            
            result = fetch_cars({
                "make": "Nissan",
                "model": "",
                "year": -1,
                "max_year": -1,
                "price": -1,
                "max_price": -1,
                "mileage": -1,
                "color": "",
                "stock_number": "",
                "vin": ""
            })
            print("DEBUG: Fallback fetch_cars result:", result)
            
            # Add the result as a tool response message
            tool_response_message = {
                "role": "tool",
                "tool_call_id": "fallback_tool_call",
                "content": json.dumps(result)
            }
            conversation_history.append(tool_response_message)
            
            # Get the final response from the LLM
            print("DEBUG: Getting final response from LLM with fallback data")
            completion = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                max_completion_tokens=750
            )
            message = completion.choices[0].message
            final_response = message.content or ""
            print("DEBUG: Final response from LLM with fallback data:", final_response)
            
            # Calculate token usage and cost for the fallback response
            token_usage = completion.usage
            cost_info = calculate_token_cost(
                prompt_tokens=token_usage.prompt_tokens,
                completion_tokens=token_usage.completion_tokens
            )
            
            # Store analytics data
            store_request_analytics(token_usage, cost_info)
            
            # Append the final response to the conversation history
            conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
            
            # Check if the conversation has ended and generate a summary if needed
            summary = None
            if detect_end_of_conversation(conversation_history):
                print("DEBUG: End of conversation detected, generating summary")
                # Generate a conversation ID if not already present
                conversation_id = None
                for msg in conversation_history:
                    if msg.get("role") == "system" and "conversation_id" in msg.get("content", ""):
                        try:
                            conversation_id = json.loads(msg.get("content")).get("conversation_id")
                            break
                        except:
                            pass
                
                # Generate the summary
                summary = generate_conversation_summary(conversation_history, conversation_id)
            
            return {
                "final_response": final_response,
                "final_conversation_history": conversation_history,
                "summary": summary,
                "token_usage": {
                    "prompt_tokens": token_usage.prompt_tokens,
                    "completion_tokens": token_usage.completion_tokens,
                    "total_tokens": token_usage.total_tokens
                },
                "cost": cost_info
            }, 200
    
    # Process each tool call
    for tool_call in tool_call_message["tool_calls"]:
        func_name = tool_call["function"]["name"]
        args_str = tool_call["function"]["arguments"]
        tool_call_id = tool_call["id"]

        try:
            func_args = json.loads(args_str)
        except Exception as parse_error:
            return {"error": "Error parsing tool arguments"}, 400

        # Execute the appropriate function based on the tool name
        if func_name == "fetch_cars":
            result = fetch_cars(func_args)
        else:
            return {"error": f"Unknown tool '{func_name}' called"}, 400

        # Add the tool response message with the tool_call_id
        tool_response_message = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(result)
        }
        conversation_history.append(tool_response_message)

    # Get the final response from the LLM
    completion = client.chat.completions.create(
        model=model,
        messages=conversation_history,
        max_completion_tokens=750
    )
    message = completion.choices[0].message
    final_response = message.content or ""

    # Calculate token usage and cost for the final response
    token_usage = completion.usage
    cost_info = calculate_token_cost(
        prompt_tokens=token_usage.prompt_tokens,
        completion_tokens=token_usage.completion_tokens
    )
    
    # Store analytics data
    store_request_analytics(token_usage, cost_info)

    # Append the final response to the conversation history
    conversation_history.append({
        "role": "assistant",
        "content": final_response
    })
    
    # Check if the conversation has ended and generate a summary if needed
    summary = None
    if detect_end_of_conversation(conversation_history):
        # Generate a conversation ID if not already present
        conversation_id = None
        for msg in conversation_history:
            if msg.get("role") == "system" and "conversation_id" in msg.get("content", ""):
                try:
                    conversation_id = json.loads(msg.get("content")).get("conversation_id")
                    break
                except:
                    pass
        
        # Generate the summary
        summary = generate_conversation_summary(conversation_history, conversation_id)
    
    return {
        "final_response": final_response,
        "final_conversation_history": conversation_history,
        "summary": summary,
        "token_usage": {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens
        },
        "cost": cost_info
    }, 200