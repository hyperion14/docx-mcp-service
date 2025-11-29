#!/usr/bin/env python3
"""
Mistral Agent Setup Script
Creates and configures a Mistral Custom Agent for legal dictation and DOCX generation.
"""

import os
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DOCKER_API_KEY = os.getenv("DOCKER_API_KEY")
DOCKER_IP = os.getenv("DOCKER_IP", "http://localhost:5000")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in .env file")

# Initialize Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)

# System Prompt
SYSTEM_INSTRUCTIONS = f"""Du bist ein juristischer Assistent für Vergaberecht.

Aufgaben:
1. Empfange Audio (Diktat) oder Text vom Nutzer.
2. Wandle Audio in Text um (nutze die integrierte Audio-zu-Text-Funktion von Le Platform oder Mistral-API).
3. Bereinige den Text: Entferne Seitenzahlen, Kopfzeilen, Leerabsätze und Füllwörter.
4. Extrahiere Schlagwörter und Normverknüpfungen (z. B. § 97 GWB).
5. Lasse den Nutzer den Text überarbeiten und bestätigen.
6. Wenn der Nutzer die Dokumenterstellung anstößt (mit dem Kommando "/generate_docx" oder "Erstelle das Dokument"), rufe die Function generate_docx_document auf.
7. Empfange den Download-Link aus der Function-Response und gebe ihn dem Nutzer aus.

WICHTIG:
- Rufe die Function erst auf, wenn der Nutzer explizit die Dokumenterstellung bestätigt hat.
- Der Nutzer kann den Text vor der Generierung überarbeiten und korrigieren.
- Nach erfolgreicher Generierung erhältst du einen JSON mit "download_url" - zeige diesen Link dem Nutzer an.
- Sei präzise und professionell in deiner Kommunikation.
"""

# Function Definition for DOCX Generation
DOCX_GENERATION_FUNCTION = {
    "type": "function",
    "function": {
        "name": "generate_docx_document",
        "description": "Generiert ein DOCX-Dokument aus dem bereinigten Diktat-Text und gibt einen Download-Link zurück",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Der bereinigte und vom Nutzer bestätigte Diktat-Text"
                },
                "filename": {
                    "type": "string",
                    "description": "Optionaler Dateiname für das Dokument (ohne .docx-Endung). Standardwert: 'diktat_vergaberecht'"
                }
            },
            "required": ["text"]
        }
    }
}


def create_agent():
    """Create the Mistral Agent with DOCX generation capability."""

    print("Creating Mistral Agent for legal dictation...")
    print(f"Using Docker endpoint: {DOCKER_IP}")

    try:
        agent = client.beta.agents.create(
            model="mistral-large-latest",
            name="Juristischer Diktat-Assistent",
            description="Verarbeitet juristische Diktate zu Vergaberecht und generiert DOCX-Dokumente",
            instructions=SYSTEM_INSTRUCTIONS,
            tools=[DOCX_GENERATION_FUNCTION],
            completion_args={
                "temperature": 0.3,
                "top_p": 0.95,
                "max_tokens": 4096
            }
        )

        print(f"\n✅ Agent successfully created!")
        print(f"   Agent ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Version: {agent.version}")

        print(f"\n📝 Update your .env file with:")
        print(f"   MISTRAL_AGENT_ID={agent.id}")

        return agent

    except Exception as e:
        print(f"\n❌ Error creating agent: {e}")
        raise


def list_agents():
    """List all existing agents."""
    print("\nListing existing agents...")

    try:
        response = client.beta.agents.list()

        if hasattr(response, 'data') and response.data:
            print(f"\n📋 Found {len(response.data)} agent(s):")
            for agent in response.data:
                print(f"   - {agent.name} (ID: {agent.id})")
        else:
            print("\n   No agents found.")

    except Exception as e:
        print(f"\n❌ Error listing agents: {e}")


def get_agent(agent_id):
    """Retrieve agent details."""
    print(f"\nRetrieving agent {agent_id}...")

    try:
        agent = client.beta.agents.retrieve(agent_id=agent_id)

        print(f"\n✅ Agent details:")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Description: {agent.description}")
        print(f"   Tools: {len(agent.tools)} tool(s)")

        return agent

    except Exception as e:
        print(f"\n❌ Error retrieving agent: {e}")
        raise


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Mistral Agent Setup for Legal Dictation & DOCX Generation")
    print("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create":
            agent = create_agent()

        elif command == "list":
            list_agents()

        elif command == "get":
            if len(sys.argv) < 3:
                print("\n❌ Usage: python create_mistral_agent.py get <agent_id>")
                sys.exit(1)
            agent_id = sys.argv[2]
            get_agent(agent_id)

        else:
            print(f"\n❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python create_mistral_agent.py create  # Create new agent")
            print("  python create_mistral_agent.py list    # List all agents")
            print("  python create_mistral_agent.py get <agent_id>  # Get agent details")
            sys.exit(1)
    else:
        # Default: create agent
        agent = create_agent()
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Update .env with the Agent ID shown above")
        print("2. Run the conversation script to test the agent")
        print("=" * 60)
