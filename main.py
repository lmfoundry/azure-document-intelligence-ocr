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

def get_document_intelligence_client(cosmos_config_container=None):
    """
    Get a Document Intelligence client instance.
    """
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    if not endpoint or not key:
        raise ValueError("Azure Document Intelligence credentials not found in environment variables")

    return DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

def get_ocr_results(file_path: str, cosmos_config_container=None):
    """
    Get OCR results with threading support and detailed logging.
    """
    thread_id = threading.current_thread().ident
    logger = logging.getLogger(__name__)

    logger.info(f"[Thread-{thread_id}] Starting Document Intelligence OCR for: {file_path}")

    # Create a new client instance for this request to ensure parallel processing
    client = get_document_intelligence_client(cosmos_config_container)

    with open(file_path, "rb") as f:
        logger.info(f"[Thread-{thread_id}] Submitting document to Document Intelligence API")
        poller = client.begin_analyze_document("prebuilt-layout", body=f)

    logger.info(f"[Thread-{thread_id}] Waiting for Document Intelligence results...")
    ocr_result = poller.result().content
    logger.info(f"[Thread-{thread_id}] Document Intelligence OCR completed, {len(ocr_result)} characters")

    return ocr_result

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

def test_ocr_functions():
    """
    Test function to demonstrate both OCR methods.
    """
    test_file = "TAMKEEN.jpg"

    if not os.path.exists(test_file):
        print(f"Error: Test file '{test_file}' not found. Please place your file in the current directory.")
        return

    print("="*60)
    print("Testing get_ocr_results function (with threading support)")
    print("="*60)

    try:
        # Test the new get_ocr_results function
        ocr_content = get_ocr_results(test_file)

        # Save OCR output
        ocr_output_file = f"{test_file.split('.')[0]}_ocr_output.txt"
        with open(ocr_output_file, "w", encoding="utf-8") as f:
            f.write(ocr_content)

        print(f"\nOCR Results saved to: {ocr_output_file}")
        print(f"Content length: {len(ocr_content)} characters")
        print("\n--- First 500 characters of OCR content ---")
        print(ocr_content[:500] + "..." if len(ocr_content) > 500 else ocr_content)

    except Exception as e:
        print(f"Error in get_ocr_results: {e}")

    print("\n" + "="*60)
    print("Testing parse_pdf_to_markdown function (original)")
    print("="*60)

    try:
        # Test the original markdown function
        markdown_content = parse_pdf_to_markdown(test_file)

        # Save markdown output
        markdown_output_file = f"{test_file.split('.')[0]}_markdown.md"
        save_markdown_output(markdown_content, markdown_output_file)

        print(f"Content length: {len(markdown_content)} characters")
        print("\n--- First 500 characters of Markdown content ---")
        print(markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content)

    except Exception as e:
        print(f"Error in parse_pdf_to_markdown: {e}")

def main():
    """
    Main function to test OCR functionality.
    """
    test_ocr_functions()

if __name__ == "__main__":
    main()
