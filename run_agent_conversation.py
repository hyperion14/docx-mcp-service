#!/usr/bin/env python3
"""
Mistral Agent Conversation Script
Implements the function calling logic to connect the agent with the DOCX generator service.
"""

import os
import json
import requests
from mistralai import Mistral
from mistralai.models import FunctionResultEntry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_AGENT_ID = os.getenv("MISTRAL_AGENT_ID")
DOCKER_API_KEY = os.getenv("DOCKER_API_KEY")
DOCKER_IP = os.getenv("DOCKER_IP", "http://localhost:5000")

if not all([MISTRAL_API_KEY, MISTRAL_AGENT_ID, DOCKER_API_KEY]):
    raise ValueError("Missing required environment variables. Check .env file.")

# Initialize Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)


def generate_docx_document(text: str, filename: str = "diktat_vergaberecht") -> dict:
    """
    Call the DOCX generator service to create a document.

    Args:
        text: The cleaned and confirmed dictation text
        filename: Optional filename (without .docx extension)

    Returns:
        dict: Response from the DOCX generator service
    """
    url = f"{DOCKER_IP}/generate_docx"

    headers = {
        "Authorization": f"Bearer {DOCKER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "filename": filename
    }

    print(f"\n🔧 Calling DOCX Generator API...")
    print(f"   Endpoint: {url}")
    print(f"   Filename: {filename}.docx")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        print(f"\n✅ DOCX generated successfully!")
        print(f"   Download URL: {result.get('download_url')}")

        return result

    except requests.exceptions.RequestException as e:
        error_msg = f"Error calling DOCX generator: {str(e)}"
        print(f"\n❌ {error_msg}")

        return {
            "error": error_msg,
            "status": "failed"
        }


# Function mapping
FUNCTION_MAPPING = {
    "generate_docx_document": generate_docx_document
}


def run_conversation(user_message: str):
    """
    Run a conversation with the Mistral agent.

    Args:
        user_message: The user's input message
    """
    print("\n" + "=" * 60)
    print("Starting conversation with Mistral Agent")
    print("=" * 60)
    print(f"\n👤 User: {user_message}")

    # Start conversation
    response = client.beta.conversations.start(
        agent_id=MISTRAL_AGENT_ID,
        inputs=user_message
    )

    print(f"\n💬 Conversation ID: {response.conversation_id}")

    # Process outputs
    for output in response.outputs:
        if output.type == "message":
            print(f"\n🤖 Agent: {output.content}")

        elif output.type == "function.call":
            print(f"\n🔧 Function call: {output.name}")
            print(f"   Arguments: {output.arguments}")

            # Parse arguments
            try:
                args = json.loads(output.arguments)
            except json.JSONDecodeError:
                args = {}

            # Execute function
            function_name = output.name
            if function_name in FUNCTION_MAPPING:
                result = FUNCTION_MAPPING[function_name](**args)

                # Send result back to agent
                print(f"\n📤 Sending function result back to agent...")

                function_result = FunctionResultEntry(
                    tool_call_id=output.tool_call_id,
                    result=json.dumps(result)
                )

                # Append to conversation
                response = client.beta.conversations.append(
                    conversation_id=response.conversation_id,
                    inputs=[function_result]
                )

                # Process final response
                for final_output in response.outputs:
                    if final_output.type == "message":
                        print(f"\n🤖 Agent: {final_output.content}")
            else:
                print(f"\n❌ Unknown function: {function_name}")

    print("\n" + "=" * 60)
    return response


def interactive_mode():
    """
    Run the agent in interactive mode.
    """
    print("\n" + "=" * 60)
    print("Interactive Mode - Legal Dictation Assistant")
    print("=" * 60)
    print("\nType 'quit' to exit")
    print("Type '/generate_docx' to trigger document generation")
    print("\n" + "=" * 60)

    conversation_id = None

    while True:
        user_input = input("\n👤 You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        try:
            if conversation_id:
                # Continue existing conversation
                response = client.beta.conversations.append(
                    conversation_id=conversation_id,
                    inputs=user_input
                )
            else:
                # Start new conversation
                response = client.beta.conversations.start(
                    agent_id=MISTRAL_AGENT_ID,
                    inputs=user_input
                )
                conversation_id = response.conversation_id

            # Process outputs
            for output in response.outputs:
                if output.type == "message":
                    print(f"\n🤖 Agent: {output.content}")

                elif output.type == "function.call":
                    print(f"\n🔧 Calling function: {output.name}...")

                    # Parse and execute
                    args = json.loads(output.arguments)
                    function_name = output.name

                    if function_name in FUNCTION_MAPPING:
                        result = FUNCTION_MAPPING[function_name](**args)

                        # Send result back
                        function_result = FunctionResultEntry(
                            tool_call_id=output.tool_call_id,
                            result=json.dumps(result)
                        )

                        response = client.beta.conversations.append(
                            conversation_id=conversation_id,
                            inputs=[function_result]
                        )

                        # Show final response
                        for final_output in response.outputs:
                            if final_output.type == "message":
                                print(f"\n🤖 Agent: {final_output.content}")
                    else:
                        print(f"\n❌ Unknown function: {function_name}")

        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # Interactive mode
        interactive_mode()
    else:
        # Single conversation example
        test_message = """
        Ich möchte ein Diktat erstellen.

        Betreff: Vergaberechtliches Gutachten

        Die Auftraggeberin hat eine öffentliche Ausschreibung nach § 97 GWB durchgeführt.
        Der Bieter rügt die Vergabe wegen Verstoßes gegen § 97 Abs. 1 GWB.

        Bitte bereite diesen Text auf und erstelle ein Dokument.
        """

        run_conversation(test_message)

        print("\n💡 Tip: Run in interactive mode with:")
        print("   python run_agent_conversation.py interactive")
