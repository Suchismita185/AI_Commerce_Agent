import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from .prompts import SYSTEM_PROMPT
from .tools import (
    search_products,
    get_product,
    add_to_cart,
    get_cart
)


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in .env"
    )


# --------------------------------------------------
# Groq client
# --------------------------------------------------

client = Groq(
    api_key=api_key
)


# --------------------------------------------------
# AI Tools
# --------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search the merchant product catalog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What product the customer is looking for."
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Get detailed information about a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The product ID."
                    }
                },
                "required": ["product_id"]
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a product to the customer's shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The product ID."
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of products to add."
                    }
                },
                "required": [
                    "product_id",
                    "quantity"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "Get the customer's current shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    }
]


# --------------------------------------------------
# Execute tools
# --------------------------------------------------

def execute_tool(
    name,
    arguments,
    customer_id
):

    if name == "search_products":

        return search_products(
            arguments["query"]
        )


    if name == "get_product":

        return get_product(
            arguments["product_id"]
        )


    if name == "add_to_cart":

        return add_to_cart(
            customer_id=customer_id,
            product_id=arguments["product_id"],
            quantity=arguments["quantity"]
        )


    if name == "get_cart":

        return get_cart(
            customer_id=customer_id
        )


    return {
        "error": f"Unknown tool: {name}"
    }


# --------------------------------------------------
# Run AI Agent
# --------------------------------------------------

def run_agent(
    user_message: str,
    customer_id: int
):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
    ]


    while True:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=messages,

            tools=TOOLS,

            tool_choice="auto"
        )


        assistant_message = response.choices[0].message


        # --------------------------------------------------
        # No tool required
        # --------------------------------------------------

        if not assistant_message.tool_calls:

            return assistant_message.content


        # --------------------------------------------------
        # Add assistant response to conversation
        # --------------------------------------------------

        messages.append(
            assistant_message
        )


        # --------------------------------------------------
        # Execute requested tools
        # --------------------------------------------------

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )


            print(
                f"AI TOOL CALL: {tool_name} -> {arguments}"
            )


            result = execute_tool(
                tool_name,
                arguments,
                customer_id
            )


            # --------------------------------------------------
            # Send tool result back to Groq
            # --------------------------------------------------

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call.id,

                "content": json.dumps(result)
            })