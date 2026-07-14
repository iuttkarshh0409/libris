import httpx
import time
import os

def run_validation():
    base_url = "http://localhost:8000"
    
    # 1. Health check
    print("--- 1. Verification: Health Check ---")
    res = httpx.get(f"{base_url}/health")
    print(f"Health status: {res.status_code}, response: {res.json()}")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}
    print("Health Check Pass!\n")
    
    # 2. Upload book
    print("--- 2. Verification: Ingesting 'computer_networks.pdf' ---")
    pdf_path = "computer_networks.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return
        
    with open(pdf_path, "rb") as f:
        files = {"file": ("computer_networks.pdf", f, "application/pdf")}
        res = httpx.post(f"{base_url}/api/v1/books", files=files, timeout=60.0)
        
    print(f"Upload status: {res.status_code}")
    assert res.status_code in [200, 201]
    upload_data = res.json()
    print(f"Upload response data: {upload_data}")
    assert upload_data["success"] is True
    book_id = upload_data["data"]["id"]
    print(f"Ingested Book ID: {book_id}")
    print("Ingestion Pass!\n")
    
    # 3. List books
    print("--- 3. Verification: Listing Ingested Books ---")
    res = httpx.get(f"{base_url}/api/v1/books")
    print(f"List books status: {res.status_code}")
    assert res.status_code == 200
    list_data = res.json()
    print(f"List books: {list_data}")
    assert list_data["success"] is True
    book_ids = [b["id"] for b in list_data["data"]]
    assert book_id in book_ids
    print("List Books Pass!\n")
    
    # 4. Submit query
    print("--- 4. Verification: Querying RAG Pipeline ---")
    query_payload = {
        "query_text": "What are the seven layers of the OSI model?"
    }
    res = httpx.post(f"{base_url}/api/v1/queries", json=query_payload, timeout=60.0)
    print(f"Query status: {res.status_code}")
    assert res.status_code in [200, 201]
    query_data = res.json()
    print(f"Query Response: {query_data}")
    assert query_data["success"] is True
    
    item = query_data["data"]["items"][0]
    answer_text = item["answer_text"]
    citations = item["supporting_citations"]
    excerpts = item["supporting_excerpts"]
    
    print("\n=== Generated Answer ===")
    print(answer_text)
    print("========================\n")
    
    print("=== Supporting Citations ===")
    for cit in citations:
        print(f"- Page {cit.get('page_number')}: Rank {cit.get('retrieval_rank')}, Score: {cit.get('similarity_score')}")
    print("============================\n")
    
    assert len(citations) > 0
    assert "OSI model" in answer_text or "seven layers" in answer_text
    print("Query Retrieval & Grounded Generation Pass!\n")
    
    # 5. System Status
    print("--- 5. Verification: Checking System Status ---")
    res = httpx.get(f"{base_url}/api/v1/status")
    print(f"Status response: {res.json()}")
    assert res.status_code == 200
    print("System Status Pass!\n")
    
    print("ALL END-TO-END INTEGRATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_validation()
