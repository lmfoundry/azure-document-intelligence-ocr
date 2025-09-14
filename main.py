import os
import mimetypes
import threading
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_pdf_to_markdown(pdf_path: str) -> str:
    """
    Uses Azure Document Intelligence to parse PDF and return Markdown content.
    """
    # Get credentials from environment
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    if not endpoint or not key:
        raise ValueError("Azure Document Intelligence credentials not found in environment variables")

    # Initialize the client
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Read the PDF file
    with open(pdf_path, "rb") as f:
        content = f.read()

    # Determine MIME type
    mime_type = mimetypes.guess_type(pdf_path)[0] or "application/pdf"

    # Analyze the document
    poller = document_intelligence_client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=content,
        content_type=mime_type,
        output_content_format=DocumentContentFormat.MARKDOWN
    )

    result = poller.result()
    return result.content

def save_markdown_output(content: str, output_path: str) -> None:
    """
    Save the markdown content to a file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Markdown output saved to: {output_path}")

def main():
    # Example usage
    pdf_file = "TAMKEEN.jpg"  # Replace with your PDF file path
    output_file = "TAMKEEN.md"  # Output markdown file

    try:
        if not os.path.exists(pdf_file):
            print(f"Error: PDF file '{pdf_file}' not found. Please place your PDF file in the current directory or update the path.")
            return

        print(f"Processing PDF: {pdf_file}")
        markdown_content = parse_pdf_to_markdown(pdf_file)

        # Save to file
        save_markdown_output(markdown_content, output_file)

        # Also print first 500 characters as preview
        print("\n--- Preview of markdown content ---")
        print(markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content)

    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    main()
